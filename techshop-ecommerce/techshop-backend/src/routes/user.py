from flask import current_app, Blueprint, request, jsonify
from src.models.user import db, User
from src.models.product import Product, ProductReview
from functools import wraps
import jwt

user_bp = Blueprint('user', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            user_id = User.verify_token(token, current_app.config['SECRET_KEY'])
            if user_id is None:
                return jsonify({'message': 'Token is invalid'}), 401
            current_user = User.query.get(user_id)
            if not current_user or not current_user.is_active:
                return jsonify({'message': 'User not found'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'message': 'JSON object required'}), 400
        
        # Validar campos obrigatórios
        required_fields = ['name', 'username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # Criar novo usuário
        user = User(
            name=data['name'],
            username=data['username'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Gerar token
        token = user.generate_token(current_app.config['SECRET_KEY'])
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'message': 'JSON object required'}), 400
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400
        
        # Buscar usuário por username ou email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        # Gerar token
        token = user.generate_token(current_app.config['SECRET_KEY'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        return jsonify({
            'user': current_user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching profile: {str(e)}'}), 500

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'message': 'JSON object required'}), 400
        
        # Campos que podem ser atualizados
        updatable_fields = ['name', 'email', 'phone', 'address']
        
        for field in updatable_fields:
            if field in data:
                if field == 'email':
                    # Verificar se email já existe para outro usuário
                    existing_user = User.query.filter_by(email=data['email']).first()
                    if existing_user and existing_user.id != current_user.id:
                        return jsonify({'message': 'Email already exists'}), 400
                
                setattr(current_user, field, data[field])
        
        # Atualizar senha se fornecida
        if 'password' in data and data['password']:
            current_user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating profile: {str(e)}'}), 500

@user_bp.route('/reviews', methods=['POST'])
@token_required
def create_review(current_user):
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'message': 'JSON object required'}), 400
        
        product_id = data.get('product_id')
        rating = data.get('rating')
        comment = data.get('comment')
        
        if not product_id or not rating:
            return jsonify({'message': 'Product ID and rating are required'}), 400
        
        if rating < 1 or rating > 5:
            return jsonify({'message': 'Rating must be between 1 and 5'}), 400
        
        # Verificar se o produto existe
        product = Product.query.get_or_404(product_id)
        
        # Verificar se o usuário já avaliou este produto
        existing_review = ProductReview.query.filter_by(
            product_id=product_id,
            user_id=current_user.id
        ).first()
        
        if existing_review:
            return jsonify({'message': 'You have already reviewed this product'}), 400
        
        # Criar nova avaliação
        review = ProductReview(
            product_id=product_id,
            user_id=current_user.id,
            rating=rating,
            comment=comment
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review created successfully',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating review: {str(e)}'}), 500

@user_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching users: {str(e)}'}), 500

@user_bp.route('/users', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'message': 'JSON object required'}), 400
        
        if not data.get('username') or not data.get('email'):
            return jsonify({'message': 'Username and email are required'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        user = User(
            name=data.get('name', data['username']),
            username=data['username'],
            email=data['email']
        )
        
        if data.get('password'):
            user.set_password(data['password'])
        else:
            return jsonify({'message': 'Password is required'}), 400
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching user: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'message': 'JSON object required'}), 400
        
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.name = data.get('name', user.name)
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating user: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting user: {str(e)}'}), 500

