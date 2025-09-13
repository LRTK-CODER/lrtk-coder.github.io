#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
보안 배포 관리 API 서버
Jekyll 빌드 → GitHub Pages 저장소 동기화 → Git 푸시 자동화
API 키 기반 보안 인증 포함
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import logging
import secrets
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 경로 설정
JEKYLL_SOURCE = os.path.abspath('.')
JEKYLL_SITE = os.path.join(JEKYLL_SOURCE, '_site')
GITHUB_PAGES_REPO = os.path.abspath('../lrtk-coder.github.io')

# 보안 설정
API_KEY_FILE = '.deploy_api_key'
DEPLOY_STATUS_FILE = 'deploy_status.json'

def generate_api_key():
    """API 키 생성"""
    return secrets.token_urlsafe(32)

def load_or_create_api_key():
    """API 키 로드 또는 생성"""
    try:
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as f:
                api_key = f.read().strip()
                if api_key:
                    logger.info("🔑 기존 API 키 로드됨")
                    return api_key

        # 새 API 키 생성
        api_key = generate_api_key()
        with open(API_KEY_FILE, 'w') as f:
            f.write(api_key)

        # 파일 권한 설정 (읽기 전용)
        os.chmod(API_KEY_FILE, 0o600)

        logger.info("🔑 새 API 키 생성됨")
        return api_key

    except Exception as e:
        logger.error(f"API 키 처리 실패: {e}")
        raise

# API 키 초기화
API_KEY = load_or_create_api_key()

