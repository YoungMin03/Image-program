// static/js/exif.js
// 설명: EXIF 데이터 처리 및 표시를 위한 유틸리티 클래스

class ExifDisplay {
    // EXIF 데이터 표시 메인 함수
    static displayExifData(data) {
        const previewDiv = document.getElementById('preview');
        let resultHTML = '<div class="upload-result">';
        
        // 파일명 표시
        resultHTML += `<h3>업로드된 파일: ${data.filename}</h3>`;
        
        // 메타데이터 상태 섹션
        resultHTML += '<div class="metadata-status">';
        
        // 위치 정보 표시
        if (data.has_location && data.coordinates) {
            resultHTML += this.createStatusItem(
                true,
                '✓',
                `위치: ${this.formatCoordinates(data.coordinates.latitude, data.coordinates.longitude)}`
            );
        } else {
            resultHTML += this.createStatusItem(
                false,
                '!',
                '위치 정보 없음'
            );
        }
        
        // 시간 정보 표시
        if (data.has_datetime && data.datetime) {
            resultHTML += this.createStatusItem(
                true,
                '✓',
                `촬영 시간: ${this.formatDateTime(data.datetime)}`
            );
        } else {
            resultHTML += this.createStatusItem(
                false,
                '!',
                '시간 정보 없음'
            );
        }
        resultHTML += '</div>';

        // 정보 없음 경고 메시지
        if (!data.has_location || !data.has_datetime) {
            resultHTML += this.createWarningMessage();
        }

        resultHTML += '</div>';
        previewDiv.innerHTML = resultHTML;
    }

    // 상태 아이템 생성
    static createStatusItem(isSuccess, icon, text) {
        return `
            <div class="status-item ${isSuccess ? 'success' : 'warning'}">
                <span class="icon">${icon}</span>
                <span>${text}</span>
            </div>`;
    }

    // 경고 메시지 생성
    static createWarningMessage() {
        return `
            <div class="info-message">
                <p>※ 위치나 시간 정보가 없는 이미지는 경로 추적에 사용할 수 없습니다.</p>
                <p>다른 이미지를 선택해주세요.</p>
            </div>`;
    }

    // 좌표 포맷팅
    static formatCoordinates(latitude, longitude) {
        return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
    }

    // 날짜/시간 포맷팅
    static formatDateTime(dateTimeStr) {
        try {
            const date = new Date(dateTimeStr);
            return date.toLocaleString();
        } catch (error) {
            console.error('DateTime formatting error:', error);
            return dateTimeStr; // 파싱 실패시 원본 문자열 반환
        }
    }

    // EXIF 데이터 유효성 검사
    static validateExifData(data) {
        const validation = {
            isValid: true,
            messages: []
        };

        if (!data.filename) {
            validation.isValid = false;
            validation.messages.push('파일명이 없습니다.');
        }

        if (!data.has_location) {
            validation.messages.push('위치 정보가 없습니다.');
        }

        if (!data.has_datetime) {
            validation.messages.push('시간 정보가 없습니다.');
        }

        return validation;
    }
}

// upload.js에서 사용할 수 있도록 전역으로 내보내기
window.ExifDisplay = ExifDisplay;