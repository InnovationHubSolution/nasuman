# -*- encoding: utf-8 -*-

from flask import render_template, redirect, request, url_for,flash
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from flask_dance.contrib.github import github

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users,Group
from werkzeug.security import generate_password_hash,check_password_hash
from flask_mail import Message
from flask import current_app
from datetime import datetime, timedelta

import logging



@blueprint.route('/')
def route_default():
    return render_template("accounts/index.html")
    # return redirect(url_for('authentication_blueprint.login'))

# @blueprint.route('/')
# @blueprint.route("/home")
# def dashboard():
#     return render_template("index.html")

# Login & Registration

# @blueprint.route("/github")
# def login_github():
#     """ Github login """
#     if not github.authorized:
#         return redirect(url_for("github.login"))

#     res = github.get("/user")
#     return redirect(url_for('home_blueprint.index'))

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()

        if user:
            if user.group and user.group.confirmed:
                if check_password_hash(user.password, password):
                    login_user(user)
                    return redirect(url_for('home_blueprint.index'))
                else:
                    flash('Incorrect details. Please try again.', 'danger')
            else:
                if user.group:
                    flash('Group is not activated.', 'warning')
                else:
                    flash('Your account is not associated with any group.', 'warning')
        else:
            flash('Please check your login and try again.', 'danger')

    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))

    return render_template('accounts/login.html', form=login_form)




@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if request.method == 'POST' and create_account_form.validate():
        username = create_account_form.username.data
        email = create_account_form.email.data
        password = create_account_form.password.data
        group_name = create_account_form.group.data
        full_name = create_account_form.full_name.data
        phone = create_account_form.phone.data

        # Check if username exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check if email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create the group
        new_group = Group(full_name=full_name, group_name=group_name)

        # Generate confirmation token and set expiration
        new_group.generate_confirmation_token()
        new_group.confirmation_token_expiration = datetime.utcnow() + timedelta(minutes=10)

        db.session.add(new_group)
        db.session.commit()

        #update 
        # Create the user
        admin_user = Users(username=username, email=email, password=hashed_password, group_id=new_group.id, phone=phone, full_name=full_name)
        db.session.add(admin_user)
        db.session.commit()

        # Logout the current user
        logout_user()

        #send email
        confirm_url = url_for('authentication_blueprint.confirm_group', group_name=group_name, token=new_group.confirmation_token, _external=True)
        send_confirmation_email(email, confirm_url, full_name, group_name, phone)
        return render_template('accounts/register.html',
                               msg='Group created successfully. Please check your email for confirmation link.',
                               success=True,
                               form=create_account_form)
    
    return render_template('accounts/register.html', form=create_account_form)




@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500


def send_confirmation_email(email, confirm_url, full_name, group_name, phone):
    with current_app.app_context():
        # Define header HTML with styles
        header_content = '''
            <html>
            <head>
                <style>
                    .navbar {
                        background-color: rgb(34, 164, 58);
                        /* Green */
                    }
                    .navbar .nav-link {
                        color: #ffffff;
                        /* White */
                    }
                    .navbar .nav-link:hover {
                        color: #ffc107;
                        /* Yellow */
                    }
                    .footer {
                        background-color: #28a745;
                        /* Green */
                        color: #ffffff;
                        /* White */
                        padding: 15px;
                    }
                </style>
            </head>
            <body>
                <nav class="navbar navbar-expand-lg navbar-light">
                    <a class="navbar-brand" href="#">Innovatel Hub Solution Ltd</a>
                    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"
                        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item">

                            </li>
                            <li class="nav-item">

                            </li>
                        </ul>
                    </div>
                </nav>
        '''

        # Define footer HTML
        footer_content = '''
                <footer class="footer">
                    <div class="container">
                        <div class="row">
                            <div class="col-md-4">
                                <h5>About Us</h5>
                                <p>Innovatel Hub Solution Ltd is a financial management platform designed to help you track your
                                    expenses, set budgets, and achieve your financial goals.</p>
                            </div>
                            <div class="col-md-4">
                                <h5>Contact Us</h5>
                                <p>Email: support@Innovatelhubsolution.com</p>
                                <p>Phone: +6783224</p>
                            </div>
                            <div class="col-md-4">
                                <h5>Follow Us</h5>
                                <a href="#">Facebook</a><br>
                                <a href="#">Twitter</a><br>
                                <a href="#">Instagram</a>
                            </div>
                        </div>
                    </div>
                </footer>
            </body>
            </html>
        '''

        # Compose email body with header and footer
        email_body = f'''
            {header_content}
            <div class="container">
                <h3>Group Confirmation</h3>
                <p>Dear {full_name},</p>
                <p>Thank you for your interest in confirming your group. Please click the link below to proceed with the confirmation process. Please note that this link will expire in 10 minutes.</p>
                <p>Details:</p>
                <ul>
                    <li>Group name: {group_name}</li>
                    <li>Phone: {phone} </li>
                </ul>
                <p>Confirmation link: <a href="{confirm_url}">{confirm_url}</a></p>
                <p>If you did not initiate this request, please disregard this email.</p>
                <p>Thank you,</p>
                <p>Innovatel Hub Solution Ltd</p>
            </div>
            {footer_content}
        '''
        # Send email
        msg = Message(subject='Group Confirmation', sender='innovatelhubsolutionltd@gmail.com', recipients=[email])
        msg.html = email_body
        current_app.extensions['mail'].send(msg)



@blueprint.route('/<group_name>/confirm/<token>')
def confirm_group(group_name, token):
    group = Group.query.filter_by(group_name=group_name).first()
    if group and group.confirmation_token == token and group.confirmation_token_expiration > datetime.utcnow():
        group.confirmed = True
        db.session.commit()
        return render_template('home/group_creation_success.html', group_name=group_name)

    # Handle invalid or expired token
    return render_template('home/confirmation_error.html', msg='Invalid or expired confirmation token')

