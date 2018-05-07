"""
Routes and views for the flask application.
"""
import os
import json
from datetime import datetime
from flask import Flask, redirect, request, render_template, flash
from . import app
from flask_wtf import FlaskForm
from wtforms import StringField,SelectField,PasswordField,BooleanField
from wtforms.validators import InputRequired,ValidationError
from pathlib import Path

source_dexcom = 'dexcom'
source_nightscout = 'nightscout'

LOG_FILENAME="pi-sugar.log"
folder_name = '.pi-sugar'
config_file = 'config.json'
pi_sugar_path = os.path.join(str(Path.home()), folder_name)
Path(pi_sugar_path).mkdir(exist_ok=True) 

def dexcom_field_check(form, field):
    if (form.data_source.data == source_dexcom):
        if (not field.data):
            raise ValidationError('Field cannot be empty')

def nightscout_field_check(form, field):
    if (form.data_source.data == source_nightscout):
        if (not field.data):
            raise ValidationError('Field cannot be empty')


class MyForm(FlaskForm):
    class Meta:
        csrf = False
    data_source = SelectField(
        'Data Source',
        choices=[(source_dexcom, 'Dexcom'), (source_nightscout, 'Nightscout')]
    )
    use_animation = BooleanField('Use Animation')
    dexcom_user = StringField('Dexcom UserName', validators=[dexcom_field_check])
    dexcom_pass = PasswordField('Dexcom Password', validators=[dexcom_field_check])
    ns_url = StringField('Nightscout URL', validators=[nightscout_field_check])
    ns_token = StringField('Nightscout Access Token', validators=[nightscout_field_check])


@app.route('/hello')
def hello_world():
    return 'Hello, World!'

@app.route('/success')
def success():
    return 'Your device is configured.  Now cycle the power and it will use the new settings'

@app.route('/', methods=('GET', 'POST'))
def setup():
    form = MyForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('Fields are missing.')
            return render_template('setup.html', form=form)
        else:
            handle_submit(form)
            return redirect('/success')
    #if form.is_submitted():
    loadData(form)
    return render_template('setup.html', form=form)

def handle_submit(form):
    config = { 'data_source': form.data_source.data }
    config['use_animation'] = form.use_animation.data
    if (form.data_source.data == source_dexcom):
        config['dexcom_username'] = form.dexcom_user.data
        config['dexcom_password'] = form.dexcom_pass.data
    else:
        config['nightscout_url'] = form.ns_url.data
        config['nightscout_account_token'] = form.ns_token.data

    #__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(pi_sugar_path, config_file), "w")
    json.dump(config, f, indent = 4)
    f.close()

def loadData(form):
    config_full_path = os.path.join(pi_sugar_path, config_file)
    if (not Path(config_full_path).exists()):
        return
    try:
        f = open(config_full_path, "r")
        config = json.load(f)
        f.close()
        if ('data_source' in config):
            form.data_source.data = config['data_source']
            if (config['data_source'] == source_dexcom):
                if ('dexcom_username' in config):
                    form.dexcom_user.data = config['dexcom_username']
                if ('dexcom_password' in config):
                    form.dexcom_pass.data = config['dexcom_password']
            if (config['data_source'] == source_nightscout):
                if ('nightscout_url' in config):
                    form.ns_url.data = config['nightscout_url'] 
                if ('nightscout_account_token' in config):
                    form.ns_token.data = config['nightscout_account_token']
        form.use_animation.data = config['use_animation']
    except:
        pass

