from flask import Flask, request, jsonify, render_template
import os
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
MAX_FILE_SIZE = 5 * 1024 * 1024  # 10MB

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

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': '파일이 없습니다.'})
    
    files = request.files.getlist('files[]')
    results = []
    
    for file in files:
        if file.filename == '':
            continue
            
        # 파일 크기 검사 (10MB 제한)
        file.seek(0, 2)  # 파일 끝으로 이동
        file_size = file.tell()  # 현재 위치(파일 크기) 확인
        file.seek(0)  # 파일 포인터를 다시 처음으로
        
        if file_size > MAX_FILE_SIZE:
            results.append({
                'original_filename': file.filename,
                'error': f'파일 크기가 너무 큽니다. 최대 {MAX_FILE_SIZE/1024/1024:.1f}MB까지 가능합니다.'
            })
            continue
            
        if not allowed_file(file.filename):
            results.append({
                'original_filename': file.filename,
                'error': '지원하지 않는 파일 형식입니다.'
            })
            continue
        
        try:
            original_filename = file.filename
            safe_filename = secure_filename_with_hangul(original_filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            
            file.save(filepath)
            
            if not os.path.exists(filepath):
                raise Exception("파일이 정상적으로 저장되지 않았습니다.")
            
            processor = ImageProcessor()
            metadata = processor.extract_metadata(filepath)
            
            results.append({
                'original_filename': original_filename,
                'saved_filename': safe_filename,
                'metadata': metadata
            })
            
        except Exception as e:
            results.append({
                'original_filename': original_filename,
                'error': f'파일 처리 중 오류 발생: {str(e)}'
            })
    
    return jsonify(results)

if __name__ == '__main__':
    print(f"업로드 폴더 경로: {UPLOAD_FOLDER}")
    app.run(debug=True)