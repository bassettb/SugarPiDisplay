"""
The flask application package.
"""

from flask import Flask
web_app = Flask(__name__)
web_app.secret_key = 'my secret key 123'

import sugarpiconfig.views
