
from flask import Flask
app = Flask(__name__)
app.secret_key = 'my secret key 123'

from .views import *
