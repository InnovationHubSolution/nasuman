# apps/admin/routes.py
from flask import render_template, request,flash,session, redirect
from . import admin_blueprint
from apps import db
import bcrypt
from apps.authentication.models import Admin, Users

# admin loign
@admin_blueprint.route('/admin/',methods=["POST","GET"])
def adminIndex():
    # chect the request is post or not
    if request.method == 'POST':
        # get the value of field
        username = request.form.get('username')
        password = request.form.get('password')
        # check the value is not empty
        if username=="" and password=="":
            flash('Please fill all the field','danger')
            return redirect('/admin/')
        else:
            # login admin by username 
            admins=Admin().query.filter_by(username=username).first()
            if admins and bcrypt.check_password_hash(admins.password,password):
                session['admin_id']=admins.id
                session['admin_name']=admins.username
                flash('Login Successfully','success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Email and Password','danger')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html',title="Admin Login")


# admin Dashboard
@admin_blueprint.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    totalUser=Users.query.count()
    totalApprove=Users.query.filter_by(status=1).count()
    NotTotalApprove=Users.query.filter_by(status=0).count()
    return render_template('admin/dashboard.html',title="Admin Dashboard",totalUser=totalUser,totalApprove=totalApprove,NotTotalApprove=NotTotalApprove)




# admin get all user 
@admin_blueprint.route('/admin/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method== "POST":
        search=request.form.get('search')
        users=Users.query.filter(Users.username.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='Approve User',users=users)
    else:
        users=Users.query.all()
        return render_template('admin/all-user.html',title='Approve User',users=users)
    

@admin_blueprint.route('/admin/approve-user/<int:id>')
def adminApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    Users().query.filter_by(id=id).update(dict(status=1))
    db.session.commit()
    flash('Approve Successfully','success')
    return redirect('/admin/get-all-user')


@admin_blueprint.route('/admin/change-admin-password',methods=["POST","GET"])
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('Please fill the field','danger')
            return redirect('/admin/change-admin-password')
        else:
            Admin().query.filter_by(username=username).update(dict(password=bcrypt.generate_password_hash(password,10)))
            db.session.commit()
            flash('Admin Password update successfully','success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)
    

# admin logout
@admin_blueprint.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')