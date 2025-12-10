# Commute-assistant



## 실행전 .env 파일 설정 (Root Directory)
프로젝트 **최상위 루트 디렉토리**에 반드시 `.env` 파일을 생성해주세요.
- 포함 내용은 `env.example`을 참고해주세요.
- 작성 후 Linux, WSL, Git Bash 환경에서 최초 1회 실행 권한을 부여해야 합니다.
```bash
chmod +x scripts/docker-compose-up.sh
```

## 도커 실행
프로젝트는 **Docker 기반 프로그램**이므로
**Docker Desktop**가 설치되어 있고 실행 중인 상태여야 합니다.

### 실행
스크립트 폴더 내부의 `docker-compose-up.sh` 파일을 실행하면 됩니다.
```bash
cd scripts
bash docker-compose-up.sh
```