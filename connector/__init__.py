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
    def commit_latest_B(self, new_content: str) -> None:
        pass
