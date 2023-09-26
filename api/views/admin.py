# from flask_security import roles_required
import json
from datetime import datetime

from flask import request, jsonify, make_response
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required

from app import app, db, login_manager
from helpers import generate_hash
from models import User, Course, Team, Role, UserRoles, MentorOfCourse, TeamLeadOfTeam


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/admin/login', methods=['POST', 'GET'])
@cross_origin(supports_credentials=True)
def login_admin():
    if request.method == 'POST':
        data = request.json
        username = data['username']
        password = data['password']
        user = User.query.filter_by(
            username=username, password=generate_hash(password)).first()
        if user:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify(message='Invalid username or password'), 401
    return jsonify(message='Method Not Allowed'), 405


@app.route('/admin/register_user', methods=['POST'])
@jwt_required()
def register_user():
    if request.method == 'POST':
        data = request.json
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        birthday = data.get('birthday')
        role = data.get('role')
        if firstname and lastname and username and email and phone and password and birthday and role:
            if not User.query.filter_by(username=username).first():
                user = User(firstname=firstname,
                            lastname=lastname,
                            username=username,
                            email=email,
                            phone=phone,
                            password=generate_hash(password),
                            birthday=datetime.strptime(birthday, "%Y-%m-%d").date())
                db.session.add(user)
                db.session.commit()
                role = Role.query.filter_by(role_name=role).first()
                user_id = User.query.filter_by(username=username).first().id
                role_id = role.id
                user_role = UserRoles(user_id=user_id, role_id=role_id)
                db.session.add(user_role)
                db.session.commit()
                return jsonify(message='Successfully registered'), 200
        return jsonify(message='bad request'), 400
    return jsonify(message='Method Not Allowed'), 405


# new route
@app.route('/admin/<userrole>', methods=['GET'])
@jwt_required()
def get_users(userrole):
    if request.method == 'GET':
        role = Role.query.filter_by(role_name=userrole).first()
        if role:
            user_role_entries = UserRoles.query.filter_by(
                role_id=role.id).all()
            user_ids = [entry.user_id for entry in user_role_entries]
            user_length = len(user_ids)
            query = User.query.filter(User.id.in_(user_ids))
            filter_param = request.args.get('filter')
            if filter_param:
                filter_dict = json.loads(filter_param)
                if 'username' in filter_dict:
                    query = query.filter(User.username.ilike(
                        f"%{filter_dict['username']}%"))
            sort_param = request.args.get('sort')
            if sort_param:
                sort_array = json.loads(sort_param)
                if len(sort_array) == 2:
                    field = sort_array[0]
                    order = sort_array[1].lower()
                    if order == 'asc':
                        query = query.order_by(getattr(User, field))
                    elif order == 'desc':
                        query = query.order_by(getattr(User, field).desc())
            range_param = request.args.get('range')
            if range_param:
                range_array = json.loads(range_param)
                if len(range_array) == 2:
                    start = range_array[0]
                    end = range_array[1]
                    query = query.slice(start, end + 1)
            users = query.all()
            users_list = [user.user_to_dict() for user in users]

            response = make_response(users_list)
            response.headers['content-range'] = user_length
            return response, 200
        else:
            return jsonify(message='Role not found'), 404
    else:
        return jsonify(message='Method Not Allowed'), 405




