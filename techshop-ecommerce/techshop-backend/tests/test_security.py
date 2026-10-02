import os
import sys
import unittest
from pathlib import Path
os.environ['SECRET_KEY'] = 'a' * 64
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.main import app
from src.models.user import db, User

class AccessTests(unittest.TestCase):
    def setUp(self):
        self.context = app.app_context()
        self.context.push()
        db.drop_all()
        db.create_all()
        self.tokens = {}
        for username, admin, active in [('ordinary', False, True), ('admin', True, True), ('disabled', True, False)]:
            user = User(name=username, username=username, email=username+'@example.test', is_admin=admin, is_active=active)
            user.set_password('test-password-only')
            db.session.add(user)
            db.session.flush()
            self.tokens[username] = user.generate_token(app.config['SECRET_KEY'])
            self.target_id = user.id if username == 'ordinary' else self.target_id
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_anonymous_and_nonadmin_cannot_manage_users(self):
        for method, path in [('get', '/api/users'), ('post', '/api/users'), ('get', f'/api/users/{self.target_id}'), ('put', f'/api/users/{self.target_id}'), ('delete', f'/api/users/{self.target_id}')]:
            self.assertEqual(getattr(self.client, method)(path).status_code, 401)
            self.assertEqual(getattr(self.client, method)(path, headers={'Authorization': 'Bearer '+self.tokens['ordinary']}).status_code, 403)
        self.assertEqual(db.session.get(User, self.target_id).username, 'ordinary')

    def test_admin_can_list_users(self):
        self.assertEqual(self.client.get('/api/users', headers={'Authorization':'Bearer '+self.tokens['admin']}).status_code, 200)

    def test_disabled_and_forged_tokens_rejected(self):
        self.assertEqual(self.client.get('/api/users', headers={'Authorization':'Bearer '+self.tokens['disabled']}).status_code, 401)
        forged = db.session.get(User, self.target_id).generate_token('b'*64)
        self.assertEqual(self.client.get('/api/profile', headers={'Authorization':'Bearer '+forged}).status_code, 401)

    def test_admin_creation_requires_password(self):
        response = self.client.post('/api/users', json={'username':'new','email':'new@example.test'}, headers={'Authorization':'Bearer '+self.tokens['admin']})
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(User.query.filter_by(username='new').first())

    def test_invalid_cart_quantity_rejected_before_database_change(self):
        for quantity in [0, -1, True, '2', 1.5]:
            response = self.client.post('/api/cart', json={'product_id':1,'quantity':quantity}, headers={'Authorization':'Bearer '+self.tokens['ordinary']})
            self.assertEqual(response.status_code, 400)
