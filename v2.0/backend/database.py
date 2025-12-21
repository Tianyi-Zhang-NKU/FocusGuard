import sqlite3
# 引入哈希库，为了让密码加密存储，这样比较安全
from werkzeug.security import generate_password_hash, check_password_hash
import config

def get_conn():
    """连接数据库的辅助函数"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row  # 这样可以用列名访问数据
    return conn

def init_db():
    """第一次运行时创建表"""
    conn = get_conn()
    c = conn.cursor()

    # 记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            posture TEXT,
            fatigue REAL,
            alert INTEGER,
            username TEXT
        )
    ''')

    # 用户表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def add_log(username, time_str, posture, fatigue, alert):
    """插入一条监测记录"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute('INSERT INTO logs (time, posture, fatigue, alert, username) VALUES (?, ?, ?, ?, ?)',
                  (time_str, posture, fatigue, 1 if alert else 0, username))
        conn.commit()
        conn.close()
    except Exception as e:
        print("写入日志出错:", e)

def get_logs(username, limit=50):
    """查最近的记录给前端显示"""
    conn = get_conn()
    c = conn.cursor()
    # 按时间倒序查最近的
    c.execute('SELECT * FROM logs WHERE username = ? ORDER BY id DESC LIMIT ?', (username, limit))
    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "time": r['time'],
            "fatigue": r['fatigue'],
            "posture": r['posture']
        })
    return result[::-1]  # 翻转一下，按时间正序返回

# === 用户相关 ===

def add_user(username, password):
    """注册用户"""
    conn = get_conn()
    c = conn.cursor()
    try:
        # 把密码加密变成乱码存进去
        p_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, p_hash))
        conn.commit()
        return True, "注册成功"
    except sqlite3.IntegrityError:
        return False, "用户名已存在"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def check_login(username, password):
    """验证登录"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    # 检查密码是否匹配
    if user and check_password_hash(user['password'], password):
        return True, "登录成功"
    else:
        return False, "账号或密码错误"
