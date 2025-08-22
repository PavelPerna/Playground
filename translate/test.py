from transformers import pipeline

def translate_text(text: str, source_language: str, target_language: str) -> str:
    """
    Translates text from a source language to a target language using an AI model.

    Args:
        text: The text to be translated.
        source_language: The ISO 639-1 code of the source language (e.g., 'en', 'fr', 'de').
        target_language: The ISO 639-1 code of the target language (e.g., 'fr', 'en', 'es').

    Returns:
        The translated text as a string. Returns an error message if translation fails.
    """
    try:
        translator = pipeline(
            "translation",
            model=f"Helsinki-NLP/opus-mt-{source_language}-{target_language}"
        )
        result = translator(text)
        return result[0]['translation_text']
    except Exception as e:
        return f"Translation failed: {e}"

if __name__ == "__main__":
    text_to_translate = "You filthy pig , eat my big fat turds"
    source_lang = "en"
    target_lang = "cs"

    translated_text = translate_text(text_to_translate, source_lang, target_lang)
    print(f"Original text ({source_lang}): {text_to_translate}")
    print(f"Translated text ({target_lang}): {translated_text}")
