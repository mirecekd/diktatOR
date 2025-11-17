"""
Modul pro generování TTS audio pomocí Google TTS (gtts)
"""
from gtts import gTTS
import os
from datetime import datetime
from pydub import AudioSegment
import tempfile

# Výchozí nastavení
DEFAULT_LANG = 'cs'  # Čeština
DEFAULT_SLOW = True  # Pomalá řeč pro lepší srozumitelnost


def generate_audio(text: str, output_path: str, slow: bool = DEFAULT_SLOW, lang: str = DEFAULT_LANG):
    """
    Generuje audio soubor z textu pomocí Google TTS.
    
    Args:
        text: Text k přečtení
        output_path: Cesta k výstupnímu MP3 souboru
        slow: Pomalá řeč (True/False)
        lang: Jazyk (výchozí: 'cs')
    
    Returns:
        str: Cesta k vygenerovanému souboru
    """
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(output_path)
    return output_path


def generate_dictation_audio(
    sentences: list[str],
    output_path: str,
    pause_duration: float = 5.0,
    slow: bool = True,  # Výchozí: pomalá řeč
    lang: str = DEFAULT_LANG
) -> str:
    """
    Generuje audio pro diktát se speciální strukturou:
    
    Pro každou větu:
    1. Věta pomalu celá
    2. Krátká pauza (2 sekundy)
    3. Věta slovo po slovu s pauzami (1 sekunda mezi slovy)
    4. Krátká pauza (2 sekundy)
    5. Věta pomalu celá (opakování)
    6. Dlouhá pauza před další větou (pause_duration)
    
    Args:
        sentences: List vět k nadiktování
        output_path: Cesta k výstupnímu MP3 souboru
        pause_duration: Délka pauzy mezi větami v sekundách (výchozí: 5.0)
        slow: Pomalá řeč pro celé věty (True/False)
        lang: Jazyk (výchozí: 'cs')
    
    Returns:
        str: Cesta k vygenerovanému souboru
    """
    # Vytvoříme dočasný adresář pro jednotlivé audio soubory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Pauzy
        short_pause = AudioSegment.silent(duration=2000)  # 2 sekundy
        word_pause = AudioSegment.silent(duration=3000)   # 3 sekundy mezi slovy
        long_pause = AudioSegment.silent(duration=int(pause_duration * 1000))
        
        # Spojíme audio pro všechny věty
        combined = AudioSegment.empty()
        
        for i, sentence in enumerate(sentences):
            # 1. Vygeneruj audio pro celou větu (pomalu)
            sentence_file = os.path.join(temp_dir, f"sentence_{i}_full.mp3")
            tts_full = gTTS(text=sentence, lang=lang, slow=slow)
            tts_full.save(sentence_file)
            sentence_audio = AudioSegment.from_mp3(sentence_file)
            os.remove(sentence_file)
            
            # 2. Vygeneruj audio pro každé slovo zvlášť
            # Rozdělíme větu na slova (zachováváme interpunkci u posledního slova)
            words = sentence.replace('.', '').replace(',', '').replace('!', '').replace('?', '').split()
            
            word_audios = []
            for j, word in enumerate(words):
                word_file = os.path.join(temp_dir, f"sentence_{i}_word_{j}.mp3")
                tts_word = gTTS(text=word, lang=lang, slow=slow)
                tts_word.save(word_file)
                word_audio = AudioSegment.from_mp3(word_file)
                word_audios.append(word_audio)
                os.remove(word_file)
            
            # Sestavení struktury pro tuto větu:
            # Celá věta
            combined += sentence_audio
            combined += short_pause
            
            # Slovo po slovu s pauzami
            for j, word_audio in enumerate(word_audios):
                combined += word_audio
                if j < len(word_audios) - 1:  # Pauza mezi slovy (kromě posledního)
                    combined += word_pause
            combined += short_pause
            
            # Opakování celé věty
            combined += sentence_audio
            
            # Dlouhá pauza před další větou (kromě poslední věty)
            if i < len(sentences) - 1:
                combined += long_pause
        
        # Uložení výsledného souboru
        combined.export(output_path, format="mp3")
        
        return output_path
        
    finally:
        # Vyčištění dočasného adresáře
        try:
            os.rmdir(temp_dir)
        except:
            pass


if __name__ == '__main__':
    # Test s jednou větou
    print("Testing Google TTS with a simple sentence...")
    test_sentence = "Dnes je krásné slunečné počasí."
    test_output = "/tmp/test_gtts.mp3"
    
    try:
        generate_audio(test_sentence, test_output)
        print(f"✓ Audio generated successfully: {test_output}")
        print(f"  File size: {os.path.getsize(test_output)} bytes")
        
        # Test diktátu
        print("\nTesting dictation with 2 sentences...")
        sentences = ["Maminka peče koláč.", "Pes si hraje na zahradě."]
        test_dictation = "/tmp/test_dictation_gtts.mp3"
        generate_dictation_audio(sentences, test_dictation, pause_duration=3.0)
        print(f"✓ Dictation audio generated: {test_dictation}")
        print(f"  File size: {os.path.getsize(test_dictation)} bytes")
        
    except Exception as e:
        print(f"✗ Error: {e}")
