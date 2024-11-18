from PIL import Image
from PIL.ExifTags import TAGS

class ImageProcessor:
    def extract_metadata(self, image_path):
        metadata = {}
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()
                
                if exif:
                    # 시간 정보 추출
                    time_tags = {
                        36867: 'DateTimeOriginal',
                        36868: 'DateTimeDigitized'
                    }
                    
                    for tag_id in time_tags:
                        if tag_id in exif:
                            metadata['촬영시간'] = str(exif[tag_id])
                            break
                    
                    # GPS 정보 추출
                    if 34853 in exif:
                        gps_info = exif[34853]
                        if 2 in gps_info and 4 in gps_info:
                            try:
                                lat = self.convert_to_degrees(gps_info[2])
                                lat_ref = gps_info[1]
                                if lat_ref == 'S':
                                    lat = -lat
                                    
                                lon = self.convert_to_degrees(gps_info[4])
                                lon_ref = gps_info[3]
                                if lon_ref == 'W':
                                    lon = -lon
                                    
                                metadata['위도'] = f"{lat:.6f}"
                                metadata['경도'] = f"{lon:.6f}"
                            except:
                                pass
        except Exception as e:
            print(f"메타데이터 추출 중 오류: {str(e)}")
        
        return metadata

    def convert_to_degrees(self, value):
        if isinstance(value, tuple):
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)
        return None