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
    speed_factor: float = 0.9,  # Faktor zpomalení (0.85 = 85% rychlosti, čím nižší, tím pomalejší)
    lang: str = DEFAULT_LANG
) -> str:
    """
    Generuje audio pro diktát se speciální strukturou:
    
    1. Přečte všechny věty naráz pomalu
    2. Udělá pauzu (pause_duration)
    3. Pro každou větu:
       - Přečte větu pomalu (3x)
       - Pauza mezi větami
    4. Na konci přečte znovu všechny věty naráz
    
    Args:
        sentences: List vět k nadiktování
        output_path: Cesta k výstupnímu MP3 souboru
        pause_duration: Délka pauzy mezi větami v sekundách (výchozí: 5.0)
        slow: Pomalá řeč pro celé věty (True/False)
        speed_factor: Faktor zpomalení audio (0.85 = 85% rychlosti, výchozí)
        lang: Jazyk (výchozí: 'cs')
    
    Returns:
        str: Cesta k vygenerovanému souboru
    """
    # Vytvoříme dočasný adresář pro jednotlivé audio soubory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Pauzy
        sentence_pause = AudioSegment.silent(duration=int(pause_duration * 1000))  # 2 sekundy mezi opakováním věty
        between_sentences_pause = AudioSegment.silent(duration=3000)  # Pauza mezi větami
        
        # Spojíme audio pro všechny věty
        combined = AudioSegment.empty()
        
        # Krok 1: Přečteme všechny věty naráz pomalu
        full_text = ' '.join(sentences)
        full_text_file = os.path.join(temp_dir, "full_text_initial.mp3")
        tts_full_initial = gTTS(text=full_text, lang=lang, slow=slow)
        tts_full_initial.save(full_text_file)
        full_text_audio = AudioSegment.from_mp3(full_text_file)
        # Zpomalíme audio
        full_text_audio = full_text_audio._spawn(full_text_audio.raw_data, overrides={
            "frame_rate": int(full_text_audio.frame_rate * speed_factor)
        }).set_frame_rate(full_text_audio.frame_rate)
        os.remove(full_text_file)
        
        combined += full_text_audio
        
        # Krok 2: Pauza po úvodním přečtení
        combined += between_sentences_pause
        
        # Krok 3: Pro každou větu - přečteme ji 3x
        for i, sentence in enumerate(sentences):
            # Vygeneruj audio pro celou větu (pomalu)
            sentence_file = os.path.join(temp_dir, f"sentence_{i}.mp3")
            tts_sentence = gTTS(text=sentence, lang=lang, slow=slow)
            tts_sentence.save(sentence_file)
            sentence_audio = AudioSegment.from_mp3(sentence_file)
            # Zpomalíme audio
            sentence_audio = sentence_audio._spawn(sentence_audio.raw_data, overrides={
                "frame_rate": int(sentence_audio.frame_rate * speed_factor)
            }).set_frame_rate(sentence_audio.frame_rate)
            os.remove(sentence_file)
            
            # Přečteme větu 3x s pauzami
            for repeat in range(3):
                combined += sentence_audio
                if repeat < 2:  # Pauza mezi opakováními (ne po posledním)
                    combined += sentence_pause
            
            # Pauza před další větou (kromě poslední věty)
            if i < len(sentences) - 1:
                combined += between_sentences_pause
        
        # Krok 4: Na konci přečteme znovu všechny věty
        combined += between_sentences_pause  # Pauza před závěrečným čtením
        
        full_text_final_file = os.path.join(temp_dir, "full_text_final.mp3")
        tts_full_final = gTTS(text=full_text, lang=lang, slow=slow)
        tts_full_final.save(full_text_final_file)
        full_text_final_audio = AudioSegment.from_mp3(full_text_final_file)
        # Zpomalíme audio
        full_text_final_audio = full_text_final_audio._spawn(full_text_final_audio.raw_data, overrides={
            "frame_rate": int(full_text_final_audio.frame_rate * speed_factor)
        }).set_frame_rate(full_text_final_audio.frame_rate)
        os.remove(full_text_final_file)
        
        combined += full_text_final_audio
        
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
