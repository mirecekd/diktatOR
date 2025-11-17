"""
Modul pro OCR psaných diktátů od žáků základní školy.

Používá Google Gemini 2.5 Flash pro přímé OCR z obrázků.
- Výborné výsledky, podobné Google Lens
- Zachovává původní chyby v psaní pro následné hodnocení

Fallback: EasyOCR pro offline použití.
"""
from google import genai
import base64
from datetime import datetime
import os
import easyocr
from dotenv import load_dotenv

# Načtení environment variables z .env souboru
load_dotenv()

# Konfigurace Google Gemini klienta
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Model pro OCR
MODEL = "gemini-2.5-flash"  # Google Gemini 2.5 Flash - výborné OCR (podobně jako Google Lens)

# Inicializace EasyOCR readeru (čeština + angličtina pro čísla a názvy)
# gpu=False pro CPU režim
reader = easyocr.Reader(['cs', 'en'], gpu=False)


def extract_with_easyocr(image_path: str) -> str:
    """
    Extrahuje text z obrázku pomocí EasyOCR.
    
    Args:
        image_path: Cesta k obrázku
    
    Returns:
        str: Přečtený text (každá detekovaná řádka na novém řádku)
    """
    try:
        # EasyOCR vrací seznam (bounding_box, text, confidence)
        result = reader.readtext(image_path)
        
        # Spojíme text z jednotlivých detekcí
        # Zachováváme pořadí v jakém byly detekovány
        text_lines = [detection[1] for detection in result]
        
        return '\n'.join(text_lines)
        
    except Exception as e:
        raise Exception(f"EasyOCR error: {str(e)}")


def image_to_base64(image_path: str) -> str:
    """Převede obrázek na base64 string."""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_with_vision_model(image_path: str) -> str:
    """
    Extrahuje text přímo z obrázku pomocí Google Gemini 2.5 Flash.
    Přímý přístup bez lokálního OCR - využívá pokročilé vision capabilities.
    
    Args:
        image_path: Cesta k obrázku
    
    Returns:
        str: Přečtený text (přesně jak je fyzicky napsaný)
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
        
        # Volání Google Gemini API
        response = gemini_client.models.generate_content(
            model=MODEL,
            contents=[
                genai.types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                ),
                prompt
            ]
        )
        
        return response.text.strip()
        
    except Exception as e:
        raise Exception(f"Gemini OCR error: {str(e)}")


def extract_text_from_image(image_path: str, use_fallback_easyocr: bool = False) -> dict:
    """
    Extrahuje text z obrázku.
    
    Podporované metody:
    1. Google Gemini 2.5 Flash (výchozí) - nejlepší kvalita OCR
    2. EasyOCR (fallback) - offline použití
    
    Args:
        image_path: Cesta k obrázku
        use_fallback_easyocr: False = Gemini (default), True = EasyOCR fallback
    
    Returns:
        dict: {
            'extracted_text': str,      # Finální přečtený text
            'method': str,              # Použitá metoda
            'timestamp': str
        }
    """
    try:
        if not use_fallback_easyocr:
            # Přímé OCR pomocí Google Gemini 2.5 Flash
            extracted_text = extract_with_vision_model(image_path)
            
            return {
                'extracted_text': extracted_text,
                'method': f'gemini ({MODEL})',
                'timestamp': datetime.now().isoformat()
            }
        else:
            # Fallback: EasyOCR pro offline použití
            extracted_text = extract_with_easyocr(image_path)
            
            return {
                'extracted_text': extracted_text,
                'method': 'easyocr (fallback)',
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
        print(f"Testing Google Gemini OCR with {test_image}...")
        print("=" * 60)
        
        # Test Google Gemini 2.5 Flash
        print(f"\n### GOOGLE GEMINI 2.5 FLASH OCR ###")
        print("-" * 60)
        result = extract_text_from_image(test_image, use_fallback_easyocr=False)
        
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
