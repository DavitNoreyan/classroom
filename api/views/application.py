from flask import render_template, request, jsonify
from flask_jwt_extended import create_access_token

from app import app, login_manager
from forms import LoginForm
from helpers import generate_hash
from models import User, Course, Role, UserRoles, Topic, Subtopic, Exam, ExamResult, ExamDueDates


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    form = LoginForm()
    return render_template('application/loginform/index.html', form=form)


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username, password=generate_hash(password)).first()
        if user:
            access_token = create_access_token(identity=username)
            roles = Role.query.join(UserRoles).filter(UserRoles.user_id == user.id).all()
            role_names = [role.role_name for role in roles]
            return jsonify(access_token=access_token, message='Login successful', roles=role_names), 200
        else:
            return jsonify(message='Invalid username or password'), 401
    else:
        return jsonify(message='Method Not Allowed'), 405


@app.route('/get_courses/<mentor_username>')
def get_courses_mentor_username(mentor_username):
    if request.method == 'GET':
        data = request.json
        mentor = User.query.filter_by(username=mentor_username).first()
        if mentor:
            course_name = data['course_name']
            course_id = data['id']
            courses = Course.query.filter_by(id=course_id, course_name=course_name).first()
            if courses:
                course_list = []
                course_list.append({
                    'course_name': courses.course_name,
                    'id': courses.id
                })
                return jsonify({'courses': course_list, 'message': 'get course by mentor username successfully'}), 200
            else:
                return jsonify(message='Course not found'), 405
        else:
            return jsonify(message='Mentor not found'), 405
    else:
        return jsonify(message='bad request'), 400


@app.route('/get_topic_by_course/<course_name>')
def get_topic_by_course(course_name):
    if request.method == 'GET':
        course = Course.query.filter_by(course_name=course_name).first()
        if course:
            topic_results = Topic.query.filter_by(course_id=course.id).all()
            topics = []
            for topic_result in topic_results:
                topic_data = {
                    'id': topic_result.id,
                    'topic': topic_result.topic_name,
                    'queue': topic_result.topic_queue
                }
                topics.append(topic_data)

            response = {
                'course': course_name,
                'topics': topics
            }
            return jsonify(response)
        else:
            return jsonify(message='Course not found!!'), 405
    else:
        return jsonify(message='bad request'), 400


@app.route('/get_subtopic_by_topic/<topic_name>')
def get_subtopic_by_topic(topic_name):
    if request.method == 'GET':
        topic = Topic.query.filter_by(topic_name=topic_name).first()
        if topic:
            subtopics = []
            subtopic_results = Subtopic.query.filter_by(topic_id=topic.id).all()
            for subtopic_result in subtopic_results:
                subtopic_data = {
                    'id': subtopic_result.id,
                    'subtopic': subtopic_result.subtopic_name,
                    'queue': subtopic_result.subtopic_queue
                }
                subtopics.append(subtopic_data)

                response = {
                    'topic': topic_name,
                    'subtopics': subtopics
                }
            return jsonify(response)
        else:
            return jsonify(message='Topic not found'), 400
    else:
        return jsonify(message='bad request'), 400


@app.route('/get_took_exams', methods=['POST'])
def get_took_exams():
    data = request.json
    if request.method == 'POST':
        course_id = data.get('course_id')
        if course_id is not None:
            course = Course.query.get(course_id)
            if course:
                exams = Exam.query.filter_by(course_id=course_id).all()
                took_exams = []

                for exam in exams:
                    exam_result = ExamResult.query.get(exam.exam_result_id)
                    exam_date = ExamDueDates.query.get(exam.exam_due_date_id)

                    if exam_result and exam_date:
                        exam_data = {
                            'id': exam_result.id,
                            'username': exam.user_id,
                            'score': exam_result.grade,
                            'date': exam_date.exam_expected_date
                        }
                        took_exams.append(exam_data)

                return jsonify(took_exams=took_exams, message='Took exams successfully!!'), 200
            else:
                return jsonify(message='Course not found'), 400
        else:
            return jsonify(message='Course ID not provided'), 400
    else:
        return jsonify(message='Bad request'), 400


