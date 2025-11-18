// diktátOR Frontend - JavaScript
const API_URL = '/api';

// State
let currentDictation = null;
let currentImage = null;
let rotation = 0;
let originalImageData = null;

// DOM Elements
const generateBtn = document.getElementById('generate-btn');
const gradeSelect = document.getElementById('grade-select');
const numSentencesInput = document.getElementById('num-sentences');
const pauseDurationInput = document.getElementById('pause-duration');

const stepSettings = document.getElementById('step-settings');
const stepDictation = document.getElementById('step-dictation');
const stepUpload = document.getElementById('step-upload');
const stepResults = document.getElementById('step-results');

const loading = document.getElementById('loading');
const audioPlayer = document.getElementById('audio-player');
const audio = document.getElementById('audio');
const uploadBtn = document.getElementById('upload-btn');

const cameraBtn = document.getElementById('camera-btn');
const galleryBtn = document.getElementById('gallery-btn');
const cameraInput = document.getElementById('camera-input');
const galleryInput = document.getElementById('gallery-input');
const previewContainer = document.getElementById('preview-container');
const previewCanvas = document.getElementById('preview-canvas');
const rotateBtn = document.getElementById('rotate-btn');
const evaluateBtn = document.getElementById('evaluate-btn');

const evaluationLoading = document.getElementById('evaluation-loading');
const results = document.getElementById('results');
const newDictationBtn = document.getElementById('new-dictation-btn');

const statusDiv = document.getElementById('status');

// Event Listeners
generateBtn.addEventListener('click', handleGenerate);
uploadBtn.addEventListener('click', () => showStep(stepUpload));
cameraBtn.addEventListener('click', () => cameraInput.click());
galleryBtn.addEventListener('click', () => galleryInput.click());
cameraInput.addEventListener('change', handleImageSelect);
galleryInput.addEventListener('change', handleImageSelect);
rotateBtn.addEventListener('click', handleRotate);
evaluateBtn.addEventListener('click', handleEvaluate);
newDictationBtn.addEventListener('click', resetApp);

// Workflow funkce
function showStep(step) {
    [stepSettings, stepDictation, stepUpload, stepResults].forEach(s => {
        s.classList.remove('active');
    });
    step.classList.add('active');
}

