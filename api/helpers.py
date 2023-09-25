import os
from hashlib import sha256
from random import randint
import operator

from sqlalchemy import asc, desc

from constants import ALLOWED_EXTENSIONS


def generate_hash(st):
    return sha256(st.encode('utf-8')).hexdigest()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def quick_sort(ls, attribute=None):
    if len(ls) < 2:
        return ls
    pivot = randint(1, len(ls) - 1)
    left = []
    centre = []
    right = []
    for element in ls:
        if attribute:
            if operator.attrgetter(attribute)(element) < operator.attrgetter(attribute)(ls[pivot]):
                left.append(element)
            elif operator.attrgetter(attribute)(element) > operator.attrgetter(attribute)(ls[pivot]):
                right.append(element)
            else:
                centre.append(element)
        else:
            if element < ls[pivot]:
                left.append(element)
            elif element > ls[pivot]:
                right.append(element)
            else:
                centre.append(element)
    return quick_sort(left, attribute) + centre + quick_sort(right, attribute)


def save_file(file, course_name, topic_subtopic, sec_filename, root_path):
    file_name_from_request = file.filename
    if allowed_file(file_name_from_request):
        filename_for_save = f'{course_name}_{topic_subtopic}_{sec_filename}'
        folder_path = os.path.join(root_path, course_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, filename_for_save)
        file.save(file_path)
        return file_path
    return


def sort_and_filter_users(users_query, filter_query, sort_query, range_query):
    # Apply filtering
    if filter_query:
        # Parse filter query, e.g., "field_name:value"
        filter_parts = filter_query.split(':')
        if len(filter_parts) == 2:
            filter_field, filter_value = filter_parts
            users_query = users_query.filter(getattr(User, filter_field) == filter_value)

    # Apply sorting
    if sort_query:
        # Parse sort query, e.g., "field:order"
        sort_parts = sort_query.split(':')
        if len(sort_parts) == 2:
            sort_field, sort_order = sort_parts
            if sort_order == 'asc':
                users_query = users_query.order_by(asc(sort_field))
            elif sort_order == 'desc':
                users_query = users_query.order_by(desc(sort_field))

    # Paginate the results
    if range_query:
        # Parse range query, e.g., "page:per_page"
        range_parts = range_query.split(':')
        if len(range_parts) == 2:
            page, per_page = map(int, range_parts)
            users_paginated = users_query.paginate(page, per_page, False)
            users_list = [user.user_to_dict() for user in users_paginated.items]

            return users_list, users_paginated.pages

    return [], 0




if __name__ == '__main__':
    print(generate_hash('123456'))
    ls = [4, 6, 8, 2, 1, 8, 9, 6, 4]
    print(quick_sort(ls))
