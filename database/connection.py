"""
Database connection module
"""

import os
import logging
from typing import Optional
import pymysql
from contextlib import contextmanager

logger = logging.getLogger("database.connection")

class DatabaseConnection:
    """MySQL 데이터베이스 연결 클래스"""
    
    def __init__(self):
        self.connection = None
        self.database_url = os.getenv("DATABASE_URL", "mysql://root@localhost:3306/plandy")
    
    def connect(self):
        """데이터베이스에 연결합니다."""
        try:
            # DATABASE_URL 파싱: mysql://root@localhost:3306/plandy
            if self.database_url.startswith("mysql://"):
                url_parts = self.database_url[8:]  # mysql:// 제거
                
                # 사용자명@호스트:포트/데이터베이스명 파싱
                if "@" in url_parts:
                    user_part, host_db_part = url_parts.split("@", 1)
                    username = user_part
                else:
                    username = "root"
                    host_db_part = url_parts
                
                if "/" in host_db_part:
                    host_port_part, database = host_db_part.split("/", 1)
                else:
                    host_port_part = host_db_part
                    database = "plandy"
                
                if ":" in host_port_part:
                    host, port = host_port_part.split(":", 1)
                    port = int(port)
                else:
                    host = host_port_part
                    port = 3306
                
                self.connection = pymysql.connect(
                    host=host,
                    port=port,
                    user=username,
                    password="",  # 비밀번호가 없음
                    database=database,
                    charset='utf8mb4',
                    autocommit=True
                )
                
                logger.info(f"MySQL 데이터베이스에 연결되었습니다: {host}:{port}/{database}")
                return True
                
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {str(e)}")
            return False
    
    def close(self):
        """데이터베이스 연결을 닫습니다."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("데이터베이스 연결이 닫혔습니다.")
    
    def get_connection(self):
        """데이터베이스 연결을 반환합니다."""
        if not self.connection or not self.connection.open:
            self.connect()
        return self.connection

# 전역 데이터베이스 연결 인스턴스
_db_connection = DatabaseConnection()

def get_db_connection():
    """데이터베이스 연결을 반환합니다."""
    return _db_connection.get_connection()

def close_db_connection():
    """데이터베이스 연결을 닫습니다."""
    _db_connection.close()

@contextmanager
def get_db_cursor():
    """데이터베이스 커서를 컨텍스트 매니저로 제공합니다."""
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    try:
        yield cursor
    finally:
        cursor.close()
