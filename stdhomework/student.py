from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

#from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('student', __name__, url_prefix='/student')

# @bp.route('/')
# def index():
#     db = get_db()
#     # 创建一个 cursor 对象
#     cur = db.cursor()
#     # 执行 SELECT 语句
#     cur.execute("SELECT * FROM notice")
#     # 获取所有结果集
#     results = cur.fetchall()
#     return render_template('auth/index.html', notices=results)


#查看学生课程列表
@bp.route('<string:stu_id>/courses', methods=['GET'])
def get_student_courses(stu_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 stu_id 查询学生信息
    cursor.execute(f'SELECT courseinfo.course_id, courseinfo.course_name'
                   f' FROM courseinfo INNER JOIN student_course ON courseinfo.course_id = student_course.course_id '
                   f'WHERE student_course.student_id = "{stu_id}"')

    # 获取查询结果
    student_courses = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 如果查询结果为空，则返回 404 错误
    if not student_courses:
        return jsonify({'error': f'未找到 ID 为 {stu_id} 的学生的课表信息'}), 404

    # 返回查询结果
    return jsonify({'student_courses': student_courses}), 200
