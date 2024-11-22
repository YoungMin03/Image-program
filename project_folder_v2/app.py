import subprocess
import sys
import os
import shutil
import re

def install_required_packages():
    """필요한 패키지 설치"""
    required_packages = ['flask', 'Pillow', 'werkzeug', 'folium']
    
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
import folium

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)

# 업로드 설정
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGES = 5  # 최대 이미지 수 설정

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def initialize_folders():
    """필요한 폴더 초기화"""
    # uploads 폴더 초기화
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
        print(f"기존 uploads 폴더 삭제됨: {UPLOAD_FOLDER}")
    
    # 필요한 디렉토리 생성
    for directory in ['uploads']:
        dir_path = os.path.join(BASE_DIR, directory)
        try:
            os.makedirs(dir_path, exist_ok=True)
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

def convert_datetime_to_filename(datetime_str):
    """촬영시간을 파일명 형식으로 변환"""
    match = re.match(r'^(\d{4}):(\d{2}):(\d{2}) (\d{2}):(\d{2}):(\d{2})$', datetime_str)
    if match:
        year, month, day, hour, minute, second = match.groups()
        # YY/MM/DD_HHMMSS 형식으로 변환
        filename = f'{year}{month}{day}_{hour}{minute}{second}'
        return filename
    return None

@app.route('/get_settings')
def get_settings():
    # 현재 업로드된 이미지 수 계산
    current_images = len([f for f in os.listdir(UPLOAD_FOLDER) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    return jsonify({
        'max_images': MAX_IMAGES,
        'max_file_size': MAX_FILE_SIZE,
        'current_images': current_images
    })

@app.route('/map')
def show_map():
    try:
        # 업로드된 이미지들의 메타데이터 수집
        locations = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                processor = ImageProcessor()
                metadata = processor.extract_metadata(filepath)
                
                if metadata and '위도' in metadata and '경도' in metadata:
                    locations.append({
                        'filename': filename,
                        'lat': float(metadata['위도']),
                        'lng': float(metadata['경도']),
                        'time': metadata.get('촬영시간', '')
                    })
        
        # 시간순 정렬
        locations.sort(key=lambda x: x['time'])
        
        # 지도 생성
        m = folium.Map(
            location=[37.5665, 126.9780] if not locations else [locations[0]['lat'], locations[0]['lng']],
            zoom_start=12
        )
        
        # 마커와 경로 추가
        points = []
        for loc in locations:
            # 팝업 내용 생성
            popup_content = f"""
                <div style="width:200px">
                    <img src="/uploads/{loc['filename']}" style="width:100%;border-radius:4px;margin-bottom:8px">
                    <div style="font-size:12px;color:#666;">
                        <p style="margin:4px 0">촬영시간: {loc['time']}</p>
                        <p style="margin:4px 0">위도: {loc['lat']}</p>
                        <p style="margin:4px 0">경도: {loc['lng']}</p>
                    </div>
                </div>
            """
            
            # 마커 추가
            folium.Marker(
                [loc['lat'], loc['lng']],
                popup=folium.Popup(popup_content, max_width=250),
                icon=folium.Icon(color='red')
            ).add_to(m)
            
            points.append([loc['lat'], loc['lng']])
        
        # 경로 선 그리기
        if len(points) > 1:
            folium.PolyLine(
                points,
                weight=2,
                color='blue',
                opacity=0.8
            ).add_to(m)
        
        # 돌아가기 버튼이 있는 지도 HTML 생성
        map_html = m._repr_html_()
        return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .back-button {{
                        position: absolute;
                        top: 20px;
                        right: 20px;
                        z-index: 1000;
                        background-color: white;
                        padding: 10px 20px;
                        border-radius: 4px;
                        text-decoration: none;
                        color: #333;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        font-family: Arial, sans-serif;
                    }}
                    .back-button:hover {{
                        background-color: #f0f0f0;
                    }}
                </style>
            </head>
            <body>
                <a href="/" class="back-button">메인 페이지로 돌아가기</a>
                {map_html}
            </body>
            </html>
        """
            
    except Exception as e:
        return f"지도 생성 중 오류 발생: {str(e)}"

@app.route('/')
def index():
    # uploads 폴더 초기화
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
        print(f"기존 uploads 폴더 삭제됨: {UPLOAD_FOLDER}")
    
    # uploads 폴더 새로 생성
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        print(f"uploads 폴더 생성됨: {UPLOAD_FOLDER}")
    except Exception as e:
        print(f"uploads 폴더 생성 실패: {str(e)}")

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({
                'success': True,
                'message': '이미지가 삭제되었습니다.',
                'filename': filename
            })
        return jsonify({
            'success': False,
            'error': '파일을 찾을 수 없습니다.',
            'filename': filename
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'파일 삭제 중 오류가 발생했습니다: {str(e)}',
            'filename': filename
        }), 500

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
            # 임시로 파일 저장
            temp_filename = secure_filename_with_hangul(original_filename)
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            
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
            
            # 파일 형식 검사
            if not allowed_file(original_filename):
                results.append({
                    'original_filename': original_filename,
                    'error': '지원하지 않는 파일 형식입니다.'
                })
                continue
            
            # 파일 임시 저장 및 메타데이터 검사
            file.save(temp_filepath)
            processor = ImageProcessor()
            metadata = processor.extract_metadata(temp_filepath)
            
            # 메타데이터 검사
            missing_data = []
            if not metadata.get('촬영시간'):
                missing_data.append('시간')
            if not metadata.get('위도') or not metadata.get('경도'):
                missing_data.append('위치')
            
            if missing_data:
                os.remove(temp_filepath)
                error_message = f"{'와 '.join(missing_data)} 정보가 없는 이미지입니다."
                results.append({
                    'original_filename': original_filename,
                    'error': error_message
                })
                continue
            
            # 촬영시간으로 파일명 변경
            _, ext = os.path.splitext(original_filename)
            new_filename = convert_datetime_to_filename(metadata['촬영시간']) + ext.lower()
            new_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            
            # 최종 파일명으로 중복 검사
            if os.path.exists(new_filepath):
                os.remove(temp_filepath)
                results.append({
                    'original_filename': original_filename,
                    'error': '동일한 촬영 시간의 이미지가 이미 존재합니다.'
                })
                continue
            
            # 파일명 변경
            os.rename(temp_filepath, new_filepath)
            
            # 메타데이터가 있는 경우 결과 추가
            results.append({
                'original_filename': original_filename,
                'saved_filename': new_filename,
                'metadata': metadata
            })
            
        except Exception as e:
            if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            results.append({
                'original_filename': original_filename,
                'error': '파일 처리 중 오류가 발생했습니다.'
            })
    
    return jsonify(results)

if __name__ == '__main__':
    print("서버 시작 준비 중...")
    initialize_folders()  # 서버 시작 시 폴더 초기화
    print(f"업로드 폴더 경로: {UPLOAD_FOLDER}")
    app.run(debug=True)