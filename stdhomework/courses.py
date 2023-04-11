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
    cursor.execute("SELECT A.*,B.course_name FROM course_noticeinfo A INNER JOIN B courseinfo "
                   "ON A.course_id=B.course_id WHERE course_id = %s", (course_id,))
    result = cursor.fetchall()
    if not result:
        return jsonify({'code': 404, 'msg': '未找到该课程下的通知'})
    return jsonify({"code": 0, 'msg': "", 'count': len(result), 'data': result})


# 向 course_notice 表中插入数据,添加课程公告
@bp.route('/course_notice', methods=['POST'])
def create_course_notice():
    # 解析请求中的 JSON 数据
    data = request.get_json()
    # print(data)
    # 从 JSON 数据中获取数据
    title = data['title']
    content = data['content']
    course_id = data['course_id']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 插入新数据
    db = get_db()
    try:
        # 创建一个 cursor 对象
        cursor = db.cursor()
        cursor.execute("INSERT INTO course_noticeinfo (title, content, create_time, course_id) VALUES (%s, %s, %s, %s)",
                       (title, content, create_time, course_id))
        db.commit()
        # 返回信息
        return jsonify({'code': 201, 'msg': '课程通知创建成功'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 根据 id 更新 course_notice 表中的数据
@bp.route('/course_notice/update', methods=['PUT'])
def update_course_notice():
    # 解析请求中的 JSON 数据
    data = request.get_json()

    # 从 JSON 数据中获取数据
    id = data['id']
    title = data['title']
    content = data['content']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    course_id = data['course_id']

    # 更新数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    try:
        result = cursor.execute("UPDATE course_noticeinfo SET title = %s, content = %s, create_time = %s WHERE id = %s",
                                (title, content, create_time, id))
        db.commit()
        if result > 0:
            # 返回信息
            return jsonify({'code': 0, 'msg': '课程通知更新成功'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()
        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 根据 id 删除 course_notice 表中的数据
@bp.route('/course_notice/delete', methods=['DELETE'])
def delete_system_notice():
    id = request.json['id']
    # 删除数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    try:
        result = cursor.execute("DELETE FROM course_noticeinfo WHERE id = %s", (id,))
        db.commit()
        if result > 0:
            # 返回信息
            return jsonify({'code': 200, 'msg': '课程通知删除成功'})
        else:
            return jsonify({'code': 400, 'msg': '该课程不存在或已被删除'})
        
    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()
        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})
