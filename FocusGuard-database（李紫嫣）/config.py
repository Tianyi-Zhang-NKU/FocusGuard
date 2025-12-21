import os

# 自动获取当前文件的路径，防止路径写死找不到文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'focusguard.db')

# 算法每隔3帧跑一次，节省CPU
ALGO_SKIP_FRAMES = 3

# 数据库每隔5秒写一次，防止写太多
SAVE_INTERVAL = 5