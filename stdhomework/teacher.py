from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

# from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('teacher', __name__, url_prefix='/teacher')


# 查看教师课程列表
@bp.route('<string:tea_id>/courses', methods=['GET'])
def get_teacher_courses(tea_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 tea_id 查询教师课表
    cursor.execute(f'SELECT courseinfo.*'
                   f' FROM courseinfo WHERE tea_id = "{tea_id}"')

    # 获取查询结果
    teacher_courses = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 如果查询结果为空，则返回 404 错误
    if not teacher_courses:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {tea_id} 的教师的课表信息'})

    # 返回查询结果
    return jsonify({'code': 0, 'data': teacher_courses, 'msg': ""})


# 更新密码
@bp.route('/update_pwd/<string:tea_id>', methods=['PUT'])
def update_teacher(tea_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    cursor.execute(f'SELECT * FROM user WHERE identity_id = "{tea_id}"')
    student = cursor.fetchone()

    if not student:
        return jsonify({'code': 404, 'msg': f'未找到 ID 为 {tea_id} 的信息'})

    # 更新学生信息
    new_password = request.json.get('new_password', student['name'])
    cursor.execute(
        f'UPDATE user SET password = "{new_password}" WHERE identity_id = "{tea_id}"')

    # 提交更改并关闭游标
    db.commit()
    cursor.close()

    # 返回成功信息
    return jsonify({'code': 200, 'msg': f'ID 为 {tea_id} 的密码已更新'})
