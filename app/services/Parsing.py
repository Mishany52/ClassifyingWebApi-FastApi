import requests
from pydantic import AnyUrl
from typing import List, Mapping
import re
from bs4 import BeautifulSoup
import nltk
import emoji
import unicodedata
import contractions
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import CountVectorizer
from langdetect import detect
import time
# Словарь с регулярными выражениями и заменами
regexDict = {
    r'<[^<]+?>':' ', #HTML теги
    r'(?:\\n|\n)+': ' ',  # Перевод строки
    r'(\\r)+': ' ',  # Возврат каретки
    r'\d+':' ', #Числа
    r'(http?:\/\/|https?:\/\/|ftp:\/\/(\w+(:.+?)?@)?)([-a-z0-9]+\.)+[a-z]{2,4}': ' ',  # URL
    r'\b\w+@\w+\.\w+\b': ' ',  # Почта
    r'[@#]\S+': ' ',  # Упоминания пользователей и хэштеги
    r'\+\d*|[\d:;"“*™®—•→<>\\|×&\-°©%{2}·\(\)\{\}\[\]\/]': ' ',  # Цифры и другие символы
    r'"': ' ',  # Двойные кавычки
    r'(?<=[a-z])(?=[A-Z])': ' ',  # Разделение слов catDog dogCat
    r'(?<=[а-яё])(?=[А-ЯЁ])': ' ',  # Разделение слов котСобака СобакаКот
    r'(?<=[а-я])(?=[А-Я])|(?<=[А-Я])(?=[А-Я][а-я])': ' ',  # Разделение слов
    r"\s+(?=(?:[,'.?!:;…]))": '',  # Удаление пробелов перед знаками препинания
    r'(?<=[.,;:!?])[.,;:!?]+': '',  # Удаление повторов
    r'\[[^()]*\]': '',  # Текст в квадратных скобках
    r'\b\w\b': ' ', # Одиночные буквы
    r'\s+': ' ',  # Пробелы
    r'[^а-яёА-Яa-zA-Z0-9\s\.]': '',  # Специальные символы: удаляем все, что не является "словами"
}
HEADERS: dict = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
class ParsingSiteService():
    @staticmethod
    def getHtml(url: AnyUrl, params='', headers: Mapping[str, str | bytes] | None = HEADERS, proxy = None) -> str:
            try:
                r = requests.get(url, headers=headers, params=params, proxies=proxy, timeout=30)
                if r.status_code == 200:
                    html_code = r.text  # выгружаем html code со страницы
                    print("Good ",url)
                    return html_code
                else:
                    return None
            except requests.exceptions.SSLError as e:
                # Если возникает ошибка SSL, делаем запрос через HTTP
                if 'SSLEOFError' in str(e):
                    http_url = str(url).replace('https://', 'http://')
                    try:
                        r = requests.get(http_url, proxies=proxy, timeout=30)
                        r.raise_for_status()
                        html_code = r.text
                        # Обрабатываем успешный ответ
                        return html_code
                    except Exception as e:
                        # print(f"Error fetching {http_url} with proxy {proxy}: {e}")
                        return None
                else:
                    # Если другая ошибка SSL, выводим сообщение об ошибке
                    print("SSL Error:")
            except Exception as e:
                # Обрабатывать любые исключения, которые могут возникнуть во время запроса
                # print(f"Request error occurred: {e}")
                return None
    @staticmethod
    def cleanHtml(html: str) -> str:
        """
        Очистка HTML от комментариев, скриптов, стилей и ненужных тегов.
        
        :param html: Входной HTML в виде строки
        :return: Очищенный текст
        """
        try:
            # Удалить комментарии
            no_comments = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
            # Удалить элементы script и style
            soup = BeautifulSoup(no_comments, 'html.parser')
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            
            # Заменить теги <br> на пробел
            for br in soup.find_all('br'):
                br.replace_with(' ')
            
            # Заменить </li> на ' </li>' для обеспечения разделения элементов списка
            for li in soup.find_all('li'):
                li.insert_after(' ')
        
            # Получить текст и заменить несколько пробелов на один пробел
            text = ' '.join(soup.stripped_strings)
            cleaned_text = re.sub(r'\s+', ' ', text)
            return cleaned_text
        except Exception as e:
            raise ValueError(f"Ошибка при очистке HTML: {e}")

    @staticmethod
    def cleanRegex(text: str) -> str:
        """
        Очистка текста с использованием регулярных выражений.
        
        :param text: Входной текст
        :param regexDict: Словарь с регулярными выражениями и их заменами
        :return: Очищенный текст
        """
        try:
            processed_text = text  # Начальное значение processed_text
            for regex_pattern, replacement in regexDict.items():
                processed_text = re.sub(regex_pattern, replacement, processed_text)
            processed_text = processed_text.strip()  # Удаление лишних пробелов
            return processed_text
        except Exception as e:
            raise ValueError(f"Ошибка при очистке текста регулярными выражениями: {e}")

    @staticmethod
    def convert_emojis_to_words(text: str) -> str:
        """
        Преобразование эмодзи в текстовое представление.
        
        :param text: Входной текст с эмодзи
        :return: Текст с преобразованными эмодзи
        """
        try:
            # Преобразование эмодзи в слова
            text = emoji.demojize(text, delimiters=(" ", " "))
            
            # Удалить двоеточие из слов и заменить подчеркивание на пробел
            text = text.replace(":", "").replace("_", " ")
            
            return text
        except Exception as e:
            raise ValueError(f"Ошибка при преобразовании эмодзи: {e}")
            
    @staticmethod
    def text_vectorize(input_text: list) -> np.ndarray:
        """
        Преобразование текста в матрицу частот слов.
        
        :param input_text: Входной текст в виде списка предложений
        :return: Плотная матрица в виде numpy массива
        """
        try:
            if not isinstance(input_text, list):
                raise ValueError("Входной параметр должен быть списком строк")
            
            # Создание объекта CountVectorizer
            vectorizer = CountVectorizer()
            
            # Использование vectorizer.fit_transform для преобразования текста в матрицу частот слов
            counts_matrix = vectorizer.fit_transform(input_text)
            
            # Преобразование в плотную матрицу
            dense_matrix = counts_matrix.todense()
            
            # Возврат плотной матрицы в виде numpy массива
            return np.array(dense_matrix)
        except Exception as e:
            raise ValueError(f"Ошибка при векторизации текста: {e}")
    @staticmethod
    def clean_text(input_text: str):
        
        # Эмодзи и смайлики: используем самописную функцию для преобразования эмодзи в текст
        # Это важно для понимания настроения текста
        clean_text = ParsingSiteService.convert_emojis_to_words(input_text)
        
        # Привести все входные данные к нижнему регистру
        clean_text = clean_text.lower()
    
        # Преобразование символов с акцентами в ASCII символы: используем функцию нормализации unicode для преобразования всех символов с акцентами в ASCII символы
        # clean_text = unicodedata.normalize('NFKD', clean_text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    
        # Развернуть сокращения: текст часто содержит слова типа "don't" или "won't", развернем их
        clean_text = contractions.fix(clean_text)

        #Обаботка регулярными выражениями
        clean_text = ParsingSiteService.cleanRegex(clean_text)
        
        english_words = set(nltk.corpus.words.words())
        # Удалить стоп-слова
        stop_words = set(stopwords.words('english'))
        words = set(nltk.corpus.words.words())
        tokens = word_tokenize(clean_text)
        
        #! tokens = [token for token in tokens if token not in stop_words and token in english_words]
        tokens = [token for token in tokens if token not in stop_words]
        clean_text = ' '.join(tokens)
    
        # Добавить точку в конце предложений
        clean_text = re.sub('([a-z])\.([A-Z])', r'\1. \2', clean_text)
    
        # Удалить знаки препинания
        clean_text = re.sub(r'[^\w\s.]', '', clean_text)
    
        # Вернуть предварительно обработанный, чистый текст
        return clean_text
    @staticmethod
    def pos_tag_wordnet(tagged_tokens):
        """
        Преобразует теги POS, полученные от nltk.pos_tag, в теги WordNet.
        
        :param tagged_tokens: список кортежей (слово, тег)
        :return: список кортежей (слово, WordNet тег)
        """
        tag_map = {'j': wordnet.ADJ, 'v': wordnet.VERB, 'n': wordnet.NOUN, 'r': wordnet.ADV}
        new_tagged_tokens = [(word, tag_map.get(tag[0].lower(), wordnet.NOUN)) for word, tag in tagged_tokens]
        return new_tagged_tokens

    @staticmethod
    def wordnet_lemmatize_text(text: str):
        """
        Лемматизирует текст, используя теги POS для улучшения точности.
        
        :param text: строка текста для лемматизации
        :return: лемматизированная строка текста
        """
        wnl = WordNetLemmatizer()
        tagged_tokens = nltk.pos_tag(nltk.word_tokenize(text))
        wordnet_tokens = ParsingSiteService.pos_tag_wordnet(tagged_tokens)
        lemmatized_text = ' '.join(wnl.lemmatize(word,tag) for word, tag in wordnet_tokens)
        return lemmatized_text
        
    # @staticmethod
    # def full_pipepline(url: AnyUrl):
    #     start_time = time.time()  # Начало отсчета времени
        
    #     html = WebSiteService.getHtml(url=url,headers=HEADERS)
    #     withoutHtml = WebSiteService.cleanHtml(html)
    #     cleanByRegex = WebSiteService.clean_text(withoutHtml)
    #     cleanText = WebSiteService.wordnet_lemmatize_text(cleanByRegex)

    #     print('withoutHtml - ', len(withoutHtml))
    #     print('cleanByRegex - ', len(cleanByRegex))
    #     print('cleanText - ', len(cleanText))
        
    #     end_time = time.time()  # Конец отсчета времени
    #     processing_time = end_time - start_time  # Вычисление времени обработки
    #     print(f"Время обработки: {processing_time:.2f} секунд")
        
    #     return cleanText
    @staticmethod
    # Функция для определения языка текста
    def detect_language(text):
        try:
            detected_language = detect(text)
            return detected_language
        except Exception as e:
            print("An error occurred:", e)
            return None

    @staticmethod
    def full_pipeline(url: AnyUrl, proxy = None):
        processing_times = {}
        text_sizes = {}
        
        start_time = time.time()  # Начало отсчета времени
        html = ParsingSiteService.getHtml(url=url, headers=HEADERS, proxy=proxy)
        end_time = time.time()
        processing_times['getHtml'] = end_time - start_time
        if(html != None):
            text_sizes['getHtml'] = len(html)
        else: return None,None,None,None
        start_time = time.time()
        withoutHtml = ParsingSiteService.cleanHtml(html)
        end_time = time.time()
        processing_times['cleanHtml'] = end_time - start_time        
        text_sizes['cleanHtml'] = len(withoutHtml)
        
        start_time = time.time()
        cleanByRegex = ParsingSiteService.clean_text(withoutHtml)
        end_time = time.time()
        processing_times['clean_text'] = end_time - start_time
        text_sizes['clean_text'] = len(cleanByRegex)
        
        start_time = time.time()
        cleanText = ParsingSiteService.wordnet_lemmatize_text(cleanByRegex)
        end_time = time.time()
        processing_times['wordnet_lemmatize_text'] = end_time - start_time
        text_sizes['wordnet_lemmatize_text'] = len(cleanText)

        start_time = time.time()
        lang = ParsingSiteService.detect_language(cleanText)
        end_time = time.time()
        processing_times['lang_detect'] = end_time - start_time
        
        total_time = sum(processing_times.values())
        processing_times['total'] = total_time
        
        # print(f"Processing times: {processing_times}")
        # print(f"Text sizes: {text_sizes}")
        
        
        return cleanText, html, lang, processing_times['total']