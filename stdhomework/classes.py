from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

#from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('classes', __name__, url_prefix='/classes')


#查看班级列表
@bp.route('', methods=['GET'])
def get_classes_name():
    db = get_db()
    # 创建一个 cursor 对象
    cursor = db.cursor()

    # 使用指定的 stu_id 查询学生信息
    cursor.execute(f'SELECT distinct class_name FROM studentinfo');

    # 获取查询结果
    calss_name = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 如果查询结果为空，则返回 404 错误
    if not calss_name:
        return jsonify({'error': f'未找到 班级的信息'}), 404

    # 返回查询结果
    return jsonify(calss_name), 200
