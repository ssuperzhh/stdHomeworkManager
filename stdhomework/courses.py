from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

# from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('courses', __name__, url_prefix='/courses')


# 根据 course_id 获取 course_notice 表中的数据
@bp.route('/course_notice/<int:course_id>', methods=['GET'])
def get_course_notice_by_course_id(course_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("SELECT * FROM course_noticeinfo WHERE course_id = %s", (course_id,))
    result = cursor.fetchall()
    if not result:
        return jsonify({'error': '未找到该课程下的通知'}), 404
    return jsonify({"course_id": result}), 200


# 向 course_notice 表中插入数据,添加课程公告
@bp.route('/course_notice', methods=['POST'])
def create_course_notice():
    # 解析请求中的 JSON 数据
    data = request.get_json()
    #print(data)

    # 从 JSON 数据中获取数据
    title = data['title']
    content = data['content']
    course_id = data['course_id']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 插入新数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("INSERT INTO course_noticeinfo (title, content, create_time, course_id) VALUES (%s, %s, %s, %s)",
                   (title, content, create_time, course_id))
    db.commit()

    # 返回信息
    return jsonify({'message': '课程通知创建成功'}), 201


# 根据 id 更新 course_notice 表中的数据
@bp.route('/course_notice/<int:course_id>', methods=['PUT'])
def update_course_notice(course_id):
    # 解析请求中的 JSON 数据
    data = request.get_json()

    # 从 JSON 数据中获取数据
    title = data['title']
    content = data['content']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    course_id = data['course_id']

    # 更新数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("UPDATE course_noticeinfo SET title = %s, content = %s, create_time = %s WHERE course_id = %s",
                   (title, content, create_time, course_id))
    db.commit()

    # 返回信息
    return jsonify({'message': '课程通知更新成功'}), 200


# 根据 id 删除 system_notice 表中的数据
@bp.route('/system_notice/<int:id>', methods=['DELETE'])
def delete_system_notice(id):
    # 删除数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("DELETE FROM system_notice WHERE id = %s", (id,))
    db.commit()

    # 返回信息
    return jsonify({'message': '系统通知删除成功'}), 200
