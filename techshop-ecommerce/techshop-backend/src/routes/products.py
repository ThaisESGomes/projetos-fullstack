from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.product import Product, ProductReview, CartItem, Order, OrderItem
from functools import wraps
import jwt

products_bp = Blueprint('products', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            user_id = User.verify_token(token, 'asdf#FGSgvasgf$5$WGT')
            if user_id is None:
                return jsonify({'message': 'Token is invalid'}), 401
            current_user = User.query.get(user_id)
            if not current_user:
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

# Rotas públicas para produtos
@products_bp.route('/products', methods=['GET'])
def get_products():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        query = Product.query.filter_by(is_active=True)
        
        if category:
            query = query.filter(Product.category == category)
        
        if search:
            query = query.filter(Product.name.contains(search) | Product.description.contains(search))
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching products: {str(e)}'}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        if not product.is_active:
            return jsonify({'message': 'Product not found'}), 404
        
        product_data = product.to_dict()
        product_data['reviews'] = [review.to_dict() for review in product.reviews]
        
        return jsonify(product_data), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching product: {str(e)}'}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = db.session.query(Product.category).filter_by(is_active=True).distinct().all()
        category_list = [category[0] for category in categories]
        return jsonify({'categories': category_list}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching categories: {str(e)}'}), 500

# Rotas protegidas para carrinho
@products_bp.route('/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_data = [item.to_dict() for item in cart_items]
        total = sum(item['subtotal'] for item in cart_data)
        
        return jsonify({
            'cart_items': cart_data,
            'total': total,
            'item_count': len(cart_items)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching cart: {str(e)}'}), 500

@products_bp.route('/cart', methods=['POST'])
@token_required
def add_to_cart(current_user):
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({'message': 'Product ID is required'}), 400
        
        product = Product.query.get_or_404(product_id)
        if not product.is_active:
            return jsonify({'message': 'Product not available'}), 400
        
        if product.stock_quantity < quantity:
            return jsonify({'message': 'Insufficient stock'}), 400
        
        # Verificar se o item já está no carrinho
        existing_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            if existing_item.quantity > product.stock_quantity:
                return jsonify({'message': 'Insufficient stock'}), 400
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify({'message': 'Product added to cart successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding to cart: {str(e)}'}), 500

@products_bp.route('/cart/<int:item_id>', methods=['PUT'])
@token_required
def update_cart_item(current_user, item_id):
    try:
        data = request.get_json()
        quantity = data.get('quantity')
        
        if quantity is None or quantity < 1:
            return jsonify({'message': 'Valid quantity is required'}), 400
        
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=current_user.id
        ).first_or_404()
        
        if cart_item.product.stock_quantity < quantity:
            return jsonify({'message': 'Insufficient stock'}), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        
        return jsonify({'message': 'Cart item updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating cart item: {str(e)}'}), 500

@products_bp.route('/cart/<int:item_id>', methods=['DELETE'])
@token_required
def remove_from_cart(current_user, item_id):
    try:
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=current_user.id
        ).first_or_404()
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Item removed from cart successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error removing item from cart: {str(e)}'}), 500

# Rotas para pedidos
@products_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    try:
        data = request.get_json()
        shipping_address = data.get('shipping_address')
        payment_method = data.get('payment_method')
        
        if not shipping_address or not payment_method:
            return jsonify({'message': 'Shipping address and payment method are required'}), 400
        
        # Buscar itens do carrinho
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400
        
        # Calcular total
        total_amount = 0
        order_items_data = []
        
        for cart_item in cart_items:
            if cart_item.product.stock_quantity < cart_item.quantity:
                return jsonify({'message': f'Insufficient stock for {cart_item.product.name}'}), 400
            
            subtotal = cart_item.product.price * cart_item.quantity
            total_amount += subtotal
            
            order_items_data.append({
                'product_id': cart_item.product_id,
                'quantity': cart_item.quantity,
                'price_at_time': cart_item.product.price
            })
        
        # Criar pedido
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            payment_method=payment_method
        )
        db.session.add(order)
        db.session.flush()  # Para obter o ID do pedido
        
        # Criar itens do pedido e atualizar estoque
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price_at_time=item_data['price_at_time']
            )
            db.session.add(order_item)
            
            # Atualizar estoque
            product = Product.query.get(item_data['product_id'])
            product.stock_quantity -= item_data['quantity']
        
        # Limpar carrinho
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': order.id,
            'total_amount': total_amount
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating order: {str(e)}'}), 500

@products_bp.route('/orders', methods=['GET'])
@token_required
def get_user_orders(current_user):
    try:
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching orders: {str(e)}'}), 500

# Rotas administrativas
@products_bp.route('/admin/products', methods=['POST'])
@token_required
@admin_required
def create_product(current_user):
    try:
        data = request.get_json()
        
        required_fields = ['name', 'price', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'{field} is required'}), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            category=data['category'],
            brand=data.get('brand'),
            stock_quantity=data.get('stock_quantity', 0),
            image_url=data.get('image_url')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating product: {str(e)}'}), 500

@products_bp.route('/admin/orders', methods=['GET'])
@token_required
@admin_required
def get_all_orders(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        orders = Order.query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching orders: {str(e)}'}), 500