async function handleGenerate() {
    const grade = parseInt(gradeSelect.value);
    const numSentences = parseInt(numSentencesInput.value);
    const pauseDuration = parseFloat(pauseDurationInput.value);

    showStep(stepDictation);
    loading.classList.remove('hidden');
    audioPlayer.classList.add('hidden');
    uploadBtn.classList.add('hidden');

    try {
        // Krok 1: Generování vět
        showStatus('Generuji věty pro diktát...', 'info');
        const generateResponse = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grade, num_sentences: numSentences })
        });

        if (!generateResponse.ok) {
            throw new Error('Chyba při generování vět');
        }

        const dictationData = await generateResponse.json();
        currentDictation = dictationData;

        // Krok 2: Generování audio
        showStatus('Generuji audio soubor...', 'info');
        const audioResponse = await fetch(`${API_URL}/dictate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sentences: dictationData.sentences,
                pause_duration: pauseDuration,
                slow: true  // true = pomalá řeč pro lepší srozumitelnost
            })
        });

        if (!audioResponse.ok) {
            throw new Error('Chyba při generování audio');
        }

        const audioData = await audioResponse.json();
        
        // Uložit název audio souboru pro pozdější použití
        currentDictation.audio_filename = audioData.filename;

        // Přehrání audio
        loading.classList.add('hidden');
        audioPlayer.classList.remove('hidden');
        audio.src = `${API_URL}/audio/${audioData.filename}`;
        
        // Po dokončení přehrání zobrazit tlačítko
        audio.addEventListener('ended', () => {
            uploadBtn.classList.remove('hidden');
            showStatus('Diktát dokončen! Nyní můžete nahrát fotografii.', 'success');
        });

        showStatus('Diktát připraven! Stiskněte play a začněte psát.', 'success');

    } catch (error) {
        console.error('Error:', error);
        showStatus(`Chyba: ${error.message}`, 'error');
        loading.classList.add('hidden');
    }
}

// Funkce pro práci s obrázky (inspirováno TRNDA)
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        showStatus('Neplatný formát souboru', 'error');
        return;
    }

    if (file.size > 10485760) { // 10MB
        showStatus('Soubor je příliš velký (max 10MB)', 'error');
        return;
    }

    currentImage = file;
    rotation = 0;
    loadImageToCanvas(file);
    previewContainer.classList.remove('hidden');
    showStatus('Obrázek nahrán!', 'success');
}

function loadImageToCanvas(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            originalImageData = img;
            drawImageOnCanvas(img, 0);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function drawImageOnCanvas(img, angle) {
    const canvas = previewCanvas;
    const ctx = canvas.getContext('2d');
    
    let width = img.width;
    let height = img.height;
    
    // Zmenšení velkých obrázků
    if (width > 2048 || height > 2048) {
        const scale = Math.min(2048 / width, 2048 / height);
        width = Math.floor(width * scale);
        height = Math.floor(height * scale);
    }
    
    // Nastavení rozměrů canvas podle rotace
    if (angle === 90 || angle === 270) {
        canvas.width = height;
        canvas.height = width;
    } else {
        canvas.width = width;
        canvas.height = height;
    }
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate((angle * Math.PI) / 180);
    ctx.drawImage(img, -width / 2, -height / 2, width, height);
    ctx.restore();
}

function handleRotate() {
    if (!originalImageData) return;
    rotation = (rotation - 90 + 360) % 360;
    drawImageOnCanvas(originalImageData, rotation);
}

async function handleEvaluate() {
    if (!currentImage || !currentDictation) return;

    showStep(stepResults);
    evaluationLoading.classList.remove('hidden');
    results.classList.add('hidden');
    newDictationBtn.classList.add('hidden');

    try {
        // Převedení canvas na blob
        const blob = await new Promise(resolve => {
            previewCanvas.toBlob(resolve, 'image/jpeg', 0.95);
        });

        // Upload obrázku
        const formData = new FormData();
        formData.append('image', blob, 'dictation.jpg');
        formData.append('original_text', currentDictation.full_text);
        formData.append('sentences', JSON.stringify(currentDictation.sentences));
        formData.append('audio_filename', currentDictation.audio_filename);

        const response = await fetch(`${API_URL}/evaluate`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Chyba při vyhodnocení');
        }

        const evaluation = await response.json();
        displayResults(evaluation);

    } catch (error) {
        console.error('Error:', error);
        showStatus(`Chyba: ${error.message}`, 'error');
        evaluationLoading.classList.add('hidden');
    }
}

function displayResults(evaluation) {
    evaluationLoading.classList.add('hidden');
    results.classList.remove('hidden');
    newDictationBtn.classList.remove('hidden');

    // Zobrazení výsledků
    let html = '<h3>Výsledky vyhodnocení</h3>';
    
    // Skóre (pokud je k dispozici)
    if (evaluation.score !== null && evaluation.score !== undefined) {
        const scoreClass = evaluation.score >= 80 ? 'success' : evaluation.score >= 60 ? 'info' : 'error';
        html += `<div class="score-badge ${scoreClass}">
            <div class="score-number">${Math.round(evaluation.score)}</div>
            <div class="score-label">bodů ze 100</div>
        </div>`;
    }
    
    // Fotka diktátu
    const imageDataUrl = previewCanvas.toDataURL('image/jpeg', 0.9);
    html += `
        <div class="result-section">
            <h4>Vyfocený diktát:</h4>
            <img src="${imageDataUrl}" alt="Vyfocený diktát" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px;">
        </div>
    `;
    
    // Originální nadiktovaný text
    if (currentDictation && currentDictation.full_text) {
        html += `
            <div class="result-section">
                <h4>Originální nadiktovaný text:</h4>
                <div class="text-box" style="background-color: #f0f8ff;">${currentDictation.full_text}</div>
            </div>
        `;
    }
    
    // Text přečtený z fotky (OCR)
    if (evaluation.ocr_text) {
        html += `
            <div class="result-section">
                <h4>Text přečtený z fotky (OCR):</h4>
                <div class="text-box" style="background-color: #fff8dc;">${evaluation.ocr_text}</div>
            </div>
        `;
    }
    
    // Detailní vyhodnocení
    if (evaluation.evaluation_text) {
        html += `
            <div class="result-section">
                <h4>Vyhodnocení:</h4>
                <div class="evaluation-text">${formatEvaluationText(evaluation.evaluation_text)}</div>
            </div>
        `;
    }
    
    results.innerHTML = html;
    showStatus('Vyhodnocení dokončeno!', 'success');
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

function resetApp() {
    currentDictation = null;
    currentImage = null;
    rotation = 0;
    originalImageData = null;
    
    cameraInput.value = '';
    galleryInput.value = '';
    audio.src = '';
    
    previewContainer.classList.add('hidden');
    results.classList.add('hidden');
    
    showStep(stepSettings);
    showStatus('', '');
}

function showStatus(message, type) {
    statusDiv.textContent = message;
    statusDiv.className = 'status';
    if (type) statusDiv.classList.add(type);
    if (!message) statusDiv.className = 'status';
}

// Inicializace
console.log('diktátOR initialized');
showStatus('Vyberte nastavení a začněte s diktátem', 'info');
