from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
from dictation import generate_sentences, save_dictation
from tts_generator import generate_dictation_audio
from ocr_processor import extract_text_from_image
from evaluator import evaluate_dictation
from PIL import Image
import io

# Konfigurace Flask pro servírování frontendu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# Konfigurace cest
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
DICTATIONS_DIR = os.path.join(DATA_DIR, 'dictations')
AUDIO_DIR = os.path.join(DATA_DIR, 'audio')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
EVALUATIONS_DIR = os.path.join(DATA_DIR, 'evaluations')

# Ujistíme se, že adresáře existují
for directory in [DICTATIONS_DIR, AUDIO_DIR, UPLOADS_DIR, EVALUATIONS_DIR]:
    os.makedirs(directory, exist_ok=True)

@app.route('/')
def index():
    """Hlavní stránka - vrátí index.html"""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Základní health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'directories': {
            'dictations': os.path.exists(DICTATIONS_DIR),
            'audio': os.path.exists(AUDIO_DIR),
            'uploads': os.path.exists(UPLOADS_DIR)
        }
    })

@app.route('/api/generate', methods=['POST'])
def generate_dictation():
    """Generuje věty pro diktát pomocí LLM"""
    data = request.get_json()
    grade = data.get('grade', 3)
    num_sentences = data.get('num_sentences', 10)
    
    # Validace
    if not isinstance(grade, int) or grade < 1 or grade > 9:
        return jsonify({'error': 'Grade must be between 1 and 9'}), 400
    
    # Generování vět
    result = generate_sentences(grade, num_sentences)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    
    # Uložení diktátu
    filename = save_dictation(result, DICTATIONS_DIR)
    result['saved_as'] = filename
    
    return jsonify(result)

@app.route('/api/dictate', methods=['POST'])
def create_audio():
    """Vytvoří audio soubor z textu pomocí Google TTS"""
    data = request.get_json()
    sentences = data.get('sentences', [])
    pause_duration = data.get('pause_duration', 5.0)
    slow = data.get('slow', False)
    
    # Validace
    if not sentences or not isinstance(sentences, list):
        return jsonify({'error': 'Sentences array is required'}), 400
    
    try:
        # Generování názvu souboru
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"dictation_{timestamp}.mp3"
        output_path = os.path.join(AUDIO_DIR, filename)
        
        # Generování audio
        generate_dictation_audio(
            sentences=sentences,
            output_path=output_path,
            pause_duration=pause_duration,
            slow=slow
        )
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'audio_url': f'/api/audio/{filename}',
            'file_size': os.path.getsize(output_path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Nahraje fotku diktátu"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Uložení souboru
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"upload_{timestamp}.jpg"
        filepath = os.path.join(UPLOADS_DIR, filename)
        
        # Uložení a případná konverze na JPEG
        img = Image.open(file.stream)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.save(filepath, 'JPEG', quality=95)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'filepath': filepath
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate_dictation_endpoint():
    """Vyhodnotí diktát pomocí OCR a LLM"""
    print("DEBUG: Evaluate endpoint called")
    
    if 'image' not in request.files:
        print("DEBUG: No image file in request")
        return jsonify({'error': 'No image file provided'}), 400
    
    original_text = request.form.get('original_text', '')
    if not original_text:
        print("DEBUG: No original text provided")
        return jsonify({'error': 'Original text is required'}), 400
    
    print(f"DEBUG: Original text length: {len(original_text)}")
    
    try:
        # Uložení obrázku
        file = request.files['image']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"evaluation_{timestamp}.jpg"
        filepath = os.path.join(UPLOADS_DIR, filename)
        
        print(f"DEBUG: Saving image to {filepath}")
        
        # Uložení a konverze
        img = Image.open(file.stream)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        img.save(filepath, 'JPEG', quality=95)
        
        print("DEBUG: Image saved successfully")
        
        # OCR - extrakce textu z obrázku
        print("DEBUG: Starting OCR extraction...")
        ocr_result = extract_text_from_image(filepath)
        print(f"DEBUG: OCR result: {ocr_result}")
        
        if 'error' in ocr_result:
            print(f"DEBUG: OCR error: {ocr_result['error']}")
            return jsonify({'error': f"OCR failed: {ocr_result['error']}"}), 500
        
        written_text = ocr_result['extracted_text']
        print(f"DEBUG: Extracted text length: {len(written_text)}")
        
        # Vyhodnocení diktátu
        print("DEBUG: Starting evaluation...")
        evaluation = evaluate_dictation(original_text, written_text)
        print(f"DEBUG: Evaluation result: {evaluation}")
        
        if 'error' in evaluation:
            print(f"DEBUG: Evaluation error: {evaluation['error']}")
            return jsonify({'error': f"Evaluation failed: {evaluation['error']}"}), 500
        
        # Přidání informací o souboru
        evaluation['image_filename'] = filename
        evaluation['ocr_text'] = written_text
        
        # Uložení vyhodnocení do souboru
        import json
        eval_filename = f"evaluation_{timestamp}.json"
        eval_filepath = os.path.join(EVALUATIONS_DIR, eval_filename)
        with open(eval_filepath, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)
        
        evaluation['evaluation_saved_as'] = eval_filename
        print(f"DEBUG: Evaluation saved to {eval_filename}")
        print("DEBUG: Evaluation completed successfully")
        return jsonify(evaluation)
        
    except Exception as e:
        print(f"DEBUG: Exception in evaluate endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio(filename):
    """Stáhne audio soubor"""
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='audio/mpeg')
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    print("Starting diktátOR Flask server...")
    print(f"Data directory: {DATA_DIR}")
    app.run(host='0.0.0.0', port=5000, debug=True)
