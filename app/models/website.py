from sqlalchemy import Column, Integer, String

from app.db.base_class import Base

class WebSite(Base): 
    __tablename__ = "website"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    IABv2Category = Column(String)
    category = Column(String)
    content = Column(String)
    preparedContent = Column(String)
    top_category = Column(String)
    # source = Column(String(256), nullable=True) #Сторонний датасет или из нашего приложения
    



