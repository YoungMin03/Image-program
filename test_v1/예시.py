# pip install image
import PIL.Image
from pprint import pprint

# 이미지 불러오기 (YourPath 부분 수정)
img = PIL.Image.open("능소화.jpeg")

# 메타데이터 불러오기
meta_data = img._getexif()

# 메타데이터 전체 출력
pprint(meta_data)

# Check EXIF Code (16진수 -> 10진수 변환)
int("0x8825", 16)

# 추출 예정 메타데이터 정보
# - 참고자료: https://exiftool.org/TagNames/EXIF.html
# - 271: 제조사
# - 272: 모델명
# - 36868: 촬영 시각
# - 36881: 촬영 시각 offset 정보
# - 34853: 좌표 정보 2: 경도, 4: 위도, 6: 고도

# 메타데이터 정보 저장
company = meta_data[271] 
model = meta_data[272] 
timestamp = meta_data[36868] 
timestamp_offset = meta_data[36881] 
gps_info = meta_data[34853] 

# 메타데이터 정보 출력
print(company)
print(model)
print(timestamp)
print(timestamp_offset)
print(gps_info)