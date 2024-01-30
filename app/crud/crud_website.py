from app.crud.base import CRUDBase
from app.models.website import WebSite
from app.schemas.website import WebSiteUpdate, WebSiteCreate

class CRUDWebSite(CRUDBase[WebSite, WebSiteCreate, WebSiteUpdate]):
    ...
webSite = CRUDWebSite(WebSite) 