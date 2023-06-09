import functools
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)

from stdhomework.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
def index():
    return render_template('admin/admin_index.html')

# 定义获取用户信息的 API,可通过用户的身份或者姓名查看
@bp.route('/admin_info', methods=['GET'])
def get_admin_info():
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    admin_name = request.args.get('admin_name')
    sql = f"SELECT * FROM admininfo where name = '{admin_name}'"
    # 执行 SQL 查询语句
    cursor.execute(sql)
    # 获取查询结果
    users = cursor.fetchall()
    # 关闭游标
    cursor.close()
    if len(users) == 0:
        return jsonify({'code': 404, 'msg': '未找到任何用户信息'})
    # 返回查询结果
    return jsonify({'code': 0, "msg": "", "count": len(users), 'data': users})


# 定义获取用户信息的 API,可通过用户的身份或者姓名查看
@bp.route('/users', methods=['GET'])
def get_users():
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    user_name = request.args.get('user_name')
    identity = request.args.get('identity')

    # 构建 SQL 查询语句
    conditions = []
    if user_name:
        conditions.append(f"name = '{user_name}'")
    if identity:
        conditions.append(f"identity = '{identity}'")

    if conditions:
        where_clause = " AND ".join(conditions)  # 使用 AND 连接列表中的每一个元素
        sql = f"SELECT * FROM user WHERE {where_clause}"
    else:
        sql = "SELECT * FROM user"
    # 执行 SQL 查询语句
    cursor.execute(sql)
    # 获取查询结果
    users = cursor.fetchall()
    # 关闭游标
    cursor.close()
    if len(users) == 0:
        return jsonify({'code': 404, 'msg': '未找到任何用户信息'})
    # 返回查询结果
    return jsonify({'code': 0, "msg": "", "count": len(users), 'data': users})


@bp.route('/users', methods=['POST'])
def add_user():
    try:
        user_name = request.json['user_name']
        password = request.json['password']
        email = request.json['email']
        identity = request.json['identity']
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db = get_db()
        # 创建一个 cursor 对象
        cursor = db.cursor()
        cursor.execute(f'INSERT INTO user (name, password, email, identity, create_time) VALUES '
                       f'("{user_name}", "{password}", "{email}", "{identity}", "{create_time}")')

        # 提交更改并关闭游标
        db.commit()
        cursor.close()

        # 返回成功信息
        return jsonify({'code': 201, 'msg': '用户信息添加成功'})
    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 查询指定的用户信息是否存在
    cursor.execute(f'SELECT * FROM user WHERE id = "{user_id}"')
    user = cursor.fetchone()

    # 如果用户信息不存在，则返回 404 错误
    if not user:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {user_id} 的用户信息'})

    # 更新用户
    # 获取 POST 请求上传的数据
    user_id = request.json.get('user_id', user['id'])
    user_name = request.json.get('user_name', user['name'])
    password = request.json.get('password', user['password'])
    email = request.json.get('email', user['email'])
    identity = request.json.get('identity', user['identity'])
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        f'UPDATE user SET name = "{user_name}", password = "{password}", email = "{email}", identity = "{identity}", create_time = "{create_time}"'
        f' WHERE id = "{user_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'code': 200, 'msg': f'ID 为 {user_id} 的用户信息已更新'})


