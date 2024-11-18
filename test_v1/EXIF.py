# import subprocess
# import sys

# def install_required_packages():
#     """필요한 패키지 자동 설치 함수"""
#     required_packages = ['Pillow']  # Pillow 패키지만 필요
#     for package in required_packages:
#         try:
#             __import__(package)
#         except ImportError:
#             print(f"{package} 패키지를 설치합니다...")
#             subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
#             print(f"{package} 설치 완료!")

# # 필요한 패키지 설치
# install_required_packages()

import os
from PIL import Image
from PIL.ExifTags import TAGS

def extract_metadata(image_path):
    try:
        # 이미지 열기
        image = Image.open(image_path)
        exif = image._getexif()
            
        metadata = {}
        
        # 시간 정보 추출
        time_found = False
        if exif:
            time_tags = {
                36867: 'DateTimeOriginal',    # 촬영 시간
                36868: 'DateTimeDigitized'    # 디지털화된 시간
            }
            
            # 시간 정보 찾기
            for tag_id, tag_name in time_tags.items():
                if tag_id in exif:
                    metadata['촬영시간'] = str(exif[tag_id])
                    time_found = True
                    break
        
        # GPS 정보 추출
        gps_found = False
        if exif and 34853 in exif:  # GPSInfo
            gps_info = exif[34853]
            
            if 2 in gps_info and 4 in gps_info:
                try:
                    # 위도 계산
                    lat = convert_to_degrees(gps_info[2])
                    lat_ref = gps_info[1]
                    if lat_ref == 'S':
                        lat = -lat
                        
                    # 경도 계산
                    lon = convert_to_degrees(gps_info[4])
                    lon_ref = gps_info[3]
                    if lon_ref == 'W':
                        lon = -lon
                        
                    metadata['위도'] = f"{lat:.6f}"
                    metadata['경도'] = f"{lon:.6f}"
                    gps_found = True
                except:
                    pass

        return metadata, time_found, gps_found

    except Exception as e:
        return None, False, False

def convert_to_degrees(value):
    """GPS 좌표를 도(degrees) 단위로 변환"""
    if isinstance(value, tuple):
        d = float(value[0])  # 도
        m = float(value[1])  # 분
        s = float(value[2])  # 초
        return d + (m / 60.0) + (s / 3600.0)
    return None

def process_directory(directory_path):
    """디렉토리 내의 모든 이미지 파일 처리"""
    # 지원하는 이미지 형식 (기획서 요구사항)
    image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    
    for filename in os.listdir(directory_path):
        file_extension = os.path.splitext(filename)[1].lower()
        
        print(f"\n파일명: {filename}")
        
        # 파일 확장자 검사
        if not file_extension:
            print("확장자가 없는 파일입니다.")
            continue
        
        if file_extension not in [ext.lower() for ext in image_extensions]:
            print(f"지원하지 않는 파일 형식입니다. (지원 형식: JPG, JPEG, PNG)")
            continue
        
        file_path = os.path.join(directory_path, filename)
        metadata, time_found, gps_found = extract_metadata(file_path)
        
        # 시간 정보 출력
        if metadata and '촬영시간' in metadata:
            print(f"촬영시간: {metadata['촬영시간']}")
        else:
            print("시간 정보가 존재하지 않습니다.")
        
        # 위치 정보 출력
        if metadata and '위도' in metadata and '경도' in metadata:
            print(f"위도: {metadata['위도']}")
            print(f"경도: {metadata['경도']}")
        else:
            print("위치 정보가 존재하지 않습니다.")

if __name__ == "__main__":
    # 검사하고 싶은 폴더 경로를 직접 지정
    target_dir = "test_v1\static\uploads"  # 원하는 폴더 경로로 수정
    
    print("\n=== 이미지 메타데이터 분석 시작 ===")
    process_directory(target_dir)