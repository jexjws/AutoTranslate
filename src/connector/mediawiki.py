import pywikibot
import re
from typing import TypedDict

from . import Connector

from abc import abstractmethod,ABCMeta


class mediawikiConnector(Connector,metaclass=ABCMeta):
    def __init__(self, page: pywikibot.Page, upstream_page: pywikibot.Page):
        self.page = page
        self.upstream_page = upstream_page

    def get_old_B(self) -> str:
        return self.page.text

    def get_latest_A(self) -> str:
        return self.upstream_page.text

    @abstractmethod
    def get_old_A(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_latest_B(self, new_content: str)  -> str:
        raise NotImplementedError


class archwikicnPage(mediawikiConnector):
    def __init__(self, page_title: str):
        # https://wiki.archlinuxcn.org/wiki/Special:%E7%89%88%E6%9C%AC
        site = pywikibot.Site(url="https://wiki.archlinuxcn.org/wzh/api.php")
        # https://wiki.archlinux.org/api.php
        upstream_site = pywikibot.Site(url="https://wiki.archlinux.org/api.php")

        self.page = pywikibot.Page(site, page_title)
        upstream_page = pywikibot.Page(
            upstream_site, self._translation_status_get()["upstream_title"]
        )

        super().__init__(self.page, upstream_page)

    class TranslationStatus(TypedDict):
        upstream_title: str # 上游文档名
        upstream_ver: int # 上游文档版本

    def _translation_status_get(self) -> TranslationStatus:
        pattern = r"\{\{翻译状态\|([^|]+)\|([^|]+)\|([^}]+)\}\}"
        match = re.search(pattern, self.page.text)

        if match:
            upstream_title = match.group(1).strip()  # 提取 "Installation guide"
            #upstream_date = match.group(2).strip() # 提取 "2024-03-01"
            upstream_ver = match.group(3).strip()  # 提取 "817521"
        else:
            print("！未找到翻译状态模板")
            upstream_title = input("请手动输入上游文档名: ")
            upstream_ver = input("请输入上游旧文档版本号: ")
        return {"upstream_title": upstream_title, "upstream_ver": int(upstream_ver)}

    def _translation_status_update(self,new_content:str) -> str:
        pattern = r"\{\{翻译状态\|([^|]+)\|([^|]+)\|([^}]+)\}\}"
        match = re.search(pattern, new_content)
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        if match:
            # Extract the upstream title and version number
            upstream_title = match.group(1).strip()
            #old_date = match.group(2).strip()
            #old_version = match.group(3).strip()
            #
            # Replace the old date and version with the new ones
            new_translation_status = f"{{{{翻译状态|{upstream_title}|{current_date}|{self.upstream_page.latest_revision_id}}}}}"
            return re.sub(pattern, new_translation_status, new_content)
        else:
            print("未找到翻译状态模板，跳过更新翻译状态。")
            return new_content

    def get_old_A(self) -> str:
        return self.upstream_page.getOldVersion(int(self._translation_status_get()["upstream_ver"]))

    def generate_latest_B(self, new_content: str) -> str:
        return self._translation_status_update(new_content)
