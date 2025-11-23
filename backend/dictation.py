"""
Modul pro generování diktátů pomocí Google Gemini 2.5 Flash
"""
from google import genai
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from gemini_retry import retry_with_backoff

# Načtení environment variables z .env souboru
load_dotenv()

# Konfigurace Google Gemini klienta
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")

GEMINI_DICTATION_MODEL = os.getenv('GEMINI_DICTATION_MODEL', 'gemini-2.5-flash')

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


@retry_with_backoff(max_retries=5, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0)
def _call_gemini_dictation_api(prompt: str) -> str:
    """
    Volá Gemini API pro generování diktátu s retry/backoff logikou.
    
    Args:
        prompt: Prompt pro generování diktátu
        
    Returns:
        str: Vygenerovaný text diktátu
    """
    response = gemini_client.models.generate_content(
        model=GEMINI_DICTATION_MODEL,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0.8,  # Více kreativity
            max_output_tokens=4096  # Zvýšený limit pro delší odpovědi
        )
    )
    
    if hasattr(response, 'text') and response.text:
        return response.text.strip()
    else:
        # Debug info
        error_msg = f"No text in response. Response type: {type(response)}"
        if hasattr(response, 'prompt_feedback'):
            error_msg += f", prompt_feedback: {response.prompt_feedback}"
        if hasattr(response, 'candidates'):
            error_msg += f", candidates: {response.candidates}"
        raise ValueError(error_msg)


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
    prompt = f"""Vygeneruj {num_sentences} vět pro diktát v češtině pro žáky {grade}. třídy základní školy
podle typického učiva české mluvnice. Zde jsou hlavní zaměření podle ročníku:.
1. třída: délka samohlásek, měkké a tvrdé souhlásky, velká písmena na začátku věty a jmen.
2. třída: rozlišování měkkých a tvrdých souhlásek, psaní vyjmenovaných slov začínajících.
3. třída: vyjmenovaná slova, tvorba částí slova, základní druhy slov.
4. třída: procvičování vyjmenovaných slov, vzory podstatných jmen, skladba věty.
5. třída: shoda přísudku s podmětem, rozbor vět, větné členy.
6. třída: pokročilý pravopis bě/bje, vě/vje, mě/mně, zájmena, větné vzorce.
7. třída: rozbor slovních druhů, pravidla psaní velkých písmen, skladba vět.
8. třída: pravopis přejatých slov, slovní zásoba, slovesné kategorie a složitější skladba.
9. třída: rozšířené větné členy, druhy vedlejších vět, opakování pravopisných jevů.

Požadavky:
- Věty mají být spisovné, jasné a zaměřené na praktické procvičení platných mluvnických pravidel pro {grade}. ročník
- Používej slovní zásobu a gramatiku odpovídající věku
- Každá věta musí být smysluplná a gramaticky správná
- Používej pouze tečku a otazník na konci vět. Čárky uvnitř vět jsou povolené. NIKDY nepoužívej vykřičník, protože se těžko identifikuje při TTS
- od 4. třídy již využívej vyjmenovaná slova
- od 5. třídy bude v každé větě alespoň 1 vyjmenované slovo
- Věty by měly být různě dlouhé a pestré, ale max. 15 slov

Vrať pouze seznam vět, každou na samostatném řádku, bez číslování.
"""

    try:
        # Volání Google Gemini API s retry/backoff logikou
        content = _call_gemini_dictation_api(prompt)
        
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
