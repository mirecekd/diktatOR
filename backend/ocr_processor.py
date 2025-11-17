"""
Modul pro OCR pomocí Claude Vision API
"""
from openai import OpenAI
import base64
from datetime import datetime
import os

# Konfigurace OpenAI klienta pro playpi4.local
client = OpenAI(
    api_key="sk-5OYzLw5vfDWnFw6HZB4vTQ",
    base_url="http://playpi4.local:4000/v1"
)

MODEL = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"


def image_to_base64(image_path: str) -> str:
    """Převede obrázek na base64 string."""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_text_from_image(image_path: str) -> dict:
    """
    Extrahuje text z obrázku pomocí Claude Vision API.
    
    Args:
        image_path: Cesta k obrázku
    
    Returns:
        dict: {
            'extracted_text': str,  # Přečtený text
            'timestamp': str
        }
    """
    try:
        # Načtení obrázku jako base64
        image_base64 = image_to_base64(image_path)
        
        # Určení MIME typu
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = mime_types.get(ext, 'image/jpeg')
        
        # Zavolání Claude Vision API
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": """Přečti prosím text z tohoto obrázku diktátu. 

Je to psaný text od žáka základní školy. Snaž se přečíst všechny věty, i když může být písmo někdy nečitelné.

Vrať pouze přečtený text, větu po větě, každou na novém řádku. Nepiš nic dalšího, jen samotný text."""
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        extracted_text = response.choices[0].message.content.strip()
        
        return {
            'extracted_text': extracted_text,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    # Test s ukázkovým obrázkem (pokud existuje)
    test_image = '/tmp/test_dictation.jpg'
    if os.path.exists(test_image):
        print(f"Testing OCR with {test_image}...")
        result = extract_text_from_image(test_image)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"\nExtracted text:\n{result['extracted_text']}")
    else:
        print(f"Test image not found: {test_image}")
        print("Create a test image first to test OCR functionality.")
