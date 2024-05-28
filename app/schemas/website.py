from typing import Optional, Sequence
from pydantic import BaseModel, AnyUrl


class WebSiteBase(BaseModel):
    url: Optional[AnyUrl]
    IABv2Category: Optional[str]


class WebSiteCreate(WebSiteBase):
    pass


class WebSiteUpdate(WebSiteBase):
    category: Optional[str]
    content: Optional[str]
    preparedContent: Optional[str]
    top_category: Optional[str]


class WebSiteInDB(WebSiteUpdate):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class WebSite(WebSiteInDB):
    pass


class WebSiteSearchResults(BaseModel):
    results: Sequence[WebSite]
