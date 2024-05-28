from fastapi import HTTPException, status
from enum import Enum
from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from pathlib import Path
from app.config import settings


class TokenizerWrapper:
    def __init__(self, model_name, max_token_length):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_token_length = max_token_length

    def encode(self, text):
        return self.tokenizer(text, max_length=self.max_token_length, return_tensors="pt")

    def decode(self, tokens):
        return self.tokenizer.batch_decode(tokens, skip_special_tokens=True)

    def splitText(self, text: str):
        # Разделение текста
        text_parts = [text[i:i + self.max_token_length] for i in range(0, len(text), self.max_token_length)]
        # Токенизация и объединение результатов
        tokenized_outputs = [self.tokenizer(part, return_tensors="pt") for part in text_parts]
        return tokenized_outputs


def detectLang(preparedText: str) -> str:
    lang = detect(preparedText)
    return lang


def getNameModel(srcLang: str):
    models = {
        "fr": settings.MODEL_FR_EN,
        "ru": settings.MODEL_RU_EN,
    }
    return models.get(srcLang, None)


class TranslationService:

    @staticmethod
    def translateIntoEn(preparedText: str):
        langText = detectLang(preparedText)
        if not langText:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language isn't detected")

        model_name = getNameModel(langText)
        if not model_name:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not have such a model for translation")

        tokenizer = TokenizerWrapper(model_name, settings.MAX_TOKEN_LENGTH)
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name)  # Можно подумать об обертке инициализации модели в отдельный класс как токенизатор

        tokenized_outputs = tokenizer.splitText(preparedText)
        # Генерация текста с использованием model.generate
        generated_outputs = []
        for part in tokenized_outputs:
            output = model.generate(**part, max_new_tokens=100)
            generated_outputs.append(output)

        # Декодирование результатов
        decoded_texts = [tokenizer.decode(generated_output) for generated_output in generated_outputs]

        # Преобразование каждого списка строк в одну строку
        decoded_texts_flat = [' '.join(part) for part in decoded_texts]

        # Объединение всех строк в один текст
        full_text = ' '.join(decoded_texts_flat)

        # Вывод результирующего текста
        return full_text


translator = TranslationService()
