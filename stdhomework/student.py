from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

# from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('student', __name__, url_prefix='/student')


# 查看学生课程列表
@bp.route('<string:stu_id>/courses', methods=['GET'])
def get_student_courses(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 stu_id 查询学生信息
    cursor.execute(f'SELECT A.course_id, A.course_name, B.name tea_name '
                   f'FROM courseinfo A '
                   f'INNER JOIN teacherinfo B ON A.tea_id = B.tea_id '
                   f'INNER JOIN student_course C ON A.course_id = C.course_id '
                   f'WHERE C.student_id = "{stu_id}"')

    # 获取查询结果
    student_courses = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 没有查询到任何学生记录，返回 404 错误响应
    if len(student_courses) == 0:
        return jsonify({'code': 404, 'msg': '未找到该学生下的课表信息'})

    # 返回查询结果
    return jsonify({'code': 0, "msg": "", "count": len(student_courses), 'data': student_courses})


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
