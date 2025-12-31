"""
인증 관련 유틸리티
"""
import bcrypt


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )


