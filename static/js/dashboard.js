// static/js/dashboard.js

const dbName = window.location.pathname.split('/').pop();
let currentSQL = "";
let diagramLoaded = false;

// ========== 페이지 로드 시 초기화 ==========
document.addEventListener('DOMContentLoaded', function() {
    loadSchemaAnalysis();
    loadSuggestedQueries();
    loadHistory();
    loadModels();
    // 이벤트 리스너 등록
    document.getElementById('generate-sql-btn').addEventListener('click', generateSQL);
    document.getElementById('execute-sql-btn').addEventListener('click', executeSQL);
});

// ========== 스키마 분석 로드 ==========
async function loadSchemaAnalysis() {
    const container = document.getElementById('schema-analysis');
    
    try {
        const data = await apiRequest(`/api/analyze_schema/${dbName}`);
        
        if (data.success) {
            container.innerHTML = data.analysis.replace(/\n/g, '<br>');
        } else {
            container.innerHTML = '<span style="color: var(--accent-danger);">분석 실패</span>';
        }
    } catch (error) {
        container.innerHTML = '<span style="color: var(--accent-danger);">오류 발생</span>';
    }
}

// ========== 추천 질문 로드 ==========
async function loadSuggestedQueries() {
    const container = document.getElementById('suggested-queries');
    
    try {
        const data = await apiRequest(`/api/suggest_queries/${dbName}`);
        
        if (data.success && data.queries.length > 0) {
            let html = '';
            data.queries.forEach(query => {
                html += `<div class="suggestion-item" onclick="selectSuggestion('${escapeHtml(query).replace(/'/g, "\\'")}')">
                    ${escapeHtml(query)}
                </div>`;
            });
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="loading">추천 질문이 없습니다.</div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="loading">로딩 실패</div>';
    }
}

// ========== 히스토리 로드 ==========
async function loadHistory() {
    const container = document.getElementById('query-history');
    
    try {
        const data = await apiRequest(`/api/history/${dbName}`);
        
        if (data.success && data.history.length > 0) {
            let html = '';
            data.history.slice(0, 10).forEach(item => {
                const date = new Date(item.executed_at);
                const timeStr = date.toLocaleString('ko-KR', { 
                    month: 'short', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                const bookmarkIcon = item.is_bookmarked ? '⭐' : '☆';
                
                html += `
                    <div class="history-item">
                        <div class="history-content" onclick='loadFromHistory(${JSON.stringify(item.question)}, ${JSON.stringify(item.sql_query)})'>
                            <div class="history-question">${escapeHtml(item.question)}</div>
                            <div class="history-meta">
                                <span>${timeStr}</span>
                                <span>${item.result_rows}행</span>
                            </div>
                        </div>
                        <button class="bookmark-btn" onclick="toggleBookmark(${item.id}, event)" title="북마크">
                            ${bookmarkIcon}
                        </button>
                    </div>
                `;
            });
            container.innerHTML = html;
        } else {
            container.innerHTML = '<div class="loading">히스토리 없음</div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="loading">로딩 실패</div>';
    }
}

// ========== 북마크 토글 ==========
async function toggleBookmark(historyId, event) {
    event.stopPropagation();
    
    try {
        const data = await apiRequest(`/api/bookmark/${historyId}`, 'POST');
        
        if (data.success) {
            loadHistory(); // 히스토리 새로고침
        }
    } catch (error) {
        console.error('북마크 실패:', error);
    }
}

// ========== 추천 질문 선택 ==========
function selectSuggestion(query) {
    document.getElementById('user-query').value = query;
    document.getElementById('user-query').focus();
}

// ========== 히스토리에서 불러오기 ==========
function loadFromHistory(question, sql) {
    document.getElementById('user-query').value = question;
    document.getElementById('ai-reasoning').textContent = '(히스토리에서 불러온 쿼리)';
    document.getElementById('generated-sql').textContent = sql;
    currentSQL = sql;
    
    document.getElementById('sql-result-section').classList.remove('hidden');
    document.getElementById('result-section').classList.add('hidden');
    
    // 스크롤
    document.getElementById('sql-result-section').scrollIntoView({ behavior: 'smooth' });
}

// ========== SQL 생성 ==========
// ========== SQL 생성 ==========
async function generateSQL() {
    const question = document.getElementById('user-query').value.trim();
    const model = document.getElementById('model-select').value;  // 모델 선택
    
    if (!question) {
        alert('질문을 입력해주세요.');
        return;
    }
    
    // 로딩 상태
    setButtonLoading('generate-sql-btn', true, 'generate-btn-text', 'generate-spinner');
    
    try {
        const data = await apiRequest(`/api/generate_sql/${dbName}`, 'POST', { 
            question,
            model  // 모델 전달
        });
        
        if (data.success) {
            currentSQL = data.sql;
            document.getElementById('ai-reasoning').textContent = data.reasoning;
            document.getElementById('generated-sql').textContent = data.sql;
            document.getElementById('sql-result-section').classList.remove('hidden');
            document.getElementById('result-section').classList.add('hidden');
            
            // 스크롤
            setTimeout(() => {
                document.getElementById('sql-result-section').scrollIntoView({ behavior: 'smooth' });
            }, 100);
        } else {
            alert('SQL 생성 실패: ' + data.message);
        }
    } catch (error) {
        alert('오류 발생: ' + error);
    } finally {
        setButtonLoading('generate-sql-btn', false, 'generate-btn-text', 'generate-spinner');
    }
}
// ========== SQL 실행 ==========
async function executeSQL() {
    if (!currentSQL) {
        alert('먼저 SQL을 생성해주세요.');
        return;
    }
    
    const question = document.getElementById('user-query').value.trim();
    
    // 로딩 상태
    setButtonLoading('execute-sql-btn', true, 'execute-btn-text', 'execute-spinner');
    
    try {
        const data = await apiRequest(`/api/execute_sql/${dbName}`, 'POST', { 
            sql: currentSQL,
            question: question 
        });
        
        if (data.success) {
            displayResults(data.columns, data.rows);
            loadHistory(); // 히스토리 새로고침
        } else {
            alert('SQL 실행 실패: ' + data.error);
        }
    } catch (error) {
        alert('오류 발생: ' + error);
    } finally {
        setButtonLoading('execute-sql-btn', false, 'execute-btn-text', 'execute-spinner');
    }
}

// ========== 결과 테이블 렌더링 ==========
function displayResults(columns, rows) {
    let html = '<table><thead><tr>';
    
    columns.forEach(col => {
        html += `<th>${escapeHtml(col)}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    if (rows.length === 0) {
        html += `<tr><td colspan="${columns.length}" style="text-align: center; color: var(--text-muted);">결과가 없습니다.</td></tr>`;
    } else {
        rows.forEach(row => {
            html += '<tr>';
            row.forEach(cell => {
                const value = cell !== null ? escapeHtml(String(cell)) : '<span style="color: var(--text-muted);">NULL</span>';
                html += `<td>${value}</td>`;
            });
            html += '</tr>';
        });
    }
    
    html += '</tbody></table>';
    
    document.getElementById('query-result').innerHTML = html;
    document.getElementById('result-section').classList.remove('hidden');
    
    // 스크롤
    setTimeout(() => {
        document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

// ========== CSV/Excel 내보내기 ==========
async function exportData(format) {
    if (!currentSQL) {
        alert('먼저 쿼리를 실행해주세요.');
        return;
    }
    
    const success = await downloadFile(
        `/api/export/${format}/${dbName}`,
        'POST',
        { sql: currentSQL },
        `export_${Date.now()}.${format === 'csv' ? 'csv' : 'xlsx'}`
    );
    
    if (!success) {
        alert('내보내기 실패');
    }
}

// ========== 다이어그램 토글 ==========
function toggleDiagram() {
    const container = document.getElementById('diagram-container');
    const toggle = document.getElementById('diagram-toggle');
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        toggle.textContent = '▲';
        
        if (!diagramLoaded) {
            loadSchemaDiagram();
            diagramLoaded = true;
        }
    } else {
        container.classList.add('hidden');
        toggle.textContent = '▼';
    }
}

// ========== 스키마 다이어그램 로드 ==========
async function loadSchemaDiagram() {
    const container = document.getElementById('schema-diagram');
    
    try {
        const data = await apiRequest(`/api/schema_diagram/${dbName}`);
        
        if (data.success) {
            container.innerHTML = `<pre class="mermaid">${data.diagram}</pre>`;
            
            // Mermaid 렌더링
            mermaid.run({
                querySelector: '.mermaid'
            });
        } else {
            container.innerHTML = '<div class="loading" style="color: var(--accent-danger);">다이어그램 생성 실패</div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="loading" style="color: var(--accent-danger);">오류 발생</div>';
    }
}

async function loadModels() {
    try {
        const data = await apiRequest('/api/models');
        
        if (data.success) {
            const select = document.getElementById('model-select');
            select.innerHTML = '';
            
            for (const [key, description] of Object.entries(data.models)) {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = `${key} - ${description}`;
                select.appendChild(option);
            }
        }
    } catch (error) {
        console.error('모델 목록 로드 실패:', error);
    }
}