#TO DO
'''@app.route('/get_students_by_courses', methods=['POST'])'''
# def get_students_by_courses():
#     if request.method == 'POST':
#         data = request.json
#         course_id = data['course_ids']
#         students = []
#         course = Course.query.filter_by(id=course_id).first()
#         if course:
#             student = User.query.filter_by(id=User.id, username=User.username, progress=User.progresses).first()
#             student_info = {
#                 'id': student.id,
#                 'username': student.username,
#                 'progress': student.progress
#             }
#             students.append(student_info)
#         else:
#             return jsonify(message='Course not found'), 404
#         response = {
#             'students': students
#         }
#         return jsonify(response), 200
#     else:
#         return jsonify(message='Bad request'), 400
#







#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if request.method == 'POST':
#         data = request.form
#         user = User.query.filter_by(username=data['username']).first()
#         if user:
#             user_role = UserRoles.query.filter_by(user_id=user.id).first()
#             role_name = Role.query.filter_by(id=user_role.role_id).first().role_name
#             if data['username'] == user.username and generate_hash(data['password']) == user.password:
#                 if role_name == 'mentor':
#                     login_user(user)
#                     return redirect(url_for('mentor_dashboard', username=user.username))
#                 elif role_name == 'teamlead':
#                     login_user(user)
#                     return redirect(url_for('teamlead_dashboard', username=user.username))
#                 elif role_name == 'student':
#                     pass  # TODO
#
#                 else:
#                     pass  # TODO
#             else:
#                 error_message = 'Wrong password'
#                 return render_template('application/loginform/index.html', form=form, error=error_message)
#         else:
#             error_message = 'Wrong username'
#             return render_template('application/loginform/index.html', form=form, error=error_message)
#     return render_template('application/loginform/index.html', form=form)
#
#
# @app.route('/mentor/dashboard', defaults={'username': 'admin'})
# @app.route('/mentor/dashboard/<username>')
# # @login_required
# def mentor_dashboard(username):
#     user_id = User.query.filter_by(username=username).first().id
#
#     attached_courses = MentorOfCourse.query.filter_by(user_id=user_id).all()
#     attached_courses_by_courses = [Course.query.filter_by(id=course.course_id).first() for course in attached_courses]
#     return render_template('application/mentor/dashboard/index.html',
#                            username=username,
#                            attached_courses_by_courses=attached_courses_by_courses)
#
#
# @app.route('/teamlead/dashboard/<username>')
# def teamlead_dashboard(username):
#     users = User.query.all()  # TODO filter by student
#     student_role_id = Role.query.filter_by(role_name='student').first().id
#     user_roles = UserRoles.query.filter_by(role_id=student_role_id).all()
#     student_user_id_list = [user.user_id for user in user_roles]
#     students_list = []
#     for user in users:
#         if user.id in student_user_id_list:
#             usr = User.query.filter_by(username=user.username).first()
#             usr_id = usr.id
#             fullprg = FullProgress.query.filter_by(id=usr_id).first()
#             user.fullprogress = fullprg.progress_value
#             students_list.append(user)
#
#     user = User.query.filter_by(username=username).first()
#     user_role = UserRoles.query.filter_by(user_id=user.id).first()
#     role_name = Role.query.filter_by(id=user_role.role_id).first().role_name
#     if role_name == 'teamlead':
#         team_id_of_teamlead = TeamLeadOfTeam.query.filter_by(user_id=user.id).first().team_id
#         team_of_teamlead = Team.query.filter_by(id=team_id_of_teamlead).first()
#         attached_training_course = TrainingCourses.query.filter_by(team_id=team_id_of_teamlead).all()
#         attached_training_course_by_courses = [Course.query.filter_by(id=course.course_id).first() for course in
#                                                attached_training_course]
#         available_courses = Course.query.all()
#         available_not_attached_courses = set(available_courses).symmetric_difference(
#             set(attached_training_course_by_courses))
#         return render_template('application/mentor/dashboard/index.html', username=username,
#                                users=students_list,
#                                attached_training_course_by_courses=attached_training_course_by_courses,
#                                available_not_attached_courses=available_not_attached_courses,
#                                team_of_teamlead=team_of_teamlead, role_name=role_name)
#     elif role_name == 'mentor':
#         attached_training_course = MentorOfCourse.query.filter_by(user_id=user.id).all()
#         attached_training_course_by_courses = [Course.query.filter_by(id=course.course_id).first() for course in
#                                                attached_training_course]
#         pass
#
#
# @app.route('/teamlead/course/add', methods=['POST'])
# def teamlead_add_course():
#     username = current_user.username
#     data = request.form
#     course_name = data['course']
#     teamlead = User.query.filter_by(username=username).first()
#     team = TeamLeadOfTeam.query.filter_by(user_id=teamlead.id).first()
#     course = Course.query.filter_by(course_name=course_name).first()
#     course_queue = data['course_queue']
#     if course and team and course_queue:
#         attach_course = TrainingCourses(team_id=team.team_id, course_id=course.id, training_queue=course_queue)
#         db.session.add(attach_course)
#         db.session.commit()
#     else:
#         flash('name of course is not correct')
#     return redirect(url_for('mentor_dashboard', username=username))
#
#
# @app.route('/teamlead/course/delete-attached-course', methods=['POST'])
# def teamlead_delete_course():
#     username = current_user.username
#     data = request.form
#     course_name = data['course']
#     if course_name:
#         course_id = Course.query.filter_by(course_name=course_name).first().id
#         attached_course = TrainingCourses.query.filter_by(course_id=course_id).first()
#         db.session.delete(attached_course)
#         db.session.commit()
#     return redirect(url_for('mentor_dashboard', username=username))
#
#
# @app.route('/courses/<course_name>')
# def courses(course_name):
#     username = current_user.username
#     course_id = Course.query.filter_by(course_name=course_name).first().id
#     course_topics = quick_sort(Topic.query.filter_by(course_id=course_id).all(), attribute='topic_queue')
#     course_subtopics = []
#     source_by_course_topic = []
#     video_source_by_topic = []
#     for course_topic in course_topics:
#         course_subtopics += Subtopic.query.filter_by(topic_id=course_topic.id).all()
#         source_by_course_topic += SourceOfLearningTextContent.query.filter_by(topic_id=course_topic.id).all()
#         video_source_by_topic += SourceOfLearningVideoContent.query.filter_by(topic_id=course_topic.id).all()
#
#     source_by_course_subtopics = []
#     video_source_by_subtopic = []
#     for subtopic in course_subtopics:
#         source_by_course_subtopics += SourceOfLearningTextContent.query.filter_by(subtopic_id=subtopic.id).all()
#         video_source_by_subtopic += SourceOfLearningVideoContent.query.filter_by(subtopic_id=subtopic.id).all()
#
#     return render_template('application/mentor/coursespage/index.html',
#                            username=username,
#                            course=course_name,
#                            topics=course_topics,
#                            subtopics=course_subtopics,
#                            source_by_course_topic=source_by_course_topic,
#                            source_by_course_subtopics=source_by_course_subtopics,
#                            video_source_by_topic=video_source_by_topic,
#                            video_source_by_subtopic=video_source_by_subtopic)
#
#
# @app.route('/courses/<course_name>/add-topic', methods=['POST'])
# def courses_add_topic(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'topic' in data and 'queue' in data:
#             topic_name = data['topic']
#             if topic_name:
#                 queue = data['queue']
#                 if queue:
#                     if queue.isnumeric():
#                         course_id = Course.query.filter_by(course_name=course_name).first().id
#                         course_topics = Topic.query.filter_by(course_id=course_id).all()
#                         topics_id_list = [topic.id for topic in course_topics]
#                         if int(queue) not in topics_id_list:
#                             topic = Topic(topic_name=topic_name, course_id=course_id, topic_queue=queue)
#                             db.session.add(topic)
#                             db.session.commit()
#                         else:
#                             flash('topic queue is available')
#                     else:
#                         flash('Topic queue can be only numeric')
#                 else:
#                     flash('queue is required')  # TODO
#             else:
#                 flash('topic name is required')
#         else:
#             flash('topic name and queue is not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/edit-topic', methods=['POST'])
# def courses_edit_topic(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'topic_id' in data:
#             topic_id = int(data['topic_id'])
#             if topic_id:
#                 topic = Topic.query.filter_by(id=topic_id).first()
#                 if topic:
#                     if 'topic_new_queue' in data and 'topic_new_name':
#                         topic_new_queue = data['topic_new_queue']
#                         topic_new_name = data['topic_new_name']
#                         if topic_new_name or topic_new_queue:
#                             if topic_new_name:
#                                 topic.topic_name = topic_new_name
#                             if topic_new_queue and topic_new_name.isnumeric():
#                                 if int(topic_new_queue) != topic.topic_queue:
#                                     course_id = Course.query.filter_by(course_name=course_name).first().id
#                                     course_topics = Topic.query.filter_by(course_id=course_id).all()
#                                     topics_queue_list = [topic.topic_queue for topic in course_topics]
#                                     if topic_new_queue in topics_queue_list:
#                                         available_topic_with_new_queue = Topic.query.filter_by(course_id=course_id,
#                                                                                                topic_queue=topic_new_queue).first()
#                                         available_topic_with_new_queue.topic_queue, topic.topic_queue = topic.topic_queue, available_topic_with_new_queue.topic_queue
#                                     else:
#                                         topic.topic_queue = topic_new_queue
#                                 else:
#                                     topic.topic_queue = topic_new_queue
#                             db.session.commit()
#                         else:
#                             flash('topic new queue or new name is required')
#                     else:
#                         flash('new queue and new name not in request')
#                 else:
#                     flash('not topic with this id')
#             else:
#                 flash('topic id is required')
#         else:
#             flash('topic id not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/delete-topic', methods=['POST'])
# def courses_delete_topic(course_name):
#     data = request.form
#     if request.method == 'POST':
#         if 'topic_id' in data:
#             if data['topic_id']:
#                 topic_id = int(data['topic_id'])
#                 topic = Topic.query.filter_by(id=topic_id).first()
#                 db.session.delete(topic)
#                 db.session.commit()
#             else:
#                 flash('topic id is required')
#         else:
#             flash('topic id not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/add-subtopic', methods=['POST'])
# def courses_add_subtopic(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'topic_id' in data and 'subtopic' in data and 'queue' in data:
#             topic_id = data['topic_id']
#             subtopic = data['subtopic']
#             subtopic_queue = data['queue']
#             if topic_id:
#                 if subtopic:
#                     if subtopic_queue and subtopic_queue.isnumeric():
#                         available_queues = [av_subtopic.subtopic_queue for av_subtopic in
#                                             Subtopic.query.filter_by(topic_id=int(topic_id)).all()]
#                         if int(subtopic_queue) not in available_queues:
#                             subtopic = Subtopic(subtopic_name=subtopic, topic_id=topic_id,
#                                                 subtopic_queue=subtopic_queue)
#                             db.session.add(subtopic)
#                             db.session.commit()
#                         else:
#                             flash('queue is available')
#                     else:
#                         flash('subtopic queue is required and need be a numeric')
#                 else:
#                     flash('subtopic is required')
#             else:
#                 flash('topic id is required')
#         else:
#             flash('topic id, subtopic name and subtopic queue is not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/edit-subtopic', methods=['POST'])
# def courses_edit_subtopic(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'subtopic_id' in data:
#             if 'new_queue' in data:
#                 if 'new_subtopic' in data:
#                     subtopic_id = data['subtopic_id']
#                     new_queue = data['new_queue']
#                     new_subtopic = data['new_subtopic']
#                     if subtopic_id:
#                         if new_queue or new_subtopic:
#                             subtopic = Subtopic.query.filter_by(id=subtopic_id).first()
#                             if new_subtopic:
#                                 subtopic.subtopic_name = new_subtopic
#                             if new_queue and new_queue.isnumeric():
#                                 topic_id_of_subtopic = subtopic.topic_id
#                                 available_subtopic_queue_list = [st.subtopic_queue for st in Subtopic.query.filter_by(
#                                     topic_id=topic_id_of_subtopic).all()]
#                                 if int(new_queue) in available_subtopic_queue_list:
#                                     available_subtopic_with_new_queue = Subtopic.query.filter_by(
#                                         topic_id=topic_id_of_subtopic, subtopic_queue=new_queue).first()
#                                     subtopic.subtopic_queue, available_subtopic_with_new_queue.subtopic_queue = \
#                                         available_subtopic_with_new_queue.subtopic_queue, subtopic.subtopic_queue
#                                 else:
#                                     subtopic.subtopic_queue = new_queue
#                             db.session.commit()
#                         else:
#                             flash('new queue or new subtopic name is required')
#                     else:
#                         flash('subtopic id is required')
#                 else:
#                     flash('new subtopic not in request')
#             else:
#                 flash('new queue not in  request')
#
#         else:
#             flash('subtopic id not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/delete-subtopic', methods=['POST'])
# def courses_delete_subtopic(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'subtopic_id' in data:
#             subtopic_id = data['subtopic_id']
#             if subtopic_id:
#                 subtopic = Subtopic.query.filter_by(id=subtopic_id).first()
#                 db.session.delete(subtopic)
#                 db.session.commit()
#             else:
#                 flash('subtopic id is required')
#         else:
#             flash('subtopic id not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/add-plaintext-content>', methods=['POST'])
# def courses_add_plaintext_content(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'content_header' in data:
#             content_header = data['content_header']
#             if 'content_plain_text' in data:
#                 content_plain_text = data['content_plain_text']
#                 if content_header:
#                     if content_plain_text:
#                         if 'topic_id' in data or 'subtopic_id' in data:
#                             if 'topic_id' in data:
#                                 topic_id = data['topic_id']
#                                 if topic_id:
#                                     content = SourceOfLearningTextContent(source_content_header=content_header,
#                                                                           source_content_plain_text=content_plain_text,
#                                                                           topic_id=topic_id)
#                                 else:
#                                     flash('topic id is required')
#                             if 'subtopic_id' in data:
#                                 subtopic_id = data['subtopic_id']
#                                 if subtopic_id:
#                                     content = SourceOfLearningTextContent(source_content_header=content_header,
#                                                                           source_content_plain_text=content_plain_text,
#                                                                           subtopic_id=subtopic_id)
#                                 else:
#                                     flash('subtopic id is required')
#                             db.session.add(content)
#                             db.session.commit()
#                         else:
#                             flash('topic id and subtopic id not in request')
#                     else:
#                         flash('Content is required')
#                 else:
#                     flash('content header is required')
#             else:
#                 flash('content plain text not in request')
#         else:
#             flash('content header not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/edit-plaintext-content>', methods=['POST'])
# def courses_edit_plaintext_content(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'content_id' in data:
#             if 'new_header' in data:
#                 if 'new_content_plain_text' in data:
#                     content_id = data['content_id']
#                     new_header = data['new_header']
#                     new_content_plain_text = data['new_content_plain_text']
#                     if content_id:
#                         content = SourceOfLearningTextContent.query.filter_by(id=content_id).first()
#                         if new_header or new_content_plain_text:
#                             if new_header:
#                                 content.source_content_header = new_header
#                             if new_content_plain_text:
#                                 content.source_content_plain_text = new_content_plain_text
#                             db.session.commit()
#                         else:
#                             flash('content header or content plain text is required')
#
#                     else:
#                         flash('content id is required')
#                 else:
#                     flash('content plain text not in request')
#             else:
#                 flash('content header not in request')
#         else:
#             flash('content id not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/delete-plaintext-content>', methods=['POST'])
# def courses_delete_plaintext_content(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'content_id' in data:
#             content_id = data['content_id']
#             if content_id:
#                 content = SourceOfLearningTextContent.query.filter_by(id=content_id).first()
#                 db.session.delete(content)
#                 db.session.commit()
#             else:
#                 flash('content id is required')
#         else:
#             flash('content id not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/upload-video-content>', methods=['POST'])
# def courses_upload_video_content(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'video_name' in data:
#             if 'queue' in data:
#                 if 'subtopic_id' in data or 'topic_id' in data:
#                     subtopic_id = data.get('subtopic_id')
#                     topic_id = data.get('topic_id')
#                     video_name = data['video_name']
#                     queue = data['queue']
#                     if subtopic_id:
#                         subtopic_name_or_topic_name = Subtopic.query.filter_by(id=subtopic_id).first().subtopic_name
#                     else:
#                         subtopic_name_or_topic_name = Topic.query.filter_by(id=topic_id).first().topic_name
#                     if video_name and queue:
#                         if 'file' in request.files:
#                             file = request.files['file']
#                             if file.filename:
#                                 upload_root_path = os.path.join(app.config["UPLOAD_FOLDER"])
#                                 sec_filename = secure_filename(file.filename)
#                                 file_path = save_file(file=file,
#                                                       course_name=course_name,
#                                                       topic_subtopic=subtopic_name_or_topic_name,
#                                                       sec_filename=sec_filename,
#                                                       root_path=upload_root_path)
#                                 if file_path:
#                                     video_content = SourceOfLearningVideoContent(video_name=video_name,
#                                                                                  video_path=file_path,
#                                                                                  topic_id=topic_id,
#                                                                                  subtopic_id=subtopic_id,
#                                                                                  video_queue=queue)
#                                     db.session.add(video_content)
#                                     db.session.commit()
#                             else:
#                                 flash('File not selected')
#                         else:
#                             flash('file not in request')
#                     else:
#                         flash('video name and video queue is required')
#                 else:
#                     flash('topic id and subtopic id not in request')
#             else:
#                 flash('queue not in request')
#         else:
#             flash('video name not in request')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/courses/<course_name>/edit-video-content>', methods=['POST'])
# def courses_edit_video_content(course_name):
#     if request.method == "POST":
#         data = request.form
#         if 'id' in data:
#             source_video_id = data['id']
#             source_video = SourceOfLearningVideoContent.query.filter_by(id=source_video_id).first()
#             if 'video_queue' or 'video_name' or 'video_content' in data:
#                 video_queue = data['video_queue']
#                 video_name = data['video_name']
#                 video_path = data['video_path']
#                 if video_queue:
#                     source_video.video_queue = video_queue
#                 if video_name:
#                     source_video.video_name = video_name
#                 if video_path:
#                     if 'file' in request.files:
#                         file = request.files['file']
#                         if file.filename:
#                             upload_root_path = os.path.join(app.config["UPLOAD_FOLDER"])
#                             sec_filename = secure_filename(file.filename)
#                             file_path = save_file(file=file,
#                                                   course_name=course_name,
#                                                   topic_subtopic=subtopic_name_or_topic_name,
#                                                   sec_filename=sec_filename,
#                                                   root_path=upload_root_path)
#                             if file_path:
#                                 video_content = SourceOfLearningVideoContent(video_name=video_name,
#                                                                              video_path=file_path,
#                                                                              topic_id=topic_id,
#                                                                              subtopic_id=subtopic_id,
#                                                                              video_queue=queue)
#                                 db.session.add(video_content)
#                                 db.session.commit()
#                     source_video.video_path = video_path
#             else:
#                 flash('wideo queue or video name or video content required')
#         else:
#             flash('id is required')
#
#
# @app.route('/courses/<course_name>/delete-video-content>', methods=['POST'])
# def courses_delete_video_content(course_name):
#     if request.method == 'POST':
#         data = request.form
#         if 'id' in data:
#             source_video_id = data['id']
#             source_video = SourceOfLearningVideoContent.query.filter_by(id=source_video_id).first()
#             path_of_video = source_video.video_path
#             db.session.delete(source_video)
#             db.session.commit()
#             os.remove(path_of_video)
#         else:
#             flash('id for video required')
#     return redirect(url_for('courses', course_name=course_name))
#
#
# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))
#
#
# @app.errorhandler(404)
# def not_found(e):
#     return render_template('pagenotfound/index.html')
#
#
# @app.route('/test/<name>/<age>')
# def test(name, age):
#     return f'<h1>{name}-{age}</h1>'
