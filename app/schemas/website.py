from typing import Optional
from pydantic import BaseModel,  HttpUrl

class WebSiteBase(BaseModel):
    url: Optional[HttpUrl]
    IABv2Category: Optional[str]
class WebSiteCreate(WebSiteBase):
    pass   
class WebSiteUpdate(WebSiteBase):
    category: Optional[str]
    htmlCode: Optional[str]
    preparedContent: Optional[str]
    # source: Optional[str]

class WebSiteInDB(WebSiteUpdate):
    id: Optional[int] = None
    
    class Config: 
        from_attributes = True

class WebSite(WebSiteInDB):
    pass
            