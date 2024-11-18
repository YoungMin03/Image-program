// static/js/upload.js
// 설명: 이미지 업로드 및 메타데이터 처리를 위한 클라이언트 사이드 스크립트
// static/js/upload.js
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('imageInput');
    const messageDiv = document.getElementById('message');
    const previewDiv = document.getElementById('preview');

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            validateFile(file);
        }
    });

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await handleFormSubmit();
    });

    function validateFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            showMessage('지원하지 않는 파일 형식입니다. (JPG, PNG만 가능)', 'error');
            fileInput.value = '';
            return false;
        }

        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
            showMessage('파일 크기가 5MB를 초과합니다.', 'error');
            fileInput.value = '';
            return false;
        }

        return true;
    }

    async function handleFormSubmit() {
        const file = fileInput.files[0];
        if (!file) {
            showMessage('파일을 선택해주세요.', 'error');
            return;
        }

        if (!validateFile(file)) {
            return;
        }

        try {
            showMessage('파일 업로드 중...', 'info');
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            handleUploadResponse(result);

        } catch (error) {
            console.error('Upload error:', error);
            showMessage('업로드 중 오류가 발생했습니다. 다시 시도해주세요.', 'error');
        }
    }

    function handleUploadResponse(result) {
        if (result.status === 'success' || result.status === 'warning') {
            showMessage(result.message, result.status);
            if (result.data) {
                ExifDisplay.displayExifData(result.data);  // exif.js의 클래스 사용
            }
        } else {
            showMessage(result.message || '업로드 중 오류가 발생했습니다.', 'error');
        }
    }
    
    function displayUploadResult(data) {
        let resultHTML = '<div class="upload-result">';
        resultHTML += `<h3>업로드된 파일: ${data.filename}</h3>`;
        
        resultHTML += '<div class="metadata-status">';
        
        if (data.has_location && data.coordinates) {
            resultHTML += createStatusItem(
                true,
                '✓',
                `위치: ${formatCoordinates(data.coordinates.latitude, data.coordinates.longitude)}`
            );
        } else {
            resultHTML += createStatusItem(
                false,
                '!',
                '위치 정보 없음'
            );
        }
        
        if (data.has_datetime && data.datetime) {
            resultHTML += createStatusItem(
                true,
                '✓',
                `촬영 시간: ${formatDateTime(data.datetime)}`
            );
        } else {
            resultHTML += createStatusItem(
                false,
                '!',
                '시간 정보 없음'
            );
        }
        resultHTML += '</div>';

        // 메타데이터 부재 시 안내 메시지
        if (!data.has_location || !data.has_datetime) {
            resultHTML += `
                <div class="info-message">
                    <p>※ 위치나 시간 정보가 없는 이미지는 경로 추적에 사용할 수 없습니다.</p>
                    <p>다른 이미지를 선택해주세요.</p>
                </div>`;
        }

        resultHTML += '</div>';
        previewDiv.innerHTML = resultHTML;
    }

    function createStatusItem(isSuccess, icon, text) {
        return `
            <div class="status-item ${isSuccess ? 'success' : 'warning'}">
                <span class="icon">${icon}</span>
                <span>${text}</span>
            </div>`;
    }

    function formatCoordinates(latitude, longitude) {
        return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
    }

    function formatDateTime(dateTimeStr) {
        const date = new Date(dateTimeStr);
        return date.toLocaleString();
    }

    function showMessage(message, type) {
        const messageDiv = document.getElementById('message');
        messageDiv.textContent = message;
        messageDiv.className = `message ${type}`;
        messageDiv.style.display = 'block';
    }
});