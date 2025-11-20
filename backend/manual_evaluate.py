#!/usr/bin/env python3
"""
Skript pro ruční vyhodnocení diktátu z existující fotky
"""
import sys
import os
import json
from pathlib import Path
from ocr_processor import extract_text_from_image
from evaluator import evaluate_dictation
from datetime import datetime

# Cesty
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DICTATIONS_DIR = DATA_DIR / 'dictations'
UPLOADS_DIR = DATA_DIR / 'uploads'
EVALUATIONS_DIR = DATA_DIR / 'evaluations'


def manual_evaluate(dictation_file: str, image_file: str):
    """
    Vyhodnotí diktát z existujících souborů
    
    Args:
        dictation_file: Název dictation JSON souboru (např. dictation_grade6_20251120_152322.json)
        image_file: Název fotky (např. evaluation_20251120_152809.jpg)
    """
    
    # Načtení dictation souboru
    dictation_path = DICTATIONS_DIR / dictation_file
    if not dictation_path.exists():
        print(f"❌ Dictation soubor nenalezen: {dictation_path}")
        return False
    
    with open(dictation_path, 'r', encoding='utf-8') as f:
        dictation = json.load(f)
    
    original_text = dictation.get('full_text', '')
    if not original_text:
        print("❌ V dictation souboru chybí full_text")
        return False
    
    print(f"✓ Načten dictation soubor: {dictation_file}")
    print(f"  Ročník: {dictation.get('grade')}")
    print(f"  Počet vět: {dictation.get('num_sentences')}")
    
    # Kontrola fotky
    image_path = UPLOADS_DIR / image_file
    if not image_path.exists():
        print(f"❌ Fotka nenalezena: {image_path}")
        return False
    
    print(f"✓ Nalezena fotka: {image_file}")
    
    # OCR - extrakce textu
    print("\n📸 Provádím OCR (čtení textu z fotky)...")
    ocr_result = extract_text_from_image(str(image_path))
    
    if 'error' in ocr_result:
        print(f"❌ OCR selhalo: {ocr_result['error']}")
        return False
    
    written_text = ocr_result['extracted_text']
    print(f"✓ Text úspěšně přečten z fotky ({len(written_text)} znaků)")
    
    # Vyhodnocení
    print("\n🤖 Vyhodnocuji diktát pomocí LLM...")
    evaluation = evaluate_dictation(original_text, written_text)
    
    if 'error' in evaluation:
        print(f"❌ Vyhodnocení selhalo: {evaluation['error']}")
        return False
    
    # Přidání metadat
    evaluation['image_filename'] = image_file
    evaluation['ocr_text'] = written_text
    
    # Odvození audio filename z dictation souboru
    timestamp = dictation_file.replace('dictation_grade', 'dictation_').replace('.json', '').replace('dictation_', '')
    audio_filename = f"dictation_{timestamp}.mp3"
    audio_path = DATA_DIR / 'audio' / audio_filename
    if audio_path.exists():
        evaluation['audio_file'] = audio_filename
    
    # Uložení evaluation
    # Použijeme timestamp z fotky pro konzistenci
    eval_timestamp = image_file.replace('evaluation_', '').replace('.jpg', '')
    eval_filename = f"evaluation_{eval_timestamp}.json"
    eval_path = EVALUATIONS_DIR / eval_filename
    
    with open(eval_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Vyhodnocení uloženo: {eval_filename}")
    
    # Výpis skóre
    if evaluation.get('score'):
        score = evaluation['score']
        print(f"\n🎯 SKÓRE: {score}/100")
        if score >= 80:
            print("   🌟 Výborně!")
        elif score >= 60:
            print("   👍 Dobře!")
        else:
            print("   💪 Pokračuj v procvičování!")
    
    print(f"\n✅ Hotovo! Nyní se diktát zobrazí na /predesle")
    
    return True


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Použití:")
        print(f"  python {sys.argv[0]} <dictation_soubor> <fotka>")
        print()
        print("Příklad:")
        print(f"  python {sys.argv[0]} dictation_grade6_20251120_152322.json evaluation_20251120_152809.jpg")
        sys.exit(1)
    
    dictation_file = sys.argv[1]
    image_file = sys.argv[2]
    
    print("=" * 60)
    print("diktátOR - Ruční vyhodnocení diktátu")
    print("=" * 60)
    print()
    
    success = manual_evaluate(dictation_file, image_file)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
