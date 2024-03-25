# -*- encoding: utf-8 -*-

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required, current_user
from flask import current_app
from jinja2 import TemplateNotFound
from apps import db
from apps.authentication.models import Subscription, Member
from apps.home.forms import ProfileForm, MemberForm
from werkzeug.utils import secure_filename
import os

@blueprint.route('/index')
@login_required
def index():
    user_group = current_user.group
    
    return render_template('home/index.html', segment='index', user_id=current_user.id, user_group=user_group)

@blueprint.route('/dashboard')
@login_required
def dashboard():
    
    profile_image = current_user.profile_image
    if not profile_image:
        # Use the default profile image if no profile image is set
        ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')
        default_profile_image = os.path.join(ASSETS_ROOT, 'img', 'team', 'profile-default.png')
        profile_image = default_profile_image
    
    return render_template('home/dashboard.html', profile_image=profile_image)


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None



@blueprint.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    # Populate the form with the current user's data
    if current_user.group:
        group_name = current_user.group.group_name
    else:
        group_name = "No Group" # Or any default value you prefer

    form = ProfileForm(email=current_user.email, group=group_name)
    if form.validate_on_submit():
        # Update the user's profile
        current_user.full_name = form.full_name.data
        current_user.birthday = form.birthday.data
        current_user.gender = form.gender.data
        current_user.island = form.island.data
        # The email field is read-only and should not be updated from the form
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.province = form.province.data
        current_user.island = form.island.data
     
        
        db.session.commit()
        
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('home_blueprint.update_profile'))
    
        # Get the profile image path
    profile_image = current_user.profile_image
    if not profile_image:
        # Use the default profile image if no profile image is set
        ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')
        default_profile_image = os.path.join(ASSETS_ROOT, 'img', 'team', 'profile-default.png')
        profile_image = default_profile_image
    
    return render_template('home/settings.html', form=form, profile_image=profile_image)


@blueprint.route('/profile_image', methods=['POST'])
@login_required
def update_profile_photo():
    if 'profile_image' not in request.files:
        flash('No file part', 'warning')
        return redirect(request.referrer)

    file = request.files['profile_image']
    if file.filename == '':
        flash('No selected file', 'warning')
        return redirect(request.referrer)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        new_filename = f"profile-image-{current_user.id}.jpg"
        
        # Construct the directory path using ASSETS_ROOT
        ASSETS_ROOT = os.getenv('ASSETS_ROOT', 'static/assets')
        directory = os.path.join(ASSETS_ROOT, 'img', 'team') 
        os.makedirs(directory, exist_ok=True)  # Ensure the directory exists
        
        file_path = os.path.join(directory, new_filename)
        
        file.save(file_path)
        current_user.profile_image = file_path
        db.session.commit()
        flash('Profile photo updated.', 'success')
        return jsonify({'message': 'Profile photo updated.'})
    else:
        flash('File type not allowed', 'warning')
        return jsonify({'error': 'File type not allowed'}), 400


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@blueprint.route('/members', methods=['POST'])
@login_required
def members():

        return render_template("home/members.html")


@blueprint.route('/subscribe', methods=['POST'])
@login_required
def subscribe():

        return render_template("home/subscription.html")


@blueprint.route('/addmembers', methods=['GET', 'POST'])
@login_required
def addmembers():
    # Populate the form with the data from the request
    form = MemberForm()
    
    # Check if the current user has a subscription
    if not current_user.subscription_id:
        flash('You need to subscribe to a plan to create members.', 'error')
        return redirect(url_for('home_blueprint.subscribe'))  # Redirect to subscription page
    
    subscription_id = current_user.subscription_id

    if form.validate_on_submit():
        # Query the subscription to get its plan details
        subscription = Subscription.query.get(subscription_id)
        max_members_allowed = subscription.plan.max_members
        
        # Count the current number of members
        current_member_count = Member.query.filter_by(user_id=current_user.id).count()
        
        if current_member_count >= max_members_allowed:
            flash('You have reached the maximum number of members allowed for your subscription plan.', 'error')
            return redirect(url_for('home_blueprint.dashboard'))  # Redirect to appropriate page
        
        # Get the current user's group ID
        group_id = current_user.group.id if current_user.group else None
        new_member = Member(
            full_name=form.full_name.data,
            phone=form.phone.data,
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            address=form.address.data,
            relative_name=form.relative_name.data,
            relative_phone=form.relative_phone.data,
            relative_address=form.relative_address.data,
            group_id=group_id
        )

        # Add the new member to the database
        db.session.add(new_member)
        db.session.commit()

        flash('Member added successfully', 'success')
        form = MemberForm()  # Clear the form after successful submission
        return render_template('home/addmembers.html', form=form)
    
    return render_template('home/addmembers.html', form=form)


