"""
Modul pro generování diktátů pomocí Claude LLM
"""
from openai import OpenAI
import json
from datetime import datetime
import os

# Konfigurace OpenAI klienta pro playpi4.local
client = OpenAI(
    api_key="sk-5OYzLw5vfDWnFw6HZB4vTQ",
    base_url="http://playpi4.local:4000/v1"
)

MODEL = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"

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
- Používej různou interpunkci (tečka, čárka, otazník, vykřičník)
- Věty by měly být různě dlouhé a pestré

Vrať pouze seznam vět, každou na samostatném řádku, bez číslování.
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
            temperature=0.8,  # Více kreativity
            max_tokens=1000
        )
        
        # Získání odpovědi
        content = response.choices[0].message.content.strip()
        
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
