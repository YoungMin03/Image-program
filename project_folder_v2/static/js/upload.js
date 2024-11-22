let uploadedImageCount = 0;
let MAX_IMAGES;
let MAX_FILE_SIZE;

document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    const error = document.getElementById('error');
    const preview = document.getElementById('preview');
    
    if (files.length === 0) {
        error.textContent = '파일을 선택해주세요.';
        return;
    }

    error.textContent = '';
    preview.innerHTML = '';
    const formData = new FormData();
    let hasValidFiles = false;

    // 각 파일별로 크기 검사 및 처리
    for (let file of files) {
        const div = document.createElement('div');
        div.className = 'preview-item';
        
        // 파일 크기 검사
        if (file.size > MAX_FILE_SIZE) {
            div.innerHTML = `
                <p>파일명: ${file.name}</p>
                <p class="error">파일이 너무 큽니다. (${(file.size/1024/1024).toFixed(1)}MB / 최대 5MB)</p>
            `;
            preview.appendChild(div);
        } else {
            formData.append('files[]', file);
            hasValidFiles = true;
            div.innerHTML = `
                <p>파일명: ${file.name}</p>
                <p class="loading">업로드 중...</p>
            `;
            preview.appendChild(div);
        }
    }

    // 유효한 파일이 있는 경우에만 업로드 진행
    if (hasValidFiles) {
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(results => {
            // 크기 초과 파일의 미리보기는 유지하면서 업로드된 파일들만 결과 업데이트
            const validPreviews = Array.from(preview.children).filter(div => 
                !div.querySelector('.error'));
            validPreviews.forEach(div => div.remove());

            results.forEach(result => {
                const div = document.createElement('div');
                div.className = 'preview-item';

                if (result.error) {
                    div.innerHTML = `
                        <p>파일명: ${result.original_filename}</p>
                        <p class="error">${result.error}</p>
                    `;
                    } else {
                        hasValidImage = true;
                        div.innerHTML = `
                            <p>파일명: ${result.original_filename}</p>
                            <p>촬영시간: ${result.metadata.촬영시간 || '없음'}</p>
                            <p>위치: ${result.metadata.위도 ? 
                                `위도 ${result.metadata.위도}, 경도 ${result.metadata.경도}` : 
                                '없음'}</p>
                        `;
                        // 성공적으로 업로드된 이미지를 사이드바에 추가
                        updateUploadedImages(result);
                    }
                    preview.appendChild(div);
                    
    });

    // 유효한 이미지가 있으면 지도 버튼 표시
    document.getElementById('showMapBtn').style.display = 
        hasValidImage ? 'block' : 'none';

            // 파일 입력 초기화
            document.getElementById('fileInput').value = '';
            document.getElementById('fileList').textContent = '선택된 파일 없음';
        })
        .catch(err => {
            error.textContent = '업로드 중 오류가 발생했습니다.';
            preview.innerHTML = '';
            
            // 에러 발생시에도 파일 입력 초기화
            document.getElementById('fileInput').value = '';
            document.getElementById('fileList').textContent = '선택된 파일 없음';
        });
    }
});

// 파일 선택 시 파일 목록 표시
document.getElementById('fileInput').addEventListener('change', function(e) {
    const fileList = document.getElementById('fileList');
    if (this.files.length > 0) {
        const fileNames = Array.from(this.files).map(file => file.name);
        fileList.innerHTML = `
            <p>${this.files.length}개 파일 선택됨:</p>
            <ul>${fileNames.map(name => `<li>${name}</li>`).join('')}</ul>
        `;
    } else {
        fileList.textContent = '선택된 파일 없음';
    }
});


// 페이지 로드 시 서버에서 설정값 가져오기
document.addEventListener('DOMContentLoaded', function() {
    fetch('/get_settings')
        .then(response => response.json())
        .then(data => {
            MAX_IMAGES = data.max_images;  // MAX_IMAGES 전역 변수에 값 설정
            MAX_FILE_SIZE = data.max_file_size;
            document.getElementById('maxImageCount').textContent = data.max_images;
            uploadedImageCount = data.current_images;  // 현재 이미지 수 설정
            document.getElementById('imageCount').textContent = data.current_images;
            checkImageLimit();  // 초기 상태 체크
        });
});

