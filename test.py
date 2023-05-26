import unittest
from app import app
from flask import Flask, session
from models.model_auth import Userotp
from flask.testing import FlaskClient


class FlaskTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
    
    def test_login_with_2fa(self):
        with self.client as c:
            # Perform the login request with valid username and password
            login_response = c.post('/login', data={'username': 'user17', 'password': 'pass'})

            # Assert that the login response is successful (e.g., 200 OK)
            self.assertEqual(login_response.status_code, 302)

            #print("login_response is: ", login_response.data)

            # Assert that the user is redirected to the 2FA step
            self.assertTrue(login_response.location.endswith('/two-factor-authentication'))

          
            # Perform the 2FA request with a valid OTP
            otp_data_found = Userotp.find_otp('user17')
            otp_in = otp_data_found['otp']
            two_fa_response = c.post('/api/v1/verify/two-factor-authentication', data={'otp': otp_in})

            #print("two_fa_response: ", two_fa_response.data)

            # Extract the session data for future requests
            session_data = dict(session)

            # Assert that the 2FA response is successful (e.g., 200 OK)
            self.assertEqual(two_fa_response.status_code, 302)


            # Assert that the user is authenticated
            with c.session_transaction() as sess:
                print("Session is :", sess)
                self.assertTrue(sess.get('name'))

            self.__class__.saved_session = session_data
            #self.saved_session = session_data
    
    def test_transfer_with_authenticated_user(self):
        with self.client as c:
            # Restore the saved session
            with c.session_transaction() as sess:
                sess.clear()
                sess.update(self.__class__.saved_session)

            # Perform the transfer request
            transfer_response = c.get('/transfer')

            # Assert that the transfer response is successful (e.g., 200 OK)
            self.assertEqual(transfer_response.status_code, 200)

            #
            #print("Transfer page is: ", transfer_response.data)

            self.assertIn(b'No Beneficiary Found for user17', transfer_response.data)
    
   
    
    
    def test_recent_transactions_with_authenticated_user(self):
        with self.client as c:
            # Restore the saved session
            with c.session_transaction() as sess:
                sess.clear()
                sess.update(self.__class__.saved_session)
            
            # Perform the transfer request
            transactions_response = c.get('/recent-transactions')

            # Assert that the transfer response is successful (e.g., 200 OK)
            self.assertEqual(transactions_response.status_code, 200)

            #
            #print("Transfer page is: ", transactions_response.data)

            self.assertIn(b'Recent Transcations of user17', transactions_response.data)

    def test_with_cards_authenticated_user(self):
        with self.client as c:
            # Restore the saved session
            with c.session_transaction() as sess:
                sess.clear()
                sess.update(self.__class__.saved_session)

            # Perform the transfer request
            transactions_response = c.get('/cards')

            # Assert that the transfer response is successful (e.g., 200 OK)
            self.assertEqual(transactions_response.status_code, 200)

            #
            #print("Transfer page is: ", transactions_response.data)

            self.assertIn(b'username17', transactions_response.data) 
 

if __name__ == '__main__':
    unittest.main()