@app.route('/admin/courses', methods=['POST', 'GET', 'PUT', 'DELETE'])
@jwt_required()
def admin_courses():
    if request.method == 'POST':
        data = request.json
        course_name = data.get('course_name')
        if course_name:
            course = Course(course_name=course_name)
            db.session.add(course)
            db.session.commit()
            return jsonify({'message': 'Course added successfully'}), 200
        else:
            return jsonify(message='Bad request'), 400
    elif request.method == 'GET':
        course_query = Course.query

        filter_param = request.args.get('filter')
        if filter_param:
            filter_dict = json.loads(filter_param)
            if 'course_name' in filter_dict:
                course_query = course_query.filter(
                    Course.course_name.ilike(f"%{filter_dict['course_name']}%"))

        sort_param = request.args.get('sort')
        if sort_param:
            sort_array = json.loads(sort_param)
            if len(sort_array) == 2:
                field = sort_array[0]
                order = sort_array[1].lower()
                if order == 'asc':
                    course_query = course_query.order_by(getattr(Course, field))
                elif order == 'desc':
                    course_query = course_query.order_by(
                        getattr(Course, field).desc())

        range_param = request.args.get('range')
        if range_param:
            range_array = json.loads(range_param)
            if len(range_array) == 2:
                start = range_array[0]
                end = range_array[1]
                course_query = course_query.slice(start, end + 1)

        courses = course_query.all()
        course_list = [course.course_to_dict() for course in courses]

        return jsonify(courses=course_list), 200

    elif request.method == 'PUT':
        data = request.json
        course_id = data.get('id')
        course_new_name = data.get('course_new_name')
        course = Course.query.filter_by(id=course_id).first()
        if course:
            course.course_name = course_new_name
            db.session.commit()
            return jsonify({'message': 'Course edited successfully'}), 200
        else:
            return jsonify(message='Bad request'), 400

    elif request.method == 'DELETE':
        data = request.json
        course_id = data.get('id')
        course = Course.query.filter_by(id=course_id).first()
        if course:
            db.session.delete(course)
            db.session.commit()
            return jsonify({'message': 'Course deleted successfully'}), 200
        else:
            return jsonify(message='Bad request'), 400
    return jsonify(message='Method Not Allowed'), 405


