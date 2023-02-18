from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, RegisterForm
from flask_security import roles_required
from datetime import date, datetime

from app import app, db, login_manager
from models import User, Course, Progress, FullProgress, Team, Role, UserRoles, TeamLeadOfTeam, MentorOfCourse, \
    TrainingCourses
from helpers import generate_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/', methods=['GET', 'POST'])
# @roles_required('admin')
def admin():
    form = LoginForm()
    if request.method == 'POST':
        data = request.form
        username = data['username']
        user = User.query.filter_by(username=username).first()

        if user:
            if data['username'] == user.username and generate_hash(data['password']) == user.password:
                login_user(user)
                return redirect(url_for('admin_dashboard', username=user.username))
            else:
                error_message = 'Wrong password'
                return render_template('admin/loginform/index.html', form=form, error=error_message)
        else:
            error_message = 'Wrong username'
            return render_template('admin/loginform/index.html', form=form, error=error_message)
    return render_template('admin/loginform/index.html', form=form)


@app.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin'))


@app.route('/admin/dashboard')
@app.route('/admin/dashboard/<username>')
# @login_required
def admin_dashboard(username):
    users = User.query.all()
    teams = Team.query.all()
    teamlead_role = Role.query.filter_by(role_name='teamlead').first()
    all_teamleads_in_user_role = UserRoles.query.filter_by(role_id=teamlead_role.id)
    attached_teamleads_id_list = [user.user_id for user in TeamLeadOfTeam.query.all()]
    team_leads_wthout_team = []
    for lead in all_teamleads_in_user_role:
        if lead.user_id not in attached_teamleads_id_list:
            team_leads_wthout_team.append(User.query.filter_by(id=lead.user_id).first())
    attached_teams_id_list = [team.team_id for team in TeamLeadOfTeam.query.all()]
    teams_without_lead = []
    for team in teams:
        if team.id not in attached_teams_id_list:
            teams_without_lead.append(team)
    team_attached_to_team_lead = TeamLeadOfTeam.query.all()
    team_and_teamlead = [(Team.query.filter_by(id=attached_team_andteamlead.team_id).first(),
                          User.query.filter_by(id=attached_team_andteamlead.user_id).first()) for
                         attached_team_andteamlead in
                         team_attached_to_team_lead]
    for user in users:
        role_id = UserRoles.query.filter_by(user_id=user.id).first().role_id
        role = Role.query.filter_by(id=role_id).first().role_name
        user.role = role
    roles = Role.query.all()
    avalaible_courses = Course.query.all()
    attached_mentor_id_set = set([mentor.user_id for mentor in MentorOfCourse.query.all()])
    attached_mentor_to_course = []
    for mentor_id in attached_mentor_id_set:
        one_mentor_attached_courses = MentorOfCourse.query.filter_by(user_id=mentor_id).all()
        one_mentor_attached_courses_names = [Course.query.filter_by(id=attached_course.course_id).first().course_name
                                             for
                                             attached_course in one_mentor_attached_courses]
        mentor_and_courses = (User.query.filter_by(id=mentor_id).first().username, one_mentor_attached_courses_names)
        attached_mentor_to_course.append(mentor_and_courses)

    form = RegisterForm()
    return render_template('admin/dashboard/index.html',
                           username=username,
                           users=users,
                           form=form,
                           roles=roles,
                           teams=teams,
                           team_leads_wthout_team=team_leads_wthout_team,
                           teams_without_lead=teams_without_lead,
                           team_and_teamlead=team_and_teamlead,
                           avalaible_courses=avalaible_courses,
                           attached_mentor_to_course=attached_mentor_to_course, now_date=date.today())


