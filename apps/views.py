from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash
from flask_login import login_user, current_user
from .models import User, Group, Member, db
import secrets
from flask import jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message

views = Blueprint('views', __name__)
bcrypt = Bcrypt()

@views.route('/')
@views.route("/home")
def dashboard():
    return render_template("index.html")



from flask import jsonify

@views.route('/create_group', methods=['POST'])
def create_group():
    if request.method == 'POST':
        group_name = request.form.get('groupName')
        admin_name = request.form.get('adminName')
        email = request.form.get('email')
        island = request.form.get('island')
        village = request.form.get('village')
        admin_password = request.form.get('adminPassword')

        # Check if group name already exists
        existing_group_name = Group.query.filter_by(name=group_name).first()
        existing_username = User.query.filter_by(username=email).first()
        if existing_group_name:
            error_message = 'Group name already exists.'
            return jsonify({'error': error_message})
        if existing_username:
            error_message = 'Username already exits.'
            return jsonify({'error': error_message})

        # Create a new group
        new_group = Group(admin_name=admin_name, name=group_name, email=email, island=island, village=village, admin_password=admin_password)
        new_group.generate_confirmation_token() # Generate confirmation token after creating the group
        db.session.add(new_group)
        db.session.commit()

        # Create an admin user associated with the new group
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
        admin_user = User(username=email, email=email, password=hashed_password, is_admin=True, group_id=new_group.id)
        db.session.add(admin_user)
        db.session.commit()

        # Generate and send confirmation email
        confirmation_token = new_group.confirmation_token
        confirm_url = url_for('views.confirm_group', group_name=group_name, token=confirmation_token, _external=True)
        send_confirmation_email(email, confirm_url, admin_name, group_name, island, village)

        # Return success message
        return jsonify({'success': 'Group created successfully'})

    # Handle GET requests or other cases
    return jsonify({'error': 'Invalid request'})



def send_confirmation_email(email, confirm_url, admin_name, group_name, island, village):
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
                                <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#createGroupModal">
                                    Create New Group
                                </button>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#login">Login</a>
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
                <p>Dear {admin_name},</p>
                <p>Thank you for your interest in confirming your group. Please click the link below to proceed with the confirmation process. Please note that this link will expire in 10 minutes.</p>
                <p>Details:</p>
                <ul>
                    <li>Group name: {group_name}</li>
                    <li>Village: {village}</li>
                    <li>Island: {island}</li>
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



@views.route('/group_creation_success')
def group_creation_success():
    return render_template('group_creation_success.html')



@views.route('/<group_name>/confirm/<token>')
def confirm_group(group_name, token):
    group = Group.query.filter_by(name=group_name).first()
    if group and group.confirmation_token == token and group.confirmation_token_expiration > datetime.utcnow():
        group.confirmed = True
        db.session.commit()
        flash('Group confirmed! You can now add members.', 'success')
    else:
        flash('Invalid or expired confirmation link.', 'danger')
    return redirect(url_for('views.dashboard'))
