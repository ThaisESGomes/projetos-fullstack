import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
os.environ['SECRET_KEY'] = 'a'*64
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.main import app

class AccessTests(unittest.TestCase):
    def test_missing_token_configuration_is_closed(self):
        with patch.dict(os.environ, {'ADMIN_API_TOKEN':''}):
            self.assertEqual(app.test_client().get('/api/users').status_code, 503)

    def test_authentication_required_for_every_crud_operation(self):
        with patch.dict(os.environ, {'ADMIN_API_TOKEN':'x'*64}):
            client = app.test_client()
            for method, path in [('get','/api/users'),('post','/api/users'),('put','/api/users/1'),('delete','/api/users/1')]:
                self.assertEqual(getattr(client,method)(path).status_code, 401)
            self.assertEqual(client.get('/api/users', headers={'Authorization':'Bearer '+'x'*64}).status_code, 200)
