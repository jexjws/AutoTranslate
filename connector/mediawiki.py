import pywikibot
import re
from typing import TypedDict

from . import Connector

from abc import abstractmethod


class mediawikiConnector(Connector):
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

    def commit_latest_B(self, new_content: str) -> None:
        self.page.text = new_content
        #self.page.save(summary="同步上游文档")


class archlinuxcnPage(mediawikiConnector):
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
            upstream_date = match.group(2).strip() # 提取 "2024-03-01"
            upstream_ver = match.group(3).strip()  # 提取 "817521"
            print(f"上游文档名: {upstream_title}")
            print(f"上游文档旧版本号: {upstream_ver}")
        else:
            raise ValueError("未找到翻译状态模板")
        return {"upstream_title": upstream_title, "upstream_ver": int(upstream_ver)}
    
    def _translation_status_update(self,new_content:str) -> None:
        pattern = r"\{\{翻译状态\|([^|]+)\|([^|]+)\|([^}]+)\}\}"
        match = re.search(pattern, new_content)
        if match:
            # Extract the upstream title and version number
            upstream_title = match.group(1).strip()
            #old_date = match.group(2).strip()
            #old_version = match.group(3).strip()
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Replace the old date and version with the new ones
            new_translation_status = f"{{{{翻译状态|{upstream_title}|{current_date}|{self.upstream_page.latest_revision_id}}}}}"
            self.page.text= re.sub(pattern, new_translation_status, new_content)
        else:
            print("Translation status not found")
            self.page.text = new_content

    def get_old_A(self) -> str:
        return self.upstream_page.getOldVersion(int(self._translation_status_get()["upstream_ver"]))
    
    def commit_latest_B(self, new_content: str) -> None:
        # Update the page content and save it
        self._translation_status_update(new_content)
        with open("latest1B.txt", "w", encoding="utf-8") as file:
            file.write(self.page.text)
        #self.page.save(summary="同步上游文档")

