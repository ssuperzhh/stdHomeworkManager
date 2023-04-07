from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

#from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('teacher', __name__, url_prefix='/teacher')


#查看教师课程列表
@bp.route('<string:tea_id>/courses', methods=['GET'])
def get_teacher_courses(tea_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 tea_id 查询教师课表
    cursor.execute(f'SELECT courseinfo.course_id, courseinfo.course_name'
                   f' FROM courseinfo WHERE tea_id = "{tea_id}"')

    # 获取查询结果
    teacher_courses = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 如果查询结果为空，则返回 404 错误
    if not teacher_courses:
        return jsonify({'error': f'未找到 ID 为 {tea_id} 的教师的课表信息'}), 404

    # 返回查询结果
    return jsonify({'teacher_courses': teacher_courses}), 200
