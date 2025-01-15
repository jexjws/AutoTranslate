import pywikibot
import re
import difflib
from typing import TypedDict


from abc import ABC, abstractmethod


class TranslationStatus(TypedDict):
    upstream_title: str
    upstream_ver: int

class mediawikiTranslator(ABC):
    def __init__(self, page: pywikibot.Page, upstream_page: pywikibot.Page):
        self.page = page
        self.upstream_page = upstream_page

    def get_old_B(self) -> str:
        """
        获取现在的翻译后文段
        """
        return self.page.text

    @abstractmethod
    def get_latest_A(self) -> str:
        """
        获取 现在的上游文段 和 现在的文段所基于的上游文段 之间的diff。
        """
        # 获取当前上游页面的内容
        current_upstream_content = self.upstream_page.text

        # 获取当前页面的内容
        current_content = self.upstream_page.getOldVersion(self.translation_status_get()["upstream_ver"])

        # 使用 difflib 生成差异
        diff = difflib.unified_diff(
            current_content.splitlines(),
            current_upstream_content.splitlines(),
            fromfile="旧版原文页面",
            tofile="新版原文页面",
            lineterm="",
        )

        # 将差异转换为字符串
        diff_str = "\n".join(diff)
        return diff_str



    @abstractmethod
    def translation_status_get(self) -> TranslationStatus:
        """
        获取 翻译状态
        """
        raise NotImplementedError

    def commit_latest_B(self, new_content: str) -> None:
        """
        提交更新后的内容
        """
        self.page.text = new_content
        self.page.save(summary="同步上游文档")


class archlinuxcnPage(mediawikiTranslator):
    def __init__(self, page_title: str):
        site = pywikibot.Site(url="https://wiki.archlinuxcn.org/wzh/api.php")
        upstream_site = pywikibot.Site(url="https://wiki.archlinux.org/api.php")

        self.page = pywikibot.Page(site, page_title)
        upstream_page = pywikibot.Page(
            upstream_site, self.translation_status_get()["upstream_title"]
        )

        super().__init__(self.page, upstream_page)

    def translation_status_get(self) -> TranslationStatus:
        pattern = r"\{\{翻译状态\|([^|]+)\|([^|]+)\|([^}]+)\}\}"
        match = re.search(pattern, self.page.text)

        if match:
            upstream_title = match.group(1).strip()  # 提取 "Installation guide"
            upstream_ver = match.group(3).strip()  # 提取 "817521"
            print(f"上游文档名: {upstream_title}")
            print(f"上游文档旧版本号: {upstream_ver}")
        else:
            raise ValueError("未找到翻译状态模板")
        return {"upstream_title": upstream_title, "upstream_ver": int(upstream_ver)}


def main():
    c = archlinuxcnPage(page_title="安装指南")

    print(c.get_upstream_diff())


if __name__ == "__main__":
    main()