@app.route('/admin/dashboard_css/delete/<user_id>')
# @login_required
def admin_delete_user(user_id):
    user = User.query.filter_by(id=user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/daashboard/edit/<user_id>')
# @login_required
def admin_edit_user(user_id):
    user = User.query.filter_by(id=user_id)
    data = request.form  # TODO chack from form data can not be empty
    user.firstname = data['firstname']
    user.lastname = data['lastname']
    user.username = data['lastname']
    user.email = data['email']
    user.phone = data['phone']
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/register', methods=['POST'])
# @login_required
def admin_register():
    # form = RegisterForm()
    if request.method == 'POST':
        data = request.form
        # if form.validate_on_submit():
        birthday = datetime.strptime(data['birthday'], "%Y-%m-%d").date()
        user = User(firstname=data['firstname'],
                    lastname=data['lastname'],
                    username=data['username'],
                    password=generate_hash(data['password']),
                    birthday=birthday,
                    email=data['email'],
                    phone=data['phone'])
        db.session.add(user)
        db.session.commit()
        added_user = User.query.filter_by(username=user.username).first()
        added_user_id = added_user.id
        fullprogress = FullProgress(progress_value=0, user_id=added_user_id)
        db.session.add(fullprogress)
        db.session.commit()
        role = Role.query.filter_by(role_name=data['role']).first()
        role_id = role.id
        user_role = UserRoles(user_id=added_user_id, role_id=role_id)
        db.session.add(user_role)
        db.session.commit()
    username = current_user.username
    return redirect(url_for('admin_dashboard', username=username))


@app.route('/admin/team/add', methods=['POST'])
# @login_required
def admin_add_team():
    username = current_user.username
    data = request.form
    team_name = data['team']
    check_team_avalblity = Team.query.filter_by(team_name=team_name).first()
    if not check_team_avalblity and team_name:
        team = Team(team_name=team_name)
        db.session.add(team)
        db.session.commit()
        return redirect(url_for('admin_dashboard', username=username))
    else:
        flash('Team exists')
        return redirect(url_for('admin_dashboard', username=username))


@app.route('/admin/team/delete', methods=['POST'])
def admin_team_delete():
    username = current_user.username
    data = request.form
    team = Team.query.filter_by(team_name=data['teamname']).first()
    team_lead_of_team = TeamLeadOfTeam.query.filter_by(team_id=team.id).first()
    db.session.delete(team)
    if team_lead_of_team:
        db.session.delete(team_lead_of_team)
    db.session.commit()
    return redirect(url_for('admin_dashboard', username=username))


@app.route('/admin/course/add', methods=['POST'])
def admin_add_course():
    username = current_user.username
    data = request.form
    course_name = data['course']
    check_course_avalability = Course.query.filter_by(course_name=course_name).first()
    if not check_course_avalability and course_name:
        course = Course(course_name=course_name)
        db.session.add(course)
        db.session.commit()
    else:
        flash('course already exists')
    return redirect(url_for('admin_dashboard', username=username))


@app.route('/admin/course/delete', methods=['POST'])
def admin_delete_course():
    username = current_user.username
    data = request.form
    course_name = data['coursename']
    course = Course.query.filter_by(course_name=course_name).first()
    mentor_of_course = MentorOfCourse.query.filter_by(course_id=course.id).all()
    for mentor in mentor_of_course:
        db.session.delete(mentor)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('admin_dashboard', username=username))


@app.route('/admin/attach_teamlead', methods=['POST'])
def admin_attach_teamlead():
    username = current_user.username
    data = request.form
    team_name = data['team']
    lead_name = data['lead']
    lead_id = User.query.filter_by(username=lead_name).first().id
    team_id = Team.query.filter_by(team_name=team_name).first().id
    team_lead_of_team_by_team = TeamLeadOfTeam.query.filter_by(team_id=team_id).first()
    team_lead_of_team_by_lead = TeamLeadOfTeam.query.filter_by(user_id=lead_id).first()
    if not team_lead_of_team_by_team:
        if not team_lead_of_team_by_lead:
            team_lead_of_team = TeamLeadOfTeam(team_id=team_id, user_id=lead_id)
            db.session.add(team_lead_of_team)
            db.session.commit()
        else:
            flash(f'{lead_name} attached on another team')
    else:
        flash(f'{team_name} already have teamlead')
    return redirect(url_for('admin_dashboard', username=username))


@app.route('/admin/delete-attached-teamlead', methods=['POST'])
def admin_delete_attached_teamlead():
    username = current_user.username
    data = request.form
    user_id = User.query.filter_by(username=data['username']).first().id
    team_id = Team.query.filter_by(team_name=data['teamname']).first().id
    team_lead_of_team = TeamLeadOfTeam.query.filter_by(user_id=user_id, team_id=team_id).first()
    db.session.delete(team_lead_of_team)
    db.session.commit()
    return redirect(url_for('admin_dashboard', username=username))


@app.route('/admin/attach-mentor-course', methods=['POST'])
def admin_attach_course_mentor():
    username = current_user.username
    data = request.form
    mentor = User.query.filter_by(username=data['mentor']).first()
    course = Course.query.filter_by(course_name=data['course']).first()
    if mentor and course:
        check_mentor_avalability = MentorOfCourse.query.filter_by(user_id=mentor.id, course_id=course.id).first()
        if not check_mentor_avalability:
            attach_mentor = MentorOfCourse(user_id=mentor.id, course_id=course.id)
            db.session.add(attach_mentor)
            db.session.commit()
        else:
            flash('mentor already attached to course')
    else:
        flash('')  # TODO
    return redirect(url_for('admin_dashboard', username=username))


@app.route('/admin/delete-mentor-from-course')
def admin_delete_mentor_from_course():
    data = request.data

    pass
