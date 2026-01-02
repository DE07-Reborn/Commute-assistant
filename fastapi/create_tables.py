"""
간단한 테이블 생성 스크립트
실행: `python create_tables.py` (fastapi 폴더에서)
주의: 환경변수로 DATABASE_URL 또는 DB 접속 정보를 설정해야 합니다
"""
from database import engine, Base, test_connection
import models

if __name__ == '__main__':
    if test_connection():
        print('테이블 생성 시작...')
        Base.metadata.create_all(bind=engine)
        print('테이블 생성 완료')
    else:
        print('데이터베이스 연결 실패. 환경변수를 확인하세요.')
