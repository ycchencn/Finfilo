"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from config import database_conn_str

# 数据库配置
DATABASE_URI = database_conn_str  # 可以修改为其他数据库URI，如postgresql或mysql
POOL_SIZE = 30  # 连接池大小
MAX_OVERFLOW = 50  # 允许的最大溢出连接数

# 创建引擎并配置连接池
engine = create_engine(
    DATABASE_URI,
    pool_size=POOL_SIZE,
    pool_recycle=3600,
    pool_pre_ping=True,
    max_overflow=MAX_OVERFLOW,
    echo=False  # 可以设置为True来调试
)

# 创建会话
db_session = scoped_session(sessionmaker(bind=engine))
