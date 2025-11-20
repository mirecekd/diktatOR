"""
Modul pro OCR psaných diktátů od žáků základní školy.

Používá Google Gemini pro přímé OCR z obrázků.
- Výborné výsledky, podobné Google Lens
- Zachovává původní chyby v psaní pro následné hodnocení
"""
from google import genai
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

GEMINI_OCR_MODEL = os.getenv('GEMINI_OCR_MODEL', 'gemini-2.5-flash')

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


@retry_with_backoff(max_retries=5, initial_delay=1.0, backoff_factor=2.0, max_delay=60.0)
def _call_gemini_ocr_api(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    """
    Volá Gemini API pro OCR s retry/backoff logikou.
    
    Args:
        image_bytes: Bytes obrázku
        mime_type: MIME typ obrázku
        prompt: Prompt pro OCR
        
    Returns:
        str: Extrahovaný text z obrázku
    """
    response = gemini_client.models.generate_content(
        model=GEMINI_OCR_MODEL,
        contents=[
            genai.types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ),
            prompt
        ]
    )
    
    if hasattr(response, 'text') and response.text:
        return response.text.strip()
    else:
        raise ValueError("No text in response from Gemini API")


def extract_text_from_image(image_path: str) -> dict:
    """
    Extrahuje text přímo z obrázku pomocí Google Gemini.
    
    Args:
        image_path: Cesta k obrázku
    
    Returns:
        dict: {
            'extracted_text': str,
            'method': str,
            'timestamp': str
        }
    """
    try:
        # Načtení obrázku jako bytes
        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()
        
        # Určení MIME typu
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')
        
        # Prompt pro OCR
        prompt = """Přečti prosím text z tohoto obrázku diktátu od žáka základní školy.

DŮLEŽITÉ INSTRUKCE:
- Přečti PŘESNĚ to, co tam dítě napsalo - znak po znaku
- NEUPRAVUJ gramatiku ani pravopis!
- Pokud je slovo napsané špatně, zapiš ho špatně
- Zachovej všechny chyby v psaní
- Vrať text větu po větě, každou na novém řádku
- Nepiš nic dalšího, jen samotný přečtený text"""
        
        # Volání Google Gemini API s retry/backoff logikou
        extracted_text = _call_gemini_ocr_api(image_bytes, mime_type, prompt)
        
        result = {
            'extracted_text': extracted_text,
            'method': f'gemini ({GEMINI_OCR_MODEL})',
            'timestamp': datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    # Test s ukázkovým obrázkem (pokud existuje)
    test_image = '/tmp/test_dictation.jpg'
    if os.path.exists(test_image):
        print(f"Testing Google Gemini OCR with {test_image}...")
        print("=" * 60)
        
        result = extract_text_from_image(test_image)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Method: {result.get('method', 'N/A')}")
            print(f"\nExtracted Text:\n{result['extracted_text']}")
        
        print("\n" + "=" * 60)
    else:
        print(f"Test image not found: {test_image}")
        print("Create a test image first to test OCR functionality.")
        print("\nExample: Place a photo of handwritten Czech text at /tmp/test_dictation.jpg")
