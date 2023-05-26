import unittest
from app import app

class FlaskTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        #self.app_context = app.app_context()
        #self.app_context.push()
        
        # Login
        response = self.app.post('/login', data=dict(
            username='user17',
            password='pass'
        ), follow_redirects=True)

        self.assertIn(b'Account Details of user17', response.data)

    # executed after each test
    def tearDown(self):
        pass


    def test_home_status_code(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 302)
    
    
    def test_login_status_code(self):
        result = self.app.get('/login')
        self.assertEqual(result.status_code, 302)
    

    def test_correct_login(self):
        tester = app.test_client(self)
        with self.app.session_transaction() as session:
            session['logged_in'] = True
        response = tester.post(
            '/login',
            data=dict(username='user16', password='pass'),
            follow_redirects=True
        )
        self.assertIn(b'Account Details of user16', response.data)
    
    def test_wrong_password(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(username='user17', password='pass123'),
            follow_redirects=True
        )
        self.assertIn(b'Wrong password', response.data)
    
    def test_wrong_username(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(username='user173', password='pass'),
            follow_redirects=True
        )
        self.assertIn(b'Invalid username user173', response.data)
    
    def test_transfer(self):
        response = self.app.get('/transfer')
        self.assertIn(b'No Beneficiary Found for user17', response.data)
    
    def test_recent_transcations(self):
        response = self.app.get('/recent-transactions')
        self.assertIn(b'Recent Transcations of user17', response.data)
    
    
    def test_cards(self):
        response = self.app.get('/cards')
        self.assertIn(b'username17', response.data)
   
    
if __name__ == '__main__':
    unittest.main()


