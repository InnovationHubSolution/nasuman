
from flask import render_template, redirect, request, url_for,flash
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from . import admin_blueprint

from apps.admin import admin_blueprint

@admin_blueprint.route('/login', methods=['GET', 'POST'])
def login():

    return render_template('admin/login.html')