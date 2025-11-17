"""
Modul pro generování diktátů pomocí Google Gemini 2.5 Flash
"""
from google import genai
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Načtení environment variables z .env souboru
load_dotenv()

# Konfigurace Google Gemini klienta
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")

GEMINI_DICTATION_MODEL = os.getenv('GEMINI_DICTATION_MODEL', 'gemini-2.5-flash')

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def generate_sentences(grade: int, num_sentences: int = 10) -> dict:
    """
    Generuje věty pro diktát podle ročníku školy.
    
    Args:
        grade: Ročník školy (1-9)
        num_sentences: Počet vět k vygenerování (výchozí: 10)
    
    Returns:
        dict: {
            'sentences': list[str],  # List vět
            'grade': int,
            'timestamp': str,
            'full_text': str  # Všechny věty spojené do jednoho textu
        }
    """
    
    # Prompt pro generování vět podle ročníku
    prompt = f"""Vygeneruj {num_sentences} vět pro diktát v češtině pro žáky {grade}. třídy základní školy.

Požadavky:
- Věty musí být přiměřené úrovni žáka {grade}. třídy
- Používej slovní zásobu a gramatiku odpovídající věku
- Každá věta musí být smysluplná a gramaticky správná
- Používej pouze tečku a otazník na konci vět. Čárky uvnitř vět jsou povolené. NIKDY nepoužívej vykřičník, protože se těžko identifikuje při TTS
- od 4. třídy již využívej vyjmenovaná slova
- od 5. třídy bude v každé větě alespoň 1 vyjmenované slovo
- Věty by měly být různě dlouhé a pestré, ale max. 15 slov

Vrať pouze seznam vět, každou na samostatném řádku, bez číslování.
"""

    try:
        # Volání Google Gemini API
        response = gemini_client.models.generate_content(
            model=GEMINI_DICTATION_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.8,  # Více kreativity
                max_output_tokens=4096  # Zvýšený limit pro delší odpovědi
            )
        )
        
        # Získání odpovědi
        if hasattr(response, 'text') and response.text:
            content = response.text.strip()
        else:
            # Debug info
            error_msg = f"No text in response. Response type: {type(response)}"
            if hasattr(response, 'prompt_feedback'):
                error_msg += f", prompt_feedback: {response.prompt_feedback}"
            if hasattr(response, 'candidates'):
                error_msg += f", candidates: {response.candidates}"
            raise ValueError(error_msg)
        
        # Rozdělení na jednotlivé věty (každá na novém řádku)
        sentences = [s.strip() for s in content.split('\n') if s.strip()]
        
        # Spojení všech vět do jednoho textu
        full_text = ' '.join(sentences)
        
        result = {
            'sentences': sentences,
            'grade': grade,
            'timestamp': datetime.now().isoformat(),
            'full_text': full_text,
            'num_sentences': len(sentences)
        }
        
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'grade': grade,
            'timestamp': datetime.now().isoformat()
        }

def save_dictation(dictation_data: dict, data_dir: str) -> str:
    """
    Uloží diktát do souboru.
    
    Args:
        dictation_data: Data diktátu
        data_dir: Cesta k adresáři pro ukládání
    
    Returns:
        str: Název uloženého souboru
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"dictation_grade{dictation_data['grade']}_{timestamp}.json"
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(dictation_data, f, ensure_ascii=False, indent=2)
    
    return filename

if __name__ == '__main__':
    # Test generování
    print("Testing dictation generation for grade 3...")
    result = generate_sentences(3, 5)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\nGenerated {result['num_sentences']} sentences:")
        for i, sentence in enumerate(result['sentences'], 1):
            print(f"{i}. {sentence}")
        print(f"\nFull text:\n{result['full_text']}")