# 定义删除学生信息的 API
@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 stu_id 查询学生信息
    cursor.execute(f'SELECT * FROM user WHERE id = "{user_id}"')

    # 获取查询结果
    student = cursor.fetchone()

    # 如果查询结果为空，则返回 404 错误
    if not student:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {user_id} 的用户信息'})

    # 删除用户信息
    cursor.execute(f'DELETE FROM user WHERE id = "{user_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'code': 200, 'msg': f'ID 为 {user_id} 的用户信息已删除'})


# 获取 system_notice 表中所有的数据
@bp.route('/system_notice', methods=['GET'])
def get_system_notice():
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    admin_name = request.args.get('admin_name')

    # 构建 SQL 查询语句
    conditions = []
    if admin_name:
        conditions.append(f"name = '{admin_name}'")

    if conditions:
        # 有查询条件，按条件查询学生信息
        where_clause = " AND ".join(conditions)  # 使用 AND 连接列表中的每一个元素
        sql = f"SELECT A.*,B.name admin_name FROM system_notice A INNER JOIN admininfo B ON A.admin_id=B.id " \
              f"WHERE {where_clause} "
        cursor.execute(sql)
        system_notice = cursor.fetchall()
    else:
        cursor.execute("SELECT A.*,B.name admin_name FROM system_notice A INNER JOIN admininfo B ON A.admin_id=B.id")
        system_notice = cursor.fetchall()

    # 没有查询到任何学生记录，返回 404 错误响应
    if len(system_notice) == 0:
        return jsonify({'code': 404, 'msg': '未找到任何学生信息'})

    # 返回查询结果
    return jsonify({'code': 0, "msg": "", "count": len(system_notice), 'data': system_notice})


# 向 system_notice 表中插入数据
@bp.route('/system_notice', methods=['POST'])
def create_system_notice():
    # 解析请求中的 JSON 数据
    data = request.get_json()

    # 从 JSON 数据中获取数据
    title = data['title']
    content = data['content']
    admin_id = data['admin_id']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 插入新数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO system_notice (title, content, create_time, admin_id) VALUES (%s, %s, %s, %s)",
                       (title, content, create_time, admin_id))
        db.commit()
        # 返回成功信息
        return jsonify({'code': 201, 'msg': '系统通知添加成功'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()
        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 根据 id 更新 system_notice 表中的数据
@bp.route('/system_notice/<int:id>', methods=['PUT'])
def update_system_notice(id):
    # 解析请求中的 JSON 数据
    data = request.get_json()

    # 从 JSON 数据中获取数据
    title = data['title']
    content = data['content']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    admin_id = data['admin_id']

    # 更新数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("UPDATE system_notice SET title = %s, content = %s, create_time = %s, admin_id = %s WHERE id = %s",
                   (title, content, create_time, admin_id, id))
    db.commit()

    # 返回信息
    # 返回成功信息
    return jsonify({'code': 200, 'msg': f' ID{id}的通知已更新'})


# 根据 id 删除 system_notice 表中的数据
@bp.route('/system_notice/<int:id>', methods=['DELETE'])
def delete_system_notice(id):
    # 删除数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("DELETE FROM system_notice WHERE id = %s", (id,))
    db.commit()

    return jsonify({'code': 200, 'msg': f'ID 为 {id} 的信息已删除'})


# 定义获取学生信息的 API,可通过学生的姓名和班级查看
@bp.route('/students', methods=['GET'])
def get_students():
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    std_name = request.args.get('std_name')
    class_name = request.args.get('class_name')

    # 构建 SQL 查询语句
    conditions = []
    if std_name:
        conditions.append(f"name = '{std_name}'")
    if class_name:
        conditions.append(f"class_name = '{class_name}'")

    if conditions:
        # 有查询条件，按条件查询学生信息
        where_clause = " AND ".join(conditions)  # 使用 AND 连接列表中的每一个元素
        sql = f"SELECT * FROM studentinfo WHERE {where_clause}"
    else:
        # 没有查询条件，查询所有学生信息
        sql = "SELECT * FROM studentinfo"

    # 执行 SQL 查询语句
    cursor.execute(sql)

    # 获取查询结果
    students = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 没有查询到任何学生记录，返回 404 错误响应
    if len(students) == 0:
        return jsonify({'code': 404, 'msg': '未找到任何学生信息'})

    # 返回查询结果
    return jsonify({'code': 0, "msg": "", "count": len(students), 'data': students})


# 定义获取单个学生信息的 API
@bp.route('/students/<string:stu_id>', methods=['GET'])
def get_student(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 stu_id 查询学生信息
    cursor.execute(f'SELECT * FROM studentinfo WHERE stu_id = "{stu_id}"')

    # 获取查询结果
    student = cursor.fetchone()

    # 关闭游标
    cursor.close()

    # 如果查询结果为空，则返回 404 错误
    if not student:
        return jsonify({'error': f'未找到 ID 为 {stu_id} 的学生信息'}), 404

    # 返回查询结果
    return jsonify({'student': student}), 200


# 定义添加学生信息的 API
@bp.route('/students', methods=['POST'])
def add_student():
    try:
        # 获取 POST 请求上传的数据
        stu_id = request.json['stu_id']
        name = request.json['name']
        class_name = request.json['class_name']
        email = request.json['email']
        telephone = request.json['telephone']

        db = get_db()
        # 创建一个 cursor 对象
        cursor = db.cursor()

        # 插入新的学生信息
        cursor.execute(f'INSERT INTO studentinfo (stu_id, name, class_name, email, telephone) VALUES '
                       f'("{stu_id}", "{name}", "{class_name}", "{email}", "{telephone}")')

        # 提交更改并关闭游标
        db.commit()
        cursor.close()

        # 返回成功信息
        return jsonify({'code': 201, 'msg': '学生信息添加成功'})
    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 定义更新学生信息的 API
@bp.route('/students/<string:stu_id>', methods=['PUT'])
def update_student(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 查询指定的学生信息是否存在
    cursor.execute(f'SELECT * FROM studentinfo WHERE stu_id = "{stu_id}"')
    student = cursor.fetchone()

    # 如果学生信息不存在，则返回 404 错误
    if not student:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {stu_id} 的学生信息'})

    # 更新学生信息
    name = request.json.get('name', student['name'])
    class_name = request.json.get('class_name', student['class_name'])
    email = request.json.get('email', student['email'])
    telephone = request.json.get('telephone', student['telephone'])

    cursor.execute(
        f'UPDATE studentinfo SET name = "{name}", class_name = "{class_name}", email = "{email}", telephone = "{telephone}" WHERE stu_id = "{stu_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'code': 200, 'msg': f'ID 为 {stu_id} 的学生信息已更新'})


# 定义删除学生信息的 API
@bp.route('/students/<string:stu_id>', methods=['DELETE'])
def delete_student(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 stu_id 查询学生信息
    cursor.execute(f'SELECT * FROM studentinfo WHERE stu_id = "{stu_id}"')

    # 获取查询结果
    student = cursor.fetchone()

    # 如果查询结果为空，则返回 404 错误
    if not student:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {stu_id} 的学生信息'})

    # 删除学生信息
    cursor.execute(f'DELETE FROM studentinfo WHERE stu_id = "{stu_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'code': 200, 'msg': f'ID 为 {stu_id} 的学生信息已删除'})


# 定义获取教师信息列表的 API
@bp.route('/teachers', methods=['GET'])
def get_teacher():
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    tea_name = request.args.get('tea_name')

    # 构建 SQL 查询语句
    conditions = []
    if tea_name:
        conditions.append(f"name = '{tea_name}'")

    if conditions:
        # 有查询条件，按条件查询学生信息
        where_clause = " AND ".join(conditions)  # 使用 AND 连接列表中的每一个元素
        sql = f"SELECT * FROM teacherinfo WHERE {where_clause}"
        cursor.execute(sql)
    else:
        cursor.execute(f'SELECT * FROM teacherinfo')

    # 获取查询结果
    teachers = cursor.fetchall()
    # 关闭游标
    cursor.close()
    # 如果查询结果为空，则返回 404 错误
    if not teachers:
        return jsonify({'code': 404, 'msg': '未找到任何教师信息'})

    # 返回查询结果
    return jsonify({'code': 0, "msg": "", "count": len(teachers), 'data': teachers})


# 定义添加教师信息的 API
@bp.route('/teachers', methods=['POST'])
def add_teacher():
    try:
        # 获取 POST 请求上传的数据
        tea_id = request.json['tea_id']
        name = request.json['name']
        email = request.json['email']
        telephone = request.json['telephone']

        db = get_db()
        # 创建一个 cursor 对象
        cursor = db.cursor()

        # 插入新的教师信息
        cursor.execute(f'INSERT INTO teacherinfo (tea_id, name, email, telephone) VALUES '
                       f'("{tea_id}", "{name}","{email}","{telephone}")')

        # 提交更改并关闭游标
        db.commit()
        cursor.close()

        # 返回成功信息
        return jsonify({'code': 201, 'msg': '教师添加成功'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 定义更新教师信息的 API
@bp.route('/teachers/<string:tea_id>', methods=['PUT'])
def update_teacher(tea_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 查询指定的教师信息是否存在
    cursor.execute(f'SELECT * FROM teacherinfo WHERE tea_id = "{tea_id}"')
    teacher = cursor.fetchone()

    # 如果教师信息不存在，则返回 404 错误
    if not teacher:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {tea_id} 的教师信息'})

    # 更新教师信息
    name = request.json.get('name', teacher['name'])
    email = request.json.get('email', teacher['email'])
    telephone = request.json.get('telephone', teacher['telephone'])

    cursor.execute(
        f'UPDATE teacherinfo SET name = "{name}", email = "{email}", telephone = "{telephone}" WHERE tea_id = "{tea_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'code': 200, 'msg': f'ID 为 {tea_id} 的教师信息已更新'})


# 定义删除教师信息的 API
@bp.route('/teachers/<string:tea_id>', methods=['DELETE'])
def delete_teacher(tea_id):
    try:
        db = get_db()
        # 创建一个 cursor 对象
        cursor = db.cursor()

        # 使用指定的 tea_id 查询教师信息
        cursor.execute(f'SELECT * FROM teacherinfo WHERE tea_id = "{tea_id}"')

        # 获取查询结果
        teacher = cursor.fetchone()

        # 如果查询结果为空，则返回 404 错误
        if not teacher:
            return jsonify({'code': 404, 'msg': f'未找到 ID 为 {tea_id} 的教师信息'})

        # 删除教师信息
        cursor.execute(f'DELETE FROM teacherinfo WHERE tea_id = "{tea_id}"')

        # 提交更改并关闭游标
        db.commit()
        cursor.close()

        # 返回成功信息
        return jsonify({'code': 200, 'msg': f'ID 为 {tea_id} 的教师信息已删除'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 定义获取所有课程信息的 API
@bp.route('/courses', methods=['GET'])
def get_courses():
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    course_name = request.args.get('course_name')
    # 构建 SQL 查询语句
    conditions = []
    if course_name:
        conditions.append(f"course_name = '{course_name}'")
    if conditions:
        # 有查询条件，按条件查询学生信息
        where_clause = " AND ".join(conditions)  # 使用 AND 连接列表中的每一个元素
        sql = f"SELECT A.*,B.name tea_name FROM courseinfo A INNER JOIN teacherinfo B ON A.tea_id=B.tea_id WHERE {where_clause}"
        cursor.execute(sql)
        courses = cursor.fetchall()
    else:
        # 查询所有的课程信息
        cursor.execute('SELECT A.*,B.name tea_name FROM courseinfo A INNER JOIN teacherinfo B ON A.tea_id=B.tea_id')
        # 获取查询结果
        courses = cursor.fetchall()
    # 关闭游标
    cursor.close()
    return jsonify({'code': 0, "msg": "", "count": len(courses), 'data': courses})


# 定义获取指定课程下的学生信息的 API
@bp.route('/courses/<string:course_id>/students', methods=['GET'])
def get_course(course_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 course_id 查询课程下的学生信息
    sql = f'SELECT studentinfo.stu_id, studentinfo.name FROM studentinfo' \
          f' INNER JOIN student_course ON studentinfo.stu_id = student_course.student_id' \
          f' WHERE student_course.course_id = "{course_id}"'

    cursor.execute(sql)
    # 获取查询结果
    student_info = cursor.fetchall()

    # 如果查询结果为空，则返回 404 错误
    if not student_info:
        return jsonify({'error': f'未找到 ID 为 {course_id} 的课程下的学生信息'}), 404

    # 关闭游标
    cursor.close()

    # 将查询结果转换为字典格式，并返回
    return jsonify({"student_info": student_info}), 200


# 定义添加课程信息的 API
@bp.route('/courses', methods=['POST'])
def add_course():
    # 获取 POST 请求上传的数据
    course_id = request.json['course_id']
    course_name = request.json['course_name']
    course_introduction = request.json['course_introduction']
    state = request.json['state']
    tea_id = request.json['tea_id']

    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    try:
        # 插入新的课程信息
        cursor.execute(f'INSERT INTO courseinfo (course_id, course_name, course_introduction, state, tea_id) VALUES '
                       f'("{course_id}", "{course_name}", "{course_introduction}", "{state}", "{tea_id}")')

        # 提交更改并关闭游标
        db.commit()
        cursor.close()
        # 返回成功信息
        return jsonify({'code': 201, 'msg': '课程信息添加成功'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})


# 定义更新课程信息的 API
@bp.route('/courses/<string:course_id>', methods=['PUT'])
def update_course(course_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 查询指定的课程信息是否存在
    cursor.execute(f'SELECT * FROM courseinfo WHERE course_id = "{course_id}"')
    course = cursor.fetchone()

    # 如果课程信息不存在，则返回 404 错误
    if not course:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {course_id} 的课程信息'})

    # 更新课程信息
    course_name = request.json.get('course_name', course['course_name'])
    course_introduction = request.json.get('course_introduction', course['course_introduction'])
    state = request.json.get('state', course['state'])
    tea_id = request.json.get('tea_id', course['tea_id'])

    try:
        cursor.execute(
            f'UPDATE courseinfo SET course_name = "{course_name}", course_introduction = "{course_introduction}", state = "{state}", tea_id = "{tea_id}" WHERE course_id = "{course_id}"')
        # 提交更改并关闭游标
        db.commit()
        cursor.close()
        return jsonify({'code': 200, 'msg': '课程信息添加成功'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})


# 定义删除课程信息的 API
@bp.route('/courses/<string:course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        db = get_db()
        # 创建一个 cursor 对象
        cursor = db.cursor()
        # 使用指定的 course_id 查询课程信息
        cursor.execute(f'SELECT * FROM courseinfo WHERE course_id = "{course_id}"')
        # 获取查询结果
        course = cursor.fetchone()

        # 如果查询结果为空，则返回 404 错误
        if not course:
            return jsonify({'code': 404, 'msg': f'未找到 ID 为 {course_id} 的课程信息'})

        # 先查询该课程是否有课程作业
        homeworkinfo = cursor.execute(f'SELECT * FROM homeworkinfo WHERE course_id = "{course_id}"')
        if homeworkinfo:  # 如果有通知则先删除通知表的数据
            cursor.execute(f'DELETE FROM homeworkinfo WHERE course_id = "{course_id}"')

        # 先查询该课程是否有课程通知
        course_noticeinfo = cursor.execute(f'SELECT * FROM course_noticeinfo WHERE course_id = "{course_id}"')
        if course_noticeinfo:  # 如果有通知则先删除通知表的数据
            cursor.execute(f'DELETE FROM course_noticeinfo WHERE course_id = "{course_id}"')

        student_course = cursor.execute(f'SELECT * FROM student_course WHERE course_id = "{course_id}"')
        if student_course:
            # 先删除关联表中的内容
            cursor.execute(f'DELETE FROM student_course WHERE course_id = "{course_id}"')
        # 最后删除课程信息
        cursor.execute(f'DELETE FROM courseinfo WHERE course_id = "{course_id}"')

        # 提交更改并关闭游标
        db.commit()
        cursor.close()

        # 返回成功信息
        return jsonify({'code': 200, 'msg': f'ID 为 {course_id} 的课程信息已删除'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})
