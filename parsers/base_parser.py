from abc import ABC, abstractmethod
from typing import List
from models.lesson import Lesson

class BaseParser(ABC):

    @abstractmethod
    def parse(self, source) -> List[Lesson]:
        pass

    @abstractmethod
    def validate(self, lessons: List[Lesson]) -> bool:
        pass