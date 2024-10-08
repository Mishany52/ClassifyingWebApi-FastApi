# Словарь с регулярными выражениями и заменами
regexDict = {
    r'(?:\\n|\n)+': ' ',  # Перевод строки
    r'(\\r)+': ' ',  # Возврат каретки
    r'\$\d+(,\d{3})*(\.\d{2})?': ' ',  # Деньги $9.95 $99. $99 $1,299.95
    r'\+\d*|[\d:;"“*™#®—•→<>\\|×&\-°©%{2}·\(\)\{\}\[\]?\/]': ' ',  # Цифры и другие символы
    r'"': ' ',  # Двойные кавычки
    r'(http?:\/\/|https?:\/\/|ftp:\/\/(\w+(:.+?)?@)?)([-a-z0-9]+\.)+[a-z]{2,4}': ' ',  # URL
    r'(?<=[a-z])(?=[A-Z])': ' ',  # Разделение слов catDog dogCat
    r'(?<=[а-яё])(?=[А-ЯЁ])': ' ',  # Разделение слов котСобака СобакаКот
    r'\w+@\w+\.\w+': ' ',  # Почта
    r'(?<=[а-я])(?=[А-Я])|(?<=[А-Я])(?=[А-Я][а-я])': ' ',  # Разделение слов
    r"\s+(?=(?:[,'.?!:;…]))": '',  # Удаление пробелов перед знаками препинания
    r'(?<=[.,;:!?])[.,;:!?]+': '',  # Удаление повторов
    r'\xa0': ' ',  # Неразрывный пробел
    r'[\s]{2,}': ' ',  # Пробелы
    r'\s+': ' ',  # Пробелы
    r'(?i)@[a-z0-9_]+': '',  # Упоминания пользователей
    r'\[[^()]*\]': '',  # Текст в квадратных скобках
    r'\d+': '',  # Цифры
    r'[^\w\s]': '',  # Невалидные символы
    r'(?:@\S*|#\S*|http(?=.*://)\S*)': ''  # Упоминания пользователей, хэштеги, URL
}