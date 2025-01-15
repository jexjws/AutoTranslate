
from connector.mediawiki import archlinuxcnPage


def main():
    c = archlinuxcnPage(page_title="安装指南")

    print(c.get_latest_A())


if __name__ == "__main__":
    main()
