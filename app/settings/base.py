from abc import ABC, abstractmethod

class BaseSettings(ABC):
    @property
    @abstractmethod
    def LOG_LEVEL(self):
        pass
