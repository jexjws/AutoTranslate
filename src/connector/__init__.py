from abc import ABCMeta, abstractmethod


class Connector(metaclass=ABCMeta):
    @abstractmethod
    def get_old_A(self) -> str:
        pass

    @abstractmethod
    def get_latest_A(self) -> str:
        pass

    @abstractmethod
    def get_old_B(self) -> str:
        pass

    @abstractmethod
    def generate_latest_B(self, new_content: str) -> str:
        pass

class ConnectorFactory():
    def __init__(self):
        pass 
    @staticmethod
    def create(type:str,conf:dict) -> Connector:
        if type == "archwikicn":
            from .mediawiki import archwikicnPage
            return archwikicnPage(page_title = conf["page_title"])
        if type == "wikipedia-zh":
            from .mediawiki import archwikicnPage
            return archwikicnPage(page_title = conf["page_title"])
        else:
            raise ValueError("Unknown Connector type")