function updateImageCounter() {
    const counter = document.getElementById('imageCount');
    counter.textContent = uploadedImageCount;
}

// 파일명 줄이기
function truncateFilename(filename, maxLength = 25) {
    if (filename.length <= maxLength) return filename;
    
    const extension = filename.slice(filename.lastIndexOf('.'));
    const nameWithoutExt = filename.slice(0, filename.lastIndexOf('.'));
    
    return nameWithoutExt.slice(0, maxLength - 3 - extension.length) + '...' + extension;
}

function updateUploadedImages(result) {
    const uploadedImages = document.getElementById('uploadedImages');
    const imageItem = document.createElement('div');
    imageItem.className = 'uploaded-image-item';

    if (!result.error && result.metadata) {
        uploadedImageCount++;
        updateImageCounter();
        checkImageLimit();  // 이미지 추가 후 체크

         // 파일명 줄이기 적용
        const truncatedFilename = truncateFilename(result.original_filename);

        imageItem.innerHTML = `
            <div class="image-header">
                <span class="filename" title="${result.original_filename}">${truncatedFilename}</span>
                <button class="delete-btn" onclick="deleteImage('${result.saved_filename}', this)">×</button>
            </div>
            <img src="/uploads/${result.saved_filename}" alt="${result.original_filename}" class="uploaded-image">
            <div class="image-info">
                <div class="metadata">
                    <p class="time">📅 ${result.metadata.촬영시간 || '시간 정보 없음'}</p>
                    ${result.metadata.위도 ? 
                        `<p class="location">📍 위도: ${result.metadata.위도}</p>
                        <p class="location">📍 경도: ${result.metadata.경도}</p>` : 
                        '<p class="no-location">📍 위치 정보 없음</p>'}
                </div>
            </div>
        `;
        
        if (uploadedImages.firstChild) {
            uploadedImages.insertBefore(imageItem, uploadedImages.firstChild);
        } else {
            uploadedImages.appendChild(imageItem);
        }
    }
}

function checkImageLimit() {
    const mapButton = document.getElementById('showMapBtn');
    const warningMsg = document.getElementById('limitWarning');
    
    if (uploadedImageCount > MAX_IMAGES) {
        mapButton.disabled = true;
        mapButton.style.backgroundColor = '#ccc';  // 비활성화 상태 시각적 표시
        warningMsg.style.display = 'block';
        warningMsg.textContent = `지도 보기는 최대 ${MAX_IMAGES}개의 이미지만 가능합니다. ${uploadedImageCount - MAX_IMAGES}개의 이미지를 삭제해주세요.`;
    } else {
        mapButton.disabled = false;
        mapButton.style.backgroundColor = '#2196F3';  // 활성화 상태로 복원
        warningMsg.style.display = 'none';
    }
}

// 이미지 삭제 함수
function deleteImage(filename, buttonElement) {
    if (confirm('이미지를 삭제하시겠습니까?')) {
        fetch(`/delete/${filename}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 삭제 성공 시 해당 이미지 항목 제거
                const imageItem = buttonElement.closest('.uploaded-image-item');
                imageItem.remove();
                uploadedImageCount--;
                updateImageCounter();
                checkImageLimit();
            } else {
                alert('이미지 삭제 실패: ' + data.error);
            }
        })
        .catch(error => {
            alert('이미지 삭제 중 오류 발생');
            console.error('Error:', error);
        });
    }
}

// 드래그 앤 드롭 기능
const dropZone = document.querySelector('.upload-form');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    dropZone.classList.add('highlight');
}

function unhighlight(e) {
    dropZone.classList.remove('highlight');
}

dropZone.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    document.getElementById('fileInput').files = files;
    
    // 파일 선택 이벤트 트리거
    const changeEvent = new Event('change');
    document.getElementById('fileInput').dispatchEvent(changeEvent);
}