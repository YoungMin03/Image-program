# utils/exif_handler.py
# 설명: EXIF 메타데이터 추출을 담당하는 유틸리티 클래스
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExifHandler:
    @staticmethod
    def get_exif_data(image_path):
        try:
            image = Image.open(image_path)
            exif = image._getexif()
            
            if exif is None:
                logger.warning(f"No EXIF data found in image: {image_path}")
                return None
            
            exif_data = {}
            for tag_id in exif:
                tag = TAGS.get(tag_id, tag_id)
                data = exif[tag_id]
                
                if tag == "GPSInfo":
                    gps_data = {}
                    for t in data:
                        sub_tag = GPSTAGS.get(t, t)
                        gps_data[sub_tag] = data[t]
                    data = gps_data
                
                exif_data[tag] = data
            
            logger.debug(f"Extracted EXIF data: {exif_data}")
            return exif_data
            
        except Exception as e:
            logger.error(f"Error extracting EXIF data: {str(e)}")
            return None

    @staticmethod
    def get_gps_coordinates(exif_data):
        try:
            if not exif_data or 'GPSInfo' not in exif_data:
                logger.warning("No GPS info found in EXIF data")
                return None

            gps = exif_data['GPSInfo']
            
            required_tags = ['GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef']
            if not all(tag in gps for tag in required_tags):
                logger.warning("Missing required GPS tags")
                return None

            lat = ExifHandler._convert_to_degrees(gps['GPSLatitude'])
            lng = ExifHandler._convert_to_degrees(gps['GPSLongitude'])
            
            if gps['GPSLatitudeRef'] == 'S':
                lat = -lat
            if gps['GPSLongitudeRef'] == 'W':
                lng = -lng
            
            logger.debug(f"Extracted coordinates: {lat}, {lng}")
            return {'latitude': lat, 'longitude': lng}
            
        except Exception as e:
            logger.error(f"Error processing GPS coordinates: {str(e)}")
            return None

    @staticmethod
    def get_datetime(exif_data):
        try:
            datetime_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
            
            for tag in datetime_tags:
                if tag in exif_data:
                    datetime_str = exif_data[tag]
                    return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            
            logger.warning("No datetime information found in EXIF data")
            return None
            
        except Exception as e:
            logger.error(f"Error processing datetime: {str(e)}")
            return None

    @staticmethod
    def _convert_to_degrees(value):
        try:
            d, m, s = value
            degrees = float(d)
            minutes = float(m)
            seconds = float(s)
            
            return degrees + (minutes / 60.0) + (seconds / 3600.0)
        except Exception as e:
            logger.error(f"Error converting GPS coordinates to degrees: {str(e)}")
            raise