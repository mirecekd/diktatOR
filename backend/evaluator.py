"""
Modul pro vyhodnocení diktátu pomocí LLM
"""
from google import genai
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Načtení environment variables z .env souboru
load_dotenv()

# Konfigurace Google Gemini klienta
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")

GEMINI_EVAL_MODEL = os.getenv('GEMINI_EVAL_MODEL', 'gemini-2.5-flash')

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def evaluate_dictation(original_text: str, written_text: str) -> dict:
    """
    Vyhodnotí diktát porovnáním originálního a napsaného textu.
    
    Args:
        original_text: Originální nadiktovaný text
        written_text: Text přečtený z fotky diktátu
    
    Returns:
        dict: {
            'summary': str,  # Celkové shrnutí
            'errors': list,  # Seznam chyb
            'score': float,  # Skóre 0-100
            'details': str,  # Detailní vyhodnocení
            'timestamp': str
        }
    """
    
    prompt = f"""Jsi učitel českého jazyka. Vyhodnoť prosím tento diktát od žáka.

ORIGINÁLNÍ TEXT (co bylo nadiktováno):
{original_text}

NAPSANÝ TEXT (co žák napsal):
{written_text}

Vyhodnoť diktát a poskytni:
1. Celkové hodnocení (1-2 věty)
2. Seznam konkrétních chyb (pravopis, interpunkce, chybějící slova)
3. Pochvalu za to, co bylo správně
4. Doporučení pro zlepšení

Buď konstruktivní a povzbuzující. Pamatuj, že je to žák základní školy.

DŮLEŽITÉ PRAVIDLO FORMÁTOVÁNÍ:
- NEPOUŽÍVEJ MARKDOWN syntaxi (žádné hvězdičky, podtržítka apod.)
- Použij jen prostý text
- Nepoužívej tučný text (bold), kurzívu nebo jiné formátování
- Piš jen normální text bez markdown značek

Vrať odpověď v následujícím formátu:

HODNOCENÍ: [tvoje celkové hodnocení]

CHYBY:
- [chyba 1]
- [chyba 2]
...

POCHVALA:
[co bylo dobře]

DOPORUČENÍ:
[co zlepšit]

SKÓRE: [číslo 0-100]
"""

    try:
        # Volání Google Gemini API
        response = gemini_client.models.generate_content(
            model=GEMINI_EVAL_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.1,  # Nižší teplota pro konzistentní vyhodnocení
                max_output_tokens=16384  # Zvýšený limit pro delší vyhodnocení (16k)
            )
        )
        
        # Získání odpovědi
        if hasattr(response, 'text') and response.text:
            evaluation_text = response.text.strip()
        else:
            raise ValueError("No text in response from Gemini API")
        
        # Parsování odpovědi
        result = {
            'evaluation_text': evaluation_text,
            'original_text': original_text,
            'written_text': written_text,
            'timestamp': datetime.now().isoformat()
        }
        
        # Pokus o extrakci skóre
        try:
            if 'SKÓRE:' in evaluation_text:
                score_line = [line for line in evaluation_text.split('\n') if 'SKÓRE:' in line][0]
                # Extrahuj první číslo ze skóre (před lomítkem nebo celé číslo)
                import re
                score_match = re.search(r'SKÓRE:\s*(\d+)', score_line)
                if score_match:
                    score = float(score_match.group(1))
                    result['score'] = min(100, max(0, score))
                else:
                    result['score'] = None
        except:
            result['score'] = None
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    # Test vyhodnocení
    original = "Maminka peče koláč. Pes si hraje na zahradě."
    written = "Maminka pece kolac. Pes sy hraje na zahjadě."
    
    print("Testing evaluation...")
    print(f"\nOriginal: {original}")
    print(f"Written: {written}\n")
    
    result = evaluate_dictation(original, written)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print("Evaluation:")
        print(result['evaluation_text'])
        if result.get('score'):
            print(f"\nScore: {result['score']}/100")
