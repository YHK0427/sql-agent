// static/js/main.js

/**
 * 공통 유틸리티 함수 모음
 */

// 로딩 버튼 상태 변경
function setButtonLoading(buttonId, isLoading, textId = null, spinnerId = null) {
    const button = document.getElementById(buttonId);
    
    if (textId && spinnerId) {
        const text = document.getElementById(textId);
        const spinner = document.getElementById(spinnerId);
        
        if (isLoading) {
            text.classList.add('d-none');
            spinner.classList.remove('d-none');
            button.disabled = true;
        } else {
            text.classList.remove('d-none');
            spinner.classList.add('d-none');
            button.disabled = false;
        }
    } else {
        button.disabled = isLoading;
    }
}

// API 요청 헬퍼
async function apiRequest(url, method = 'GET', body = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        return { success: false, message: error.toString() };
    }
}

// 날짜 포맷팅 (한국 시간)
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 스크롤 애니메이션
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// 알림 토스트 (Bootstrap 토스트 대신 간단한 alert 개선)
function showNotification(message, type = 'info') {
    // 간단한 구현 (추후 toast 라이브러리로 교체 가능)
    alert(message);
}

// HTML 이스케이프 (XSS 방지)
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// 파일 다운로드 헬퍼
async function downloadFile(url, method = 'POST', body = null, filename = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename || `download_${Date.now()}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);
        
        return true;
    } catch (error) {
        console.error('Download failed:', error);
        return false;
    }
}