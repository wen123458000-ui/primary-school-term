from abc import ABC, abstractmethod
from datetime import datetime
from permission import Permission

# 抽象父类
class FSNode(ABC):
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.permissions = {Permission.READ, Permission.WRITE, Permission.EXECUTE}

    @abstractmethod
    def get_size(self):
        pass