from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

# from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('student', __name__, url_prefix='/student')


# 查看学生课程列表
@bp.route('<string:stu_name>/courses', methods=['GET'])
def get_student_courses(stu_name):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    course_name = request.args.get('course_name')
    sql = (f'SELECT A.*, B.name tea_name '
           f'FROM courseinfo A '
           f'INNER JOIN teacherinfo B ON A.tea_id = B.tea_id '
           f'INNER JOIN student_course C ON A.course_id = C.course_id '
           f'INNER JOIN studentinfo D ON D.stu_id = C.student_id '
           f'WHERE D.name = "{stu_name}"')
    # 构建 SQL 查询语句
    conditions = []
    if course_name:
        conditions.append(f"course_name = '{course_name}'")
    if conditions:
        where_clause = " AND ".join(conditions)  # 使用 AND 连接列表中的每一个元素
        sql += f" AND {where_clause}"
        cursor.execute(sql)
        student_courses = cursor.fetchall()
    else:
        cursor.execute(sql)
        student_courses = cursor.fetchall()
    # 关闭游标
    cursor.close()

    # 没有查询到任何学生记录，返回 404 错误响应
    if len(student_courses) == 0:
        return jsonify({'code': 404, 'msg': '未找到该学生下的课表信息'})

    # 返回查询结果
    return jsonify({'code': 0, "msg": "", "count": len(student_courses), 'data': student_courses})


# 学生选课
@bp.route('courses/choose', methods=['POST'])
def choose_course():
    db = get_db()
    cursor = db.cursor()
    stu_id = request.json['stu_id']
    course_id = request.json['course_id']
    try:
        if stu_id and course_id:
            cursor.execute(f'INSERT INTO student_course(course_id,student_id) VALUES ({course_id},"{stu_id}")')
            db.commit()
            cursor.close()
            return jsonify({'code': 201, 'msg': f'添加成功'})
        else:
            return jsonify({'code': 500, 'msg': f'学号或课程号为空，无法添加'})
    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()
        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 学生退选课
@bp.route('courses/unchoose', methods=['DELETE'])
def unChoose_course():
    db = get_db()
    cursor = db.cursor()
    stu_id = request.json['stu_id']
    course_id = request.json['course_id']
    try:
        if stu_id and course_id:
            cursor.execute(f'DELETE FROM student_course WHERE student_id="{stu_id}" AND course_id={course_id}')
            db.commit()
            cursor.close()
            return jsonify({'code': 201, 'msg': f'退选成功'})
        else:
            return jsonify({'code': 500, 'msg': f'您未选这门课'})
    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()
        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 查看学生课程作业列表
@bp.route('<string:stu_id>/courses/<int:course_id>/homeworks', methods=['GET'])
def get_student_courses_homeworks(stu_id, course_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    sql = (f"SELECT A.*, C.course_name, D.name student_name, D.class_name"
           f" FROM homeworkinfo A"
           f" INNER JOIN student_course B ON B.course_id = A.course_id"
           f" INNER JOIN courseinfo C ON C.course_id = B.course_id"
           f" INNER JOIN studentinfo D ON D.stu_id = B.student_id"
           f" WHERE C.course_id = {course_id} AND D.stu_id = '{stu_id}'")

    cursor.execute(sql)

    # 获取查询结果
    student_courses_homeworks = cursor.fetchall()
    # 关闭游标
    cursor.close()

    # 如果查询结果为空，则返回 404 错误
    if not student_courses_homeworks:
        return jsonify({'error': f'未找到该学生的这门课的作业信息'}), 404

    # 返回查询结果
    return jsonify({'student_courses_homeworks': student_courses_homeworks}), 200


# 定义更新学生密码
@bp.route('/update_pwd/<string:stu_id>', methods=['PUT'])
def update_student(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    cursor.execute(f'SELECT * FROM user WHERE id = "{stu_id}"')
    student = cursor.fetchone()

    # 如果学生信息不存在，则返回 404 错误
    if not student:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {stu_id} 的信息'})

    # 更新学生信息
    new_password = request.json.get('new_password', student['name'])
    cursor.execute(
        f'UPDATE user SET password = "{new_password}" WHERE stu_id = "{stu_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'code': 200, 'msg': f'ID 为 {stu_id} 的密码已更新'})
