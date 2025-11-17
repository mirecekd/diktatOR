"""
Modul pro vyhodnocení diktátu pomocí LLM
"""
from openai import OpenAI
from datetime import datetime
import json

# Konfigurace OpenAI klienta pro playpi4.local
client = OpenAI(
    api_key="sk-5OYzLw5vfDWnFw6HZB4vTQ",
    base_url="http://playpi4.local:4000/v1"
)

MODEL = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"


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
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Nižší teplota pro konzistentní vyhodnocení
            max_tokens=2000
        )
        
        evaluation_text = response.choices[0].message.content.strip()
        
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
                score = float(''.join(filter(str.isdigit, score_line)))
                result['score'] = min(100, max(0, score))
        except:
            result['score'] = None
        
        return result
        
    except Exception as e:
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
