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
    preview.innerHTML = '<p>업로드 중...</p>';
    
    const formData = new FormData();
    
    // 여러 파일 추가
    for (let i = 0; i < files.length; i++) {
        formData.append('files[]', files[i]);
    }

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(results => {
        preview.innerHTML = '';
        
        results.forEach(result => {
            const div = document.createElement('div');
            div.className = 'preview-item';
            
            if (result.error) {
                div.innerHTML = `
                    <p>파일명: ${result.original_filename}</p>
                    <p class="error">오류: ${result.error}</p>
                `;
            } else {
                div.innerHTML = `
                    <p>파일명: ${result.original_filename}</p>
                    <p>촬영시간: ${result.metadata.촬영시간 || '없음'}</p>
                    <p>위치: ${result.metadata.위도 ? 
                        `위도 ${result.metadata.위도}, 경도 ${result.metadata.경도}` : 
                        '없음'}</p>
                `;
            }
            preview.appendChild(div);
        });
    })
    .catch(err => {
        error.textContent = '업로드 중 오류가 발생했습니다.';
        preview.innerHTML = '';
    });
});

// 파일 선택 시 파일 목록 표시
document.getElementById('fileInput').addEventListener('change', function(e) {
    const fileList = document.getElementById('fileList');
    if (this.files.length > 0) {
        fileList.textContent = `${this.files.length}개 파일 선택됨`;
    } else {
        fileList.textContent = '선택된 파일 없음';
    }
});