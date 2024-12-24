from .base import CRUDBase
from backend.src.models.connection import ConnectionCore
from backend.src.db.models.models import Connection

class CRUDConnection(CRUDBase[Connection, ConnectionCore, ConnectionCore]):
    pass

connection = CRUDConnection(Connection)