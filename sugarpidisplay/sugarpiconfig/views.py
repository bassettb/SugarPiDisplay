"""
Routes and views for the flask application.
"""
import json
import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.validators import InputRequired, ValidationError
from ..config_utils import Cfg, read_config
from . import app

source_dexcom = 'dexcom'
source_nightscout = 'nightscout'
unit_mmolperL = 'mmolperL'
unit_mgperdL = 'mgperdL'

LOG_FILENAME = "sugarpidisplay.log"
folder_name = '.sugarpidisplay'
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
    time24hour = BooleanField('24hour time')
    unit = SelectField(
        'Unit',
        choices=[(unit_mgperdL, 'mg/dL'), (unit_mmolperL, 'mmol/L')]
    )
    orientation = SelectField('Screen Orientation (location of power cord)', coerce=int,
        choices=[(0, '0° (left)'), (90, '90° (top)'), (180, '180° (right)'), (270, '270° (bottom)')])

    show_graph = BooleanField('Show Graph')

    dexcom_user = StringField(
        'Dexcom UserName', validators=[dexcom_field_check])
    dexcom_pass = PasswordField(
        'Dexcom Password', validators=[dexcom_field_check])
    outside_us = BooleanField('Outside US')
    ns_url = StringField(
        'Nightscout URL', validators=[nightscout_field_check])
    ns_token = StringField(
        'Nightscout Access Token', validators=[nightscout_field_check])


@app.route('/hello')
def hello_world():
    return 'Hello, World!'


@app.route('/success')
def success():
    return 'Your device is configured.  Now cycle the power to use the new settings'


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
    config = {Cfg.data_source: form.data_source.data}
    config[Cfg.time_24hour] = form.time24hour.data
    config[Cfg.orientation] = form.orientation.data
    config[Cfg.show_graph] = form.show_graph.data
    if (form.data_source.data == source_dexcom):
        config[Cfg.dex_user] = form.dexcom_user.data
        config[Cfg.dex_pass] = form.dexcom_pass.data
        config[Cfg.outside_us] = form.outside_us.data
    else:
        config[Cfg.ns_url] = form.ns_url.data
        config[Cfg.ns_token] = form.ns_token.data

    config[Cfg.unit_mmol] = form.unit.data == unit_mmolperL

    #__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(pi_sugar_path, config_file), "w")
    json.dump(config, f, indent=4)
    f.close()


def loadData(form):
    config_full_path = os.path.join(pi_sugar_path, config_file)
    config = {}
    try:
        read_config(config, config_full_path, None)

        if (Cfg.data_source in config):
            form.data_source.data = config[Cfg.data_source]
            if (config[Cfg.data_source] == source_dexcom):
                if (Cfg.dex_user in config):
                    form.dexcom_user.data = config[Cfg.dex_user]
                if (Cfg.dex_pass in config):
                    form.dexcom_pass.data = config[Cfg.dex_pass]
                if (Cfg.outside_us in config):
                    form.outside_us.data = config[Cfg.outside_us]
            if (config[Cfg.data_source] == source_nightscout):
                if (Cfg.ns_url in config):
                    form.ns_url.data = config[Cfg.ns_url]
                if (Cfg.ns_token in config):
                    form.ns_token.data = config[Cfg.ns_token]
        form.time24hour.data = config[Cfg.time_24hour]
        form.orientation.data = config[Cfg.orientation]
        form.show_graph.data = config[Cfg.show_graph]
        form.unit.data = unit_mgperdL
        if config[Cfg.unit_mmol]:
            form.unit.data = unit_mmolperL
    except:
        pass
