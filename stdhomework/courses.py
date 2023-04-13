import os
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, current_app, send_file, json
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

# from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('courses', __name__, url_prefix='/courses')


# 根据 course_id 获取 course_notice 表中的数据
@bp.route('/course_notice/<int:course_id>', methods=['GET'])
def get_course_notice_by_course_id(course_id):
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    cursor.execute("SELECT A.*,B.course_name FROM course_noticeinfo A INNER JOIN courseinfo B "
                   "ON A.course_id=B.course_id WHERE A.course_id = %s", (course_id,))
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
            return jsonify({'code': 200, 'msg': '课程通知更新成功'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()
        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 根据 id 删除 course_notice 表中的数据
@bp.route('/course_notice/delete', methods=['DELETE'])
def delete_course_notice_notice():
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


# 获取当前课程下的作业
@bp.route('/homeworks/<int:course_id>', methods=['GET'])
def get_course_homeworks(course_id):
    db = get_db()
    try:
        sql = f'SELECT * FROM homeworkinfo WHERE course_id = "{course_id}"'
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        result = cursor.fetchall()
        if not result:
            return jsonify({'code': 404, 'msg': '未找到该课程下的作业'})
        return jsonify({"code": 0, 'msg': "", 'count': len(result), 'data': result})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 添加课程作业
@bp.route('/homeworks', methods=['POST'])
def create_course_homeworks():
    data = request.get_json()
    homework_id = data['homework_id']
    homework_name = data['homework_name']
    type = data['type']
    course_id = data['course_id']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 插入新数据
    db = get_db()
    try:
        # 创建一个 cursor 对象
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO homeworkinfo (homework_id, homework_name, date, type, course_id) "
                       f"VALUES ({homework_id}, '{homework_name}', '{create_time}', '{type}', {course_id})")
        db.commit()
        # 返回信息
        return jsonify({'code': 201, 'msg': '课程作业创建成功'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 编辑课程作业
@bp.route('/homeworks/update', methods=['PUT'])
def update_course_homeworks():
    data = request.get_json()
    homework_id = data['homework_id']
    homework_name = data['homework_name']
    type = data['type']
    course_id = data['course_id']
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 更新数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    try:
        result = cursor.execute(
            "UPDATE homeworkinfo SET homework_name = %s, type = %s, date = %s WHERE homework_id = %s",
            (homework_name, type, create_time, homework_id))
        db.commit()
        if result > 0:
            # 返回信息
            return jsonify({'code': 200, 'msg': '课程作业更新成功'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()
        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 删除某课程的作业
@bp.route('/homeworks/delete', methods=['DELETE'])
def delete_course_homeworks():
    homework_id = request.json['homework_id']
    # 删除数据
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()
    try:
        result = cursor.execute(f"DELETE FROM homeworkinfo WHERE homework_id = '{homework_id}'")
        db.commit()
        if result > 0:
            # 返回信息
            return jsonify({'code': 200, 'msg': '课程作业删除成功'})
        else:
            return jsonify({'code': 400, 'msg': '该课程作业不存在或已被删除'})

    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()
        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# 创建允许上传的文件类型的集合
ALLOWED_EXTENSIONS = {'txt', 'xls', 'xlsx', 'xlsm', 'xlsb'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods=['POST'])  # 中文文件上传尚未解决
def file_upload():
    # 检查上传的文件是否存在
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': 'No file found'}), 400
    file = request.files['file']
    # 检查上传的文件名是否合法
    if file.filename == '':
        return jsonify({'code': 400, 'msg': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'msg': 'Invalid file type'}), 400
    # 保存文件
    filename = secure_filename(file.filename)
    file_url = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    #file.save(file_url)  # 文件上传
    return jsonify({'code': 200, 'msg': 'File uploaded successfully'}), 200

@bp.route('/upload/add', methods=['POST'])  # 中文文件上传尚未解决
def file_upload_add():
    # 检查上传的文件是否存在
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': 'No file found'}), 400
    file = request.files['file']
    # 检查上传的文件名是否合法
    if file.filename == '':
        return jsonify({'code': 400, 'msg': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'msg': 'Invalid file type'}), 400
    # 保存文件
    filename = secure_filename(file.filename)
    file_url = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_url)  # 文件上传
    # 获取表单中的参数
    form_data = request.form.get('form_data')
    form_data = json.loads(form_data)

    # 获取表单中的普通字段参数
    homework_id = form_data.get('homework_id')
    homework_name = form_data.get('homework_name')
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    type = form_data.get('type')
    course_id = form_data.get('course_id')
    # 插入新数据
    db = get_db()
    try:
        # 创建一个 cursor 对象
        cursor = db.cursor()
        # 先添加作业
        cursor.execute(f"INSERT INTO homeworkinfo (homework_id, homework_name, date, type, course_id) "
                       f"VALUES ({homework_id}, '{homework_name}', '{create_time}', '{type}', {course_id})")
        # 再添加文件
        cursor.execute(f"INSERT INTO fileInfo (url, file_name, type, homework_id) "
                       f"VALUES ('{file_url}', '{filename}','{1}', {homework_id})",
                       )
        db.commit()
        cursor.close()
        return jsonify({'code': 200, 'msg': 'File uploaded successfully'}), 200
    except Exception as e:
        # 如果出现异常，回滚并关闭游标
        db.rollback()
        cursor.close()

        # 返回错误信息
        return jsonify({'code': 500, 'msg': str(e)})


# # 处理文件下载请求
@bp.route('/download/<filename>', methods=['GET'])
def file_download(filename):
    # 检查上传的文件名是否存在
    file_path = os.path.abspath(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    if not os.path.exists(file_path):
        return jsonify({'code': 404, 'msg': 'File not found'}), 404
    # 向浏览器发送文件
    return send_file(file_path, as_attachment=True)
