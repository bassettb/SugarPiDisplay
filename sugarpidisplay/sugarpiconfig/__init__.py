from flask import Flask

from .views import *

app = Flask(__name__)
app.secret_key = 'my secret key 123'
