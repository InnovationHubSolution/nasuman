# -*- encoding: utf-8 -*-

from flask import Blueprint

admin_blueprint = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin'
)

from . import routes  # Import the routes module to register its routes

