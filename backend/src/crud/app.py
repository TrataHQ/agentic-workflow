from .base import CRUDBase
from src.models.app import AppCore
from src.db.models.models import App

class CRUDApp(CRUDBase[App, AppCore, AppCore]):
    pass

app = CRUDApp(App)