def require_api_key(f):
    """API 키 검증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authorization 헤더에서 키 확인
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            provided_key = auth_header[7:]  # 'Bearer ' 제거
        else:
            # JSON 요청에서 키 확인
            provided_key = request.json.get('api_key') if request.json else None

        if not provided_key or provided_key != API_KEY:
            logger.warning(f"🚨 인증 실패 - IP: {request.remote_addr}")
            return jsonify({
                'success': False,
                'message': 'API 키가 유효하지 않습니다'
            }), 401

        return f(*args, **kwargs)

    return decorated_function

def get_deploy_status():
    """배포 상태 정보 읽기"""
    try:
        if os.path.exists(DEPLOY_STATUS_FILE):
            with open(DEPLOY_STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"배포 상태 읽기 실패: {e}")

    return {
        'last_deploy': None,
        'deploy_count': 0,
        'last_status': 'none',
        'last_message': '아직 배포된 적 없음'
    }

def save_deploy_status(status):
    """배포 상태 정보 저장"""
    try:
        with open(DEPLOY_STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"배포 상태 저장 실패: {e}")

@app.route('/deploy', methods=['POST'])
@require_api_key
def deploy():
    """보안 배포 엔드포인트"""
    logger.info("🚀 보안 배포 프로세스 시작")

    try:
        # 1. 디렉토리 존재 확인
        if not os.path.exists(GITHUB_PAGES_REPO):
            error_msg = f"GitHub Pages 저장소를 찾을 수 없습니다: {GITHUB_PAGES_REPO}"
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg,
                'step': 'repo_check'
            }), 500

        # 2. Jekyll 빌드
        logger.info("1️⃣ Jekyll 빌드 시작...")
        build_result = subprocess.run(
            ['bundle', 'exec', 'jekyll', 'build'],
            cwd=JEKYLL_SOURCE,
            capture_output=True,
            text=True,
            timeout=120
        )

        if build_result.returncode != 0:
            error_msg = f"Jekyll 빌드 실패: {build_result.stderr}"
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg,
                'step': 'jekyll_build'
            }), 500

        logger.info("✅ Jekyll 빌드 완료")

        # 3. rsync로 파일 동기화 (.git 폴더 보호)
        logger.info("2️⃣ rsync로 파일 동기화 시작...")
        rsync_result = subprocess.run([
            'rsync', '-av', '--delete',
            '--exclude=admin/',           # admin 디렉토리 제외
            '--exclude=.deploy_api_key',  # API 키 파일 제외
            '--exclude=deploy.log',       # 로그 파일 제외
            '--exclude=deploy_status.json',  # 상태 파일 제외
            '--exclude=.git/',            # .git 폴더 보호
            f'{JEKYLL_SITE}/',  # 소스 (끝에 / 중요!)
            f'{GITHUB_PAGES_REPO}/'  # 대상
        ], capture_output=True, text=True, timeout=60)

        if rsync_result.returncode != 0:
            error_msg = f"rsync 실패: {rsync_result.stderr}"
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg,
                'step': 'rsync'
            }), 500

        logger.info("✅ rsync 동기화 완료")

        # 4. Git 작업 (GitHub Pages 저장소에서)
        logger.info("3️⃣ Git 작업 시작...")

        # Git add
        add_result = subprocess.run(
            ['git', 'add', '.'],
            cwd=GITHUB_PAGES_REPO,
            capture_output=True,
            text=True
        )

        if add_result.returncode != 0:
            error_msg = f"Git add 실패: {add_result.stderr}"
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg,
                'step': 'git_add'
            }), 500

        # Git commit
        commit_msg = f"🚀 Auto deploy - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        commit_result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=GITHUB_PAGES_REPO,
            capture_output=True,
            text=True
        )

        # 변경사항이 없으면 커밋 실패는 정상
        if commit_result.returncode != 0:
            if 'nothing to commit' in commit_result.stdout:
                logger.info("📝 변경사항 없음 - 커밋 건너뜀")
            else:
                error_msg = f"Git commit 실패: {commit_result.stderr}"
                logger.error(error_msg)
                return jsonify({
                    'success': False,
                    'message': error_msg,
                    'step': 'git_commit'
                }), 500

        # Git push
        push_result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            cwd=GITHUB_PAGES_REPO,
            capture_output=True,
            text=True,
            timeout=30
        )

        if push_result.returncode != 0:
            error_msg = f"Git push 실패: {push_result.stderr}"
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg,
                'step': 'git_push'
            }), 500

        logger.info("✅ Git 작업 완료")

        # 5. 배포 상태 업데이트
        status = get_deploy_status()
        status['last_deploy'] = datetime.now().isoformat()
        status['deploy_count'] += 1
        status['last_status'] = 'success'
        status['last_message'] = '배포 성공'
        save_deploy_status(status)

        logger.info("🎉 배포 프로세스 완료!")

        return jsonify({
            'success': True,
            'message': f'🚀 배포 완료! (총 {status["deploy_count"]}회)',
            'timestamp': status['last_deploy'],
            'count': status['deploy_count']
        })

    except subprocess.TimeoutExpired:
        error_msg = "배포 작업이 시간 초과되었습니다"
        logger.error(error_msg)

        # 실패 상태 저장
        status = get_deploy_status()
        status['last_status'] = 'failed'
        status['last_message'] = error_msg
        save_deploy_status(status)

        return jsonify({
            'success': False,
            'message': error_msg,
            'step': 'timeout'
        }), 500

    except Exception as e:
        error_msg = f"배포 중 오류 발생: {str(e)}"
        logger.error(error_msg)

        # 실패 상태 저장
        status = get_deploy_status()
        status['last_status'] = 'failed'
        status['last_message'] = error_msg
        save_deploy_status(status)

        return jsonify({
            'success': False,
            'message': error_msg,
            'step': 'unknown'
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """배포 상태 조회 (인증 불필요)"""
    status = get_deploy_status()
    return jsonify(status)

@app.route('/api-key', methods=['GET'])
def get_api_key():
    """API 키 조회 (로컬 접근만)"""
    if request.remote_addr != '127.0.0.1':
        return jsonify({'error': '로컬 접근만 허용'}), 403

    return jsonify({'api_key': API_KEY})

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    logger.info("🚀 보안 배포 서버 시작 중...")
    logger.info(f"Jekyll 소스: {JEKYLL_SOURCE}")
    logger.info(f"Jekyll 빌드: {JEKYLL_SITE}")
    logger.info(f"GitHub Pages: {GITHUB_PAGES_REPO}")
    logger.info(f"🔑 API 키 파일: {API_KEY_FILE}")

    # Flask 앱 실행
    app.run(
        host='localhost',
        port=5000,
        debug=False  # 보안상 debug 모드 비활성화
    )