from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

#from stdhomework.auth import login_required
from stdhomework.db import get_db

bp = Blueprint('student', __name__)

@bp.route('/')
def index():
    db = get_db()
    # 创建一个 cursor 对象
    cur = db.cursor()
    # 执行 SELECT 语句
    cur.execute("SELECT * FROM notice")
    # 获取所有结果集
    results = cur.fetchall()
    return render_template('auth/index.html', notices=results)
