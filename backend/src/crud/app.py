from .base import CRUDBase
from backend.src.models.app import AppCore
from backend.src.db.models.models import App

class CRUDApp(CRUDBase[App, AppCore, AppCore]):
    pass

app = CRUDApp(App)