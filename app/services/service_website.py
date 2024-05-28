from typing import List, Mapping

from fastapi import HTTPException, status
from app.services.base import CRUDBase
from app.models.website import WebSite
from app.schemas.website import WebSiteUpdate, WebSiteCreate

from sqlalchemy.ext.asyncio import AsyncSession

import pandas as pd
from numpy import genfromtxt

from app.services.regex_dict import regexDict
from pydantic import AnyUrl
from bs4 import BeautifulSoup
import requests
import re


class WebSiteService(CRUDBase[WebSite, WebSiteCreate, WebSiteUpdate]):
    @staticmethod
    def load_data(fileName: str):
        data = genfromtxt(fileName, delimiter=',', converters={0: lambda s: str(s)})
        return data.tolist()

    @staticmethod
    def editCSVandSave(fileName: str, dropColumn: List[int | str] = None):
        df = pd.read_csv(fileName, escapechar='\\', header=None)
        df.drop([0, 1, 4, 5, 6], axis=1, inplace=True)

        df = df.set_axis(['url', 'IABv2Category', ], axis=1)
        df['top_category'] = df['IABv2Category'].apply(lambda x: x.split('/')[1].replace('&', 'and'))
        df['url'] = df['url'].apply(lambda x: 'https://' + x)
        df.to_csv('preparedDataSetEn.csv', index=False)
        return df[:5]


    @staticmethod
    def getHtml(url: AnyUrl, params='', headers: Mapping[str, str | bytes] | None = '') -> str:
        try:
            r = requests.get(url, headers=headers, params=params)
            print(r)
            if r.status_code == 200:
                html_code = r.text  # выгружаем html code со страницы
                return html_code
            else:
                return ''
        except requests.exceptions.SSLError as e:
            # Если возникает ошибка SSL, делаем запрос через HTTP
            if 'SSLEOFError' in str(e):
                http_url = str(url).replace('https://', 'http://')
                r = requests.get(http_url)
                html_code = r.text
                # Обрабатываем успешный ответ
                return html_code
            else:
                # Если другая ошибка SSL, выводим сообщение об ошибке
                print("SSL Error:", e)
        except Exception as e:
            print(e)

    @staticmethod
    def getContent(html_code: str):
        try:
            soup = BeautifulSoup(html_code, 'html.parser')  # Парсим html code
            return soup.get_text()
        except Exception as e:
            print(e)

    @staticmethod
    def processTextWithRegex(text: str):
        processed_text = text  # Начальное значение processed_text
        for regex_pattern, replacement in regexDict.items():
            processed_text = re.sub(regex_pattern, replacement, processed_text)
        processed_text = processed_text.strip()  # Применение lower() и удаление лишних пробелов
        return processed_text

    @staticmethod
    def remove_non_russian_letters(text):
        # Удаляем все символы, кроме русских букв и пробелов
        regex_pattern = re.compile('[^а-яА-ЯёЁ ]')
        cleaned_text = regex_pattern.sub('', text)
        # Заменяем повторяющиеся пробелы на одиночные
        cleaned_text = re.sub(r'[\s]{2,}', ' ', cleaned_text)
        return cleaned_text

    def getPreparedTextByUrl(self, url: AnyUrl, params='', headers='') -> str:
        try:
            htmlCode = self.getHtml(url=url, params=params, headers=headers)
            if not htmlCode:
                raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f"Parsing  url= {url} failed")
            content = self.getContent(htmlCode)
            preparedText = self.processTextWithRegex(content)
            return preparedText
        except Exception as e:
            print(e)

    async def uploadCSVtoDB(self, db: AsyncSession, fileName: str):
        try:
            data = pd.read_csv(fileName, delimiter=',', skiprows=1)
            for row in data.itertuples(index=False):
                record = self.model(**{
                    'url': row[0],
                    'IABv2Category': row[1],
                    'top_category': row[2],
                })
                db.add(record)  # Добавляем все записи
            await db.commit()  # Пытаемся зафиксировать все записи
        except Exception as e:
            await db.rollback()  # Откатываем изменения в случае ошибки
            raise e
        
    async def getWebSiteByUrl(self, db: AsyncSession, obj_url: AnyUrl):
        obj_db = await db.query(self.model).filter(self.model.url == obj_url).first()
        if not obj_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"WebSite with url {obj_url} not found")
        return obj_db

    def savePreparedTextInDn(self, db: AsyncSession, preparedText: str, url: AnyUrl):
        obj_db = self.getWebSiteByUrl(db=db, obj_url=url)
        # Доделать обновления сайта


webSite = WebSiteService(WebSite)
