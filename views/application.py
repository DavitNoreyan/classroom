from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, RegisterForm
from flask_security import roles_required
from werkzeug.utils import secure_filename

from app import app, db, login_manager
from models import User, Course, Progress, FullProgress, Team, Role, UserRoles, TeamLeadOfTeam, MentorOfCourse, \
    TrainingCourses, Topic, Subtopic
from helpers import generate_hash, allowed_file, quick_sort


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    form = LoginForm()
    return render_template('application/loginform/index.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        if user:
            user_role = UserRoles.query.filter_by(user_id=user.id).first()
            role_name = Role.query.filter_by(id=user_role.role_id).first().role_name
            if data['username'] == user.username and generate_hash(data['password']) == user.password:
                if role_name == 'mentor':
                    login_user(user)
                    return redirect(url_for('mentor_dashboard', username=user.username))
                elif role_name == 'teamlead':
                    login_user(user)
                    return redirect(url_for('teamlead_dashboard', username=user.username))
                elif role_name == 'student':
                    pass  # TODO

                else:
                    pass  # TODO
            else:
                error_message = 'Wrong password'
                return render_template('application/loginform/index.html', form=form, error=error_message)
        else:
            error_message = 'Wrong username'
            return render_template('application/loginform/index.html', form=form, error=error_message)
    return render_template('application/loginform/index.html', form=form)


@app.route('/mentor/dashboard', defaults={'username': 'admin'})
@app.route('/mentor/dashboard/<username>')
# @login_required
def mentor_dashboard(username):
    user_id = User.query.filter_by(username=username).first().id

    attached_courses = MentorOfCourse.query.filter_by(user_id=user_id).all()
    attached_courses_by_courses = [Course.query.filter_by(id=course.course_id).first() for course in attached_courses]
    return render_template('application/mentor/dashboard/index.html',
                           username=username,
                           attached_courses_by_courses=attached_courses_by_courses)


@app.route('/teamlead/dashboard/<username>')
def teamlead_dashboard(username):
    users = User.query.all()  # TODO filter by student
    student_role_id = Role.query.filter_by(role_name='student').first().id
    user_roles = UserRoles.query.filter_by(role_id=student_role_id).all()
    student_user_id_list = [user.user_id for user in user_roles]
    students_list = []
    for user in users:
        if user.id in student_user_id_list:
            usr = User.query.filter_by(username=user.username).first()
            usr_id = usr.id
            fullprg = FullProgress.query.filter_by(id=usr_id).first()
            user.fullprogress = fullprg.progress_value
            students_list.append(user)

    user = User.query.filter_by(username=username).first()
    user_role = UserRoles.query.filter_by(user_id=user.id).first()
    role_name = Role.query.filter_by(id=user_role.role_id).first().role_name
    if role_name == 'teamlead':
        team_id_of_teamlead = TeamLeadOfTeam.query.filter_by(user_id=user.id).first().team_id
        team_of_teamlead = Team.query.filter_by(id=team_id_of_teamlead).first()
        attached_training_course = TrainingCourses.query.filter_by(team_id=team_id_of_teamlead).all()
        attached_training_course_by_courses = [Course.query.filter_by(id=course.course_id).first() for course in
                                               attached_training_course]
        available_courses = Course.query.all()
        available_not_attached_courses = set(available_courses).symmetric_difference(
            set(attached_training_course_by_courses))
        return render_template('application/mentor/dashboard/index.html', username=username,
                               users=students_list,
                               attached_training_course_by_courses=attached_training_course_by_courses,
                               available_not_attached_courses=available_not_attached_courses,
                               team_of_teamlead=team_of_teamlead, role_name=role_name)
    elif role_name == 'mentor':
        attached_training_course = MentorOfCourse.query.filter_by(user_id=user.id).all()
        attached_training_course_by_courses = [Course.query.filter_by(id=course.course_id).first() for course in
                                               attached_training_course]
        pass


@app.route('/teamlead/course/add', methods=['POST'])
def teamlead_add_course():
    username = current_user.username
    data = request.form
    course_name = data['course']
    teamlead = User.query.filter_by(username=username).first()
    team = TeamLeadOfTeam.query.filter_by(user_id=teamlead.id).first()
    course = Course.query.filter_by(course_name=course_name).first()
    course_queue = data['course_queue']
    if course and team and course_queue:
        attach_course = TrainingCourses(team_id=team.team_id, course_id=course.id, training_queue=course_queue)
        db.session.add(attach_course)
        db.session.commit()
    else:
        flash('name of course is not correct')
    return redirect(url_for('mentor_dashboard', username=username))


@app.route('/teamlead/course/delete-attached-course', methods=['POST'])
def teamlead_delete_course():
    username = current_user.username
    data = request.form
    course_name = data['course']
    if course_name:
        course_id = Course.query.filter_by(course_name=course_name).first().id
        attached_course = TrainingCourses.query.filter_by(course_id=course_id).first()
        db.session.delete(attached_course)
        db.session.commit()
    return redirect(url_for('mentor_dashboard', username=username))


@app.route('/courses/<course_name>')
def courses(course_name):
    username = current_user.username
    course_id = Course.query.filter_by(course_name=course_name).first().id
    course_topics = quick_sort(Topic.query.filter_by(course_id=course_id).all(), attribute='topic_queue')
    course_subtopics = []
    for course_topic in course_topics:
        course_subtopics += Subtopic.query.filter_by(topic_id=course_topic.id).all()

    return render_template('application/mentor/coursespage/index.html',
                           username=username,
                           course=course_name,
                           topics=course_topics,
                           subtopics=course_subtopics)


@app.route('/courses/<course_name>/add-topic', methods=['POST'])
def courses_add_topic(course_name):
    if request.method == 'POST':
        data = request.form
        topic_name = data['topic']
        if data['queue'] and course_name:
            if data['queue'].isnumeric():
                course_id = Course.query.filter_by(course_name=course_name).first().id
                course_topics = Topic.query.filter_by(course_id=course_id).all()
                topics_id_list = [topic.id for topic in course_topics]
                queue = data['queue']
                if int(queue) not in topics_id_list:
                    topic = Topic(topic_name=topic_name, course_id=course_id, topic_queue=queue)
                    db.session.add(topic)
                    db.session.commit()
                else:
                    flash('topic queue is available')
            else:
                flash('Topic queue can be only numeric')
        else:
            flash('set queue')  # TODO
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/edit-topic', methods=['POST'])
def courses_edit_topic(course_name):
    if request.method == 'POST':
        data = request.form
        topic_name = data['topic']
        if topic_name:
            topic = Topic.query.filter_by(topic_name=topic_name).first()
            if topic:
                new_name_for_topic = data['topic_new_name']
                new_queue_for_topic = data['topic_new_queue']
                if new_name_for_topic and new_queue_for_topic:
                    if new_queue_for_topic != topic.topic_queue:
                        course_id = Course.query.filter_by(course_name=course_name).first().id
                        course_topics = Topic.query.filter_by(course_id=course_id).all()
                        topics_queue_list = [topic.topic_queue for topic in course_topics]
                        if int(new_queue_for_topic) in topics_queue_list:
                            available_topic_with_new_queue = Topic.query.filter_by(course_id=course_id,
                                                                                   topic_queue=new_queue_for_topic).first()
                            available_topic_with_new_queue.topic_queue, topic.topic_queue = topic.topic_queue, available_topic_with_new_queue.topic_queue
                        else:
                            topic.topic_queue = new_queue_for_topic
                    else:
                        topic.topic_queue = new_queue_for_topic
                    topic.topic_name = new_name_for_topic
                    db.session.commit()
            else:
                flash('not correct topic name')
        else:
            flash('topic name required for edit')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/delete-topic', methods=['POST'])
def courses_delete_topic(course_name):
    data = request.form
    if request.method == 'POST':
        if data['topic']:
            course_id = Course.query.filter_by(course_name=course_name).first().id
            topic_name = data['topic']
            topic_for_delete = Topic.query.filter_by(topic_name=topic_name, course_id=course_id).first()
            db.session.delete(topic_for_delete)
            db.session.commit()
        else:
            flash('topic name is required for deleting!')
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/add-subtopic', methods=['POST'])
def courses_add_subtopic(course_name):
    data = request.form
    topic = data['topic_name']
    subtopic = data['subtopic']
    subtopic_queue = data['queue']
    if topic and subtopic and subtopic_queue:
        topic_id = Topic.query.filter_by(topic_name=topic).first().id
        subtopic = Subtopic(subtopic_name=subtopic, topic_id=topic_id, subtopic_queue=subtopic_queue)
        db.session.add(subtopic)
        db.session.commit()
    else:
        return 'problem'
    return redirect(url_for('courses', course_name=course_name))


@app.route('/courses/<course_name>/add-resurse>')
def courses_add_resurse(course_name):
    pass


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    return render_template('pagenotfound/index.html')


@app.route('/test/<name>/<age>')
def test(name, age):
    return f'<h1>{name}-{age}</h1>'
