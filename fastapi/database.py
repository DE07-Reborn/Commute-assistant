"""
데이터베이스 연결 및 세션 관리
도커 네트워크에서 PostgreSQL에 연결
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os

# 환경 변수에서 데이터베이스 연결 정보 가져오기
# 도커 네트워크에서 PostgreSQL 컨테이너 이름은 일반적으로 'postgres' 또는 서비스 이름
DB_HOST = os.getenv('APP_DB_HOST', 'postgres')
DB_PORT = os.getenv('APP_DB_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'commute_db')
DB_USER = os.getenv('POSTGRES_USER', 'commute_user')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'commute_password')

# DATABASE_URL이 직접 설정되어 있으면 사용, 없으면 환경 변수로 구성
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

print(f"데이터베이스 연결 시도: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# SQLAlchemy 엔진 생성
# pool_pre_ping=True: 연결이 끊어졌을 때 자동으로 재연결 시도
# echo=True: SQL 쿼리 로깅 (디버깅용, 프로덕션에서는 False)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False  # SQL 쿼리 로깅 (필요시 True로 변경)
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()


# 데이터베이스 연결 테스트
def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ PostgreSQL 데이터베이스 연결 성공")
            return True
    except OperationalError as e:
        print(f"❌ PostgreSQL 데이터베이스 연결 실패: {e}")
        print(f"   연결 정보: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        print("   도커 네트워크에서 PostgreSQL 컨테이너가 실행 중인지 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ 데이터베이스 연결 오류: {e}")
        return False


# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


