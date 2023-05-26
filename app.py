from flask import Flask, render_template
from flask_session import  Session
import logging
from controllers.fund_transfer_controller import transfer_ctrl
from dotenv import  load_dotenv
import os
import secrets
import redis


load_dotenv()
secret_key = os.getenv("SESSION_SECRET")
redis_connection_string = os.getenv("REDIS_CON")

logging.basicConfig(filename='app.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


app = Flask(__name__)
app._static_folder = 'static'
app.config["DEBUG"] = True
app.secret_key = secret_key
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(redis_connection_string)
Session(app)

    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page-404.html'), 404

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

app.register_blueprint(transfer_ctrl)


if __name__ == '__main__':
 app.run()