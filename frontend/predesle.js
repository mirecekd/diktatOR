// diktátOR - Předešlé diktáty
const API_URL = '/api';

// DOM Elements
const loading = document.getElementById('loading');
const evaluationsList = document.getElementById('evaluations-list');
const noEvaluations = document.getElementById('no-evaluations');

// Načtení a zobrazení předešlých diktátů
async function loadEvaluations() {
    try {
        const response = await fetch(`${API_URL}/evaluations`);
        
        if (!response.ok) {
            throw new Error('Failed to load evaluations');
        }
        
        const data = await response.json();
        
        loading.classList.add('hidden');
        
        if (data.evaluations && data.evaluations.length > 0) {
            // Uložíme data pro globální přístup
            window.evaluationsData = data.evaluations;
            displayEvaluations(data.evaluations);
        } else {
            noEvaluations.classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('Error loading evaluations:', error);
        loading.classList.add('hidden');
        evaluationsList.innerHTML = `
            <div class="status error">
                Chyba při načítání předešlých diktátů: ${error.message}
            </div>
        `;
    }
}

function displayEvaluations(evaluations) {
    evaluationsList.innerHTML = evaluations.map((evaluation, index) => {
        const timestamp = evaluation.timestamp || 'N/A';
        const date = new Date(timestamp);
        const dateStr = date.toLocaleString('cs-CZ');
        
        const scoreClass = evaluation.score >= 80 ? 'success' : evaluation.score >= 60 ? 'info' : 'error';
        
        // Zobrazíme jen odkaz s datem a skóre
        return `
            <div class="evaluation-link" style="margin-bottom: 15px; padding: 15px; border: 2px solid #667eea; border-radius: 8px; background: white; cursor: pointer;"
                 onclick="showEvaluationDetail(${index})" data-index="${index}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #667eea;">Diktát ${index + 1}</strong>
                        <br>
                        <small style="color: #666;">${dateStr}</small>
                    </div>
                    <div class="score-badge ${scoreClass}" style="width: 80px; height: 80px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <div class="score-number" style="font-size: 2em;">${Math.round(evaluation.score)}</div>
                        <div class="score-label" style="font-size: 0.8em;">bodů</div>
                    </div>
                </div>
                <div class="evaluation-detail" id="detail-${index}" style="display: none; margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;"></div>
            </div>
        `;
    }).join('');
}

// Zobrazení detailu vyhodnocení po kliknutí
function showEvaluationDetail(index) {
    const evaluations = window.evaluationsData;
    const evaluation = evaluations[index];
    const detailDiv = document.getElementById(`detail-${index}`);
    
    // Pokud je detail již viditelný, skryjeme ho
    if (detailDiv.style.display === 'block') {
        detailDiv.style.display = 'none';
        return;
    }
    
    // Jinak načteme a zobrazíme detail
    let html = '';
    
    // Audio přehrávač
    if (evaluation.audio_file) {
        html += `
            <div class="audio-player" style="margin-bottom: 20px;">
                <h4>Audio diktátu:</h4>
                <audio controls style="width: 100%;">
                    <source src="${API_URL}/audio/${evaluation.audio_file}" type="audio/mpeg">
                    Váš prohlížeč nepodporuje přehrávání audio.
                </audio>
            </div>
        `;
    }
    
    // Fotka
    if (evaluation.image_filename) {
        html += `
            <div class="result-section" style="margin-bottom: 20px;">
                <h4>Vyfocený diktát:</h4>
                <img src="${API_URL}/uploads/${evaluation.image_filename}" 
                     alt="Vyfocený diktát" 
                     style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px;"
                     onerror="this.style.display='none';">
            </div>
        `;
    }
    
    // Texty
    if (evaluation.original_text) {
        html += `
            <div class="result-section" style="margin-bottom: 15px;">
                <h4>Originální nadiktovaný text:</h4>
                <div class="text-box" style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; font-family: 'Courier New', monospace; line-height: 1.6;">
                    ${evaluation.original_text}
                </div>
            </div>
        `;
    }
    
    if (evaluation.ocr_text || evaluation.written_text) {
        const text = evaluation.ocr_text || evaluation.written_text;
        html += `
            <div class="result-section" style="margin-bottom: 15px;">
                <h4>Text přečtený z fotky (OCR):</h4>
                <div class="text-box" style="background-color: #fff8dc; padding: 15px; border-radius: 8px; font-family: 'Courier New', monospace; line-height: 1.6;">
                    ${text}
                </div>
            </div>
        `;
    }
    
    // Vyhodnocení
    if (evaluation.evaluation_text) {
        html += `
            <div class="result-section">
                <h4>Vyhodnocení:</h4>
                <div class="evaluation-text" style="line-height: 1.8; color: #333;">
                    ${formatEvaluationText(evaluation.evaluation_text)}
                </div>
            </div>
        `;
    }
    
    detailDiv.innerHTML = html;
    detailDiv.style.display = 'block';
}

function formatEvaluationText(text) {
    // Formátování textu vyhodnocení s lepším zobrazením
    let formatted = text
        .replace(/HODNOCENÍ:/g, '<strong>📝 HODNOCENÍ:</strong>')
        .replace(/CHYBY:/g, '<strong>❌ CHYBY:</strong>')
        .replace(/POCHVALA:/g, '<strong>👍 POCHVALA:</strong>')
        .replace(/DOPORUČENÍ:/g, '<strong>💡 DOPORUČENÍ:</strong>')
        .replace(/SKÓRE:/g, '<strong>🎯 SKÓRE:</strong>');
    
    // Převod řádků na <br>
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

// Inicializace - načtení diktátů při načtení stránky
console.log('Loading evaluations...');
loadEvaluations();
