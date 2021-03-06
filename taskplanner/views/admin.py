from taskplanner import app
from taskplanner.model import (db,
                               User,
                               Task,
                               TaskNote,
                               Project,
                               Role,
                               Client)
from taskplanner.helpers import (login_required,
                                 required_roles,
                                 get_client_select_group)
from taskplanner.forms import (LoginForm,
                               RoleForm,
                               UserForm,
                               EditUserForm,
                               DeleteUserForm,
                               ClientForm,
                               AddProjectForm,
                               EditProjectForm,
                               EditTaskForm,
                               AddTaskForm)
from flask import (request,
                   session,
                   redirect,
                   url_for,
                   render_template,
                   flash,
                   abort)

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
@required_roles('admin')
def add_user():
    error = None
    form = UserForm()
    form.roles.choices = [(x.name, x.name) for x in Role.query.order_by('name')]
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).count() > 0:
            error = "User already exists"
        else:
            user = User(form.username.data, form.password.data)
            user.fname = form.fname.data
            user.lname = form.lname.data
            user.email = form.email.data
            for role in form.roles.data:
                theRole = Role.query.filter_by(name=role).one()
                user.roles.append(theRole)
            db.session.add(user)
            db.session.commit()
            msg = "{0} added".format(user.fullname)
            flash(msg)
            return redirect(url_for('users'))
    return render_template("admin/adduser.html", error=error, form=form)

@app.route('/edit_user/<username>', methods=['GET', 'POST'])
@login_required
@required_roles('admin')
def edit_user(username):
    error = None
    user = User.query.filter_by(username=username).first() or abort(404)
    form = EditUserForm(obj=user)
    form.roles.choices =  [(x.name, x.name) for x in Role.query.order_by('name')]
    if request.method == 'GET':
        form.roles.data = [x.name for x in user.roles]  
    if form.validate_on_submit():
        edited = False
        if user.fname <> form.fname.data:
            edited = True
            user.fname = form.fname.data
        if user.lname <> form.lname.data:
            edited = True
            user.lname = form.lname.data
        if user.email <> form.email.data:
            edited = True
            user.email = form.email.data
        uroles = [x.name for x in user.roles]
        if uroles <> form.roles.data:
            edited = True
            user.roles = []
            for role in form.roles.data:
                theRole = Role.query.filter_by(name=role).one()
                user.roles.append(theRole)
        if form.password.data:
            edited = True
            user.set_password(form.password.data)
        if edited:
            db.session.commit()
            msg = "{0} updated".format(user.fullname)
            flash(msg)
            return redirect(url_for('users'))
        else:
            flash("No data was updated")
    return render_template("admin/edituser.html", error=error, username=username, form=form)

@app.route('/delete_user/<username>', methods=['GET', 'POST'])
@login_required
@required_roles('admin')
def delete_user(username):
    form = DeleteUserForm()
    user = User.query.filter_by(username=username).first() or abort(404)
    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(user)
            msg = "{0} deleted".format(user.fullname)
            db.session.commit()
        else:
            msg = "{0} not deleted".format(user.fullname)
        flash(msg)
        return redirect(url_for('users'))
    return render_template("admin/deleteuser.html", form=form, user=user)

@app.route('/users')
@login_required
@required_roles('admin')
def users():
    users = User.query.order_by('lname')
    return render_template("admin/users.html", users=users)

@app.route("/admin/")
@login_required
@required_roles('admin')
def adminview():
    return render_template("admin/admin.html")

@app.route("/add_role", methods=['GET', 'POST'])
@login_required
@required_roles('admin')
def add_role():
    error = None
    form = RoleForm(request.form)
    theRoles = Role.query.all()
    if form.validate_on_submit():
        if Role.query.filter_by(name=form.name.data).count() > 0:
            error = "%s role already exists" % form.name.data
        else:
            role = Role(form.name.data)
            db.session.add(role)
            db.session.commit()
            flash("%s role added", role.name)
            return redirect(url_for('adminview'))
    return render_template("admin/addrole.html", roles = theRoles, form=form, error=error)