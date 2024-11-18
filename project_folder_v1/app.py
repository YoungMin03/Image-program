# app.py
# 설명: Flask 기반 메인 애플리케이션 파일
from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from utils.exif_handler import ExifHandler
import logging

# Flask 앱 초기화
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 상수 정의
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# uploads 폴더가 없으면 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.debug("Upload request received")
        
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '파일이 없습니다.'
            }), 400
        
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        logger.debug(f"File saved: {file_path}")

        # EXIF 데이터 처리
        exif_data = ExifHandler.get_exif_data(file_path)
        
        # EXIF 데이터가 있는 경우에만 GPS와 시간 정보 추출 시도
        coordinates = None
        datetime_info = None
        if exif_data:
            coordinates = ExifHandler.get_gps_coordinates(exif_data)
            datetime_info = ExifHandler.get_datetime(exif_data)

        # 위치 정보만 없는 경우
        if not coordinates and datetime_info:
            return jsonify({
                'status': 'warning',
                'message': '이미지에 위치 정보가 없습니다.',
                'data': {
                    'filename': filename,
                    'has_location': False,
                    'has_datetime': True,
                    'datetime': datetime_info.strftime('%Y-%m-%d %H:%M:%S')
                }
            })

        # 시간 정보만 없는 경우
        if coordinates and not datetime_info:
            return jsonify({
                'status': 'warning',
                'message': '이미지에 시간 정보가 없습니다.',
                'data': {
                    'filename': filename,
                    'has_location': True,
                    'coordinates': coordinates,
                    'has_datetime': False
                }
            })

        # 위치와 시간 정보가 모두 있는 경우
        if coordinates and datetime_info:
            return jsonify({
                'status': 'success',
                'message': '파일이 성공적으로 업로드되었습니다.',
                'data': {
                    'filename': filename,
                    'has_location': True,
                    'coordinates': coordinates,
                    'has_datetime': True,
                    'datetime': datetime_info.strftime('%Y-%m-%d %H:%M:%S')
                }
            })

        # 위치와 시간 정보가 모두 없는 경우
        return jsonify({
            'status': 'warning',
            'message': '이미지에 위치와 시간 정보가 모두 없습니다.',
            'data': {
                'filename': filename,
                'has_location': False,
                'has_datetime': False
            }
        })

    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': '파일 처리 중 오류가 발생했습니다.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)