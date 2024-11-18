import subprocess
import sys
import os

def install_required_packages():
    """필요한 패키지 설치"""
    required_packages = ['flask', 'Pillow', 'werkzeug']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"{package} 이미 설치되어 있습니다.")
        except ImportError:
            print(f"{package} 패키지를 설치합니다...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"{package} 설치 완료!")

# 패키지 설치 실행
print("필요한 패키지 확인 및 설치 중...")
install_required_packages()

# 이후 필요한 모듈 임포트
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from image_processor import ImageProcessor

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

# 업로드 설정
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 필요한 디렉토리 생성
for directory in ['templates', 'static/css', 'static/js', 'uploads']:
    dir_path = os.path.join(BASE_DIR, directory)
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            print(f"디렉토리 생성됨: {dir_path}")
        except Exception as e:
            print(f"디렉토리 생성 실패: {dir_path} - {str(e)}")

def allowed_file(filename):
    """허용된 파일 확장자 검사"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename_with_hangul(filename):
    """한글 파일명을 안전하게 처리하는 함수"""
    name, ext = os.path.splitext(filename)
    name = name.replace('/', '_').replace('\\', '_')
    ext = ext.lower()
    return f"{name}{ext}"

@app.route('/')
def index():
    return render_template('index.html')

# 이미지 제공을 위한 라우트 추가
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': '파일이 없습니다.'})
    
    files = request.files.getlist('files[]')
    results = []
    
    for file in files:
        if file.filename == '':
            continue
            
        try:
            original_filename = file.filename
            safe_filename = secure_filename_with_hangul(original_filename)
            final_filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            
            # 파일 중복 검사
            if os.path.exists(final_filepath):
                results.append({
                    'original_filename': original_filename,
                    'error': '이미 업로드된 이미지입니다.'
                })
                continue
            
            # 파일 크기 검사
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                results.append({
                    'original_filename': original_filename,
                    'error': f'파일 크기가 너무 큽니다. 최대 {MAX_FILE_SIZE/1024/1024:.1f}MB까지 가능합니다.'
                })
                continue
                
            if not allowed_file(original_filename):
                results.append({
                    'original_filename': original_filename,
                    'error': '지원하지 않는 파일 형식입니다.'
                })
                continue
            
            # 파일 저장
            file.save(final_filepath)
            
            # 메타데이터 추출
            processor = ImageProcessor()
            metadata = processor.extract_metadata(final_filepath)
            
            # 메타데이터 검사
            missing_data = []
            if not metadata.get('촬영시간'):
                missing_data.append('시간')
            if not metadata.get('위도') or not metadata.get('경도'):
                missing_data.append('위치')
            
            if missing_data:
                # 메타데이터가 없는 경우 파일 삭제
                os.remove(final_filepath)
                error_message = f"{'와 '.join(missing_data)} 정보가 없는 이미지입니다."
                results.append({
                    'original_filename': original_filename,
                    'error': error_message
                })
                continue
            
            results.append({
                'original_filename': original_filename,
                'saved_filename': safe_filename,
                'metadata': metadata
            })
            
        except Exception as e:
            results.append({
                'original_filename': original_filename,
                'error': '파일 처리 중 오류가 발생했습니다.'
            })
    
    return jsonify(results)

if __name__ == '__main__':
    print(f"업로드 폴더 경로: {UPLOAD_FOLDER}")
    app.run(debug=True)