@app.route('/admin/teams', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def admin_teams():
    if request.method == 'GET':
        team_query = Team.query

        filter_param = request.args.get('filter')
        if filter_param:
            filter_dict = json.loads(filter_param)
            if 'team_name' in filter_dict:
                team_query = team_query.filter(
                    Team.team_name.ilike(f"%{filter_dict['team_name']}%"))

        sort_param = request.args.get('sort')
        if sort_param:
            sort_array = json.loads(sort_param)
            if len(sort_array) == 2:
                field = sort_array[0]
                order = sort_array[1].lower()
                if order == 'asc':
                    team_query = team_query.order_by(getattr(Team, field))
                elif order == 'desc':
                    team_query = team_query.order_by(
                        getattr(Team, field).desc())

        range_param = request.args.get('range')
        if range_param:
            range_array = json.loads(range_param)
            if len(range_array) == 2:
                start = range_array[0]
                end = range_array[1]
                team_query = team_query.slice(start, end + 1)

        teams = team_query.all()
        teams_list = [team.team_to_dict() for team in teams]

        return jsonify(teams=teams_list), 200
    elif request.method == 'POST':
        data = request.json
        team_name = data.get('team_name')
        if team_name:
            team = Team(team_name=team_name)
            db.session.add(team)
            db.session.commit()
            return jsonify({'message': 'Team added successfully'}), 200
        else:
            return jsonify(message='Bad request'), 400
    elif request.method == 'PUT':
        data = request.json
        team_id = data.get('id')
        team_new_name = data.get('team_new_name')
        team = Team.query.filter_by(id=team_id).first()
        if team:
            team.team_name = team_new_name
            db.session.commit()
            return jsonify({'message': 'Team edited successfully'}), 200
        else:
            return jsonify(message='Bad request'), 400
    elif request.method == 'DELETE':
        data = request.json
        team_id = data.get('id')
        team = Team.query.filter_by(id=team_id).first()
        if team:
            db.session.delete(team)
            db.session.commit()
            return jsonify({'message': 'Team deleted successfully'}), 200
        else:
            return jsonify(message='Bad request'), 400
    return jsonify(message='Method Not Allowed'), 405


@app.route('/admin/<userrole>/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def get_user_info(userrole, id):
    if request.method == 'GET':
        role = Role.query.filter_by(role_name=userrole).first()
        if role:
            user_role_entry = UserRoles.query.filter_by(
                role_id=role.id, user_id=id).first()
            if user_role_entry:
                user = User.query.filter_by(id=id).first()
                if user:
                    return jsonify(user.user_to_dict()), 200
                else:
                    return jsonify(message='User not found'), 404
            else:
                return jsonify(message=f'{userrole} role not assigned to the user'), 404
        else:
            return jsonify(message='Role not found'), 404
    elif request.method == 'PUT':
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.json
            new_firstname = data.get('firstname')
            new_lastname = data.get('lastname')
            new_username = data.get('username')
            new_email = data.get('email')
            new_phone = data.get('phone')
            new_password = data.get('password')
            new_birthday = data.get('birthday')
            new_role = data.get('role')

            user.firstname = new_firstname
            user.lastname = new_lastname
            user.username = new_username
            user.email = new_email
            user.phone = new_phone
            user.password = generate_hash(new_password)
            user.birthday = new_birthday
            role = Role.query.filter_by(role_name=new_role).first()
            if role:
                user.roles = [role]
            db.session.commit()
            return jsonify(message='Successfully edited'), 200
        return jsonify(message='User not found'), 404
    elif request.method == 'DELETE':
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify(message='User deleted successfully'), 200
        else:
            return jsonify(message='User not found'), 404
    return jsonify(message='Method Not Allowed'), 405


@app.route('/admin/attache_<userrole>_course', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def attache_mentor_course(userrole):
    if request.method == 'GET':
        roles = Role.query.filter_by(role_name=userrole).first()

        if roles:
            user_roles = UserRoles.query.filter_by(role_id=roles.id).all()
            users_info = []

            for user_role in user_roles:
                user = User.query.filter_by(id=user_role.user_id).first()
                users_info.append({
                    "id": user.id,
                    "first name": user.firstname,
                    "last name": user.lastname
                })

            courses = Course.query.all()
            course_list = [course.course_to_dict() for course in courses]

            info = {
                "courses": course_list,
                userrole: users_info
            }

            return jsonify(info), 200
        else:
            return jsonify(message='Role not found'), 404
    elif request.method == 'POST':
        data = request.json
        course_id = data.get('course_id')
        mentor_id = data.get('mentor_id')
        if mentor_id and course_id:
            attach_mentor = MentorOfCourse(
                user_id=mentor_id, course_id=course_id)
            db.session.add(attach_mentor)
            db.session.commit()
            return jsonify({'message': 'Mentor attached successfully'}), 200
        else:
            return jsonify(message='bad request'), 400
    elif request.method == 'PUT':
        data = request.json
        course_id = data.get('course_id')
        mentor_id = data.get('mentor_id')

        if mentor_id and course_id:
            mentor_and_course = MentorOfCourse.query.filter_by(
                user_id=mentor_id, course_id=course_id).first()

            if mentor_and_course:
                mentor_and_course.user_id = mentor_id
                mentor_and_course.course_id = course_id

            db.session.commit()
            return jsonify({'message': 'Mentor and course attached/updated successfully'}), 200
        else:
            return jsonify(message='Bad request'), 400
    elif request.method == 'DELETE':
        data = request.json
        mentor_id = data.get('mentor_id')
        course_id = data.get('course_id')

        mentor_and_course = MentorOfCourse.query.filter_by(
            user_id=mentor_id, course_id=course_id).first()

        if mentor_and_course:
            db.session.delete(mentor_and_course)
            db.session.commit()
            return jsonify({'message': 'Mentor and course deleted successfully'}), 200
        else:
            return jsonify(message='Record not found'), 404



@app.route('/admin/attach_user_to_team', methods=['POST'])
@jwt_required()
def attache_teamlead_course():
    data = request.json
    if request.method == 'POST':
        team_id = data.get('team_id')
        user_id = data.get('user_id')
        if user_id and team_id:
            attach_user = TeamLeadOfTeam(user_id=user_id, team_id=team_id)
            db.session.add(attach_user)
            db.session.commit()
            return jsonify({'message': 'User attached successfully'}), 200
        else:
            return jsonify({'message': 'user or Team does not exist'}), 405
    return jsonify(message='bad request'), 400
