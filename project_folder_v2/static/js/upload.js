document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    const error = document.getElementById('error');
    const preview = document.getElementById('preview');
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
    
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
        } else {
            formData.append('files[]', file);
            hasValidFiles = true;
            div.innerHTML = `
                <p>파일명: ${file.name}</p>
                <p class="loading">업로드 중...</p>
            `;
        }
        preview.appendChild(div);
    }

    // 유효한 파일이 있는 경우에만 업로드 진행
    if (hasValidFiles) {
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(results => {
            // 기존 결과를 지우지 않고 업데이트
            const items = preview.getElementsByClassName('preview-item');
            results.forEach((result, index) => {
                if (items[index]) {
                    if (result.error) {
                        items[index].innerHTML = `
                            <p>파일명: ${result.original_filename}</p>
                            <p class="error">${result.error}</p>
                        `;
                    } else {
                        items[index].innerHTML = `
                            <div class="image-info">
                                <p>파일명: ${result.original_filename}</p>
                                <p>촬영시간: ${result.metadata.촬영시간 || '없음'}</p>
                                <p>위치: ${result.metadata.위도 ? 
                                    `위도 ${result.metadata.위도}, 경도 ${result.metadata.경도}` : 
                                    '없음'}</p>
                            </div>
                        `;
                        // 성공적으로 업로드된 이미지를 사이드바에 추가
                        updateUploadedImages(result);
                    }
                }
            });
    
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

function updateUploadedImages(result) {
    const uploadedImages = document.getElementById('uploadedImages');
    const imageItem = document.createElement('div');
    imageItem.className = 'uploaded-image-item';

    if (!result.error && result.metadata) {
        imageItem.innerHTML = `
            <div class="image-header">
                <span class="filename">${result.original_filename}</span>
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