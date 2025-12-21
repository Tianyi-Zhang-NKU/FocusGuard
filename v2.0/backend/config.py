import os

# 获取当前文件所在的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库文件路径
DB_PATH = os.path.join(BASE_DIR, 'focusguard.db')

# 自动保存监测记录的时间间隔（秒）
# 比如每 60 秒保存一次状态，避免数据库爆炸
SAVE_INTERVAL = 60
