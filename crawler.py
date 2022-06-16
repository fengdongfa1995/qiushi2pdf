# description: crawl key information from qiushi.com
# author: Feng Dongfa
# email: feng@dongfa.pro

from lxml import etree
import requests


class QiuShiCrawler:
    def __init__(self):
        self.session = requests.Session()

        # xpath
        self.whole_paper_xpath = "//div[@class='highlight']"
        self.title_xpath = "string(.//p[1])"
        self.author_xpath = "string(.//p[2])"

    def fetch_info(self, url: str) -> dict:
        """fecth key information from qiushi.com"""
        result = {}

        # download html from internet
        resp = self.session.get(url=url)
        resp.encoding = 'utf8'

        # extract paper content from html source code
        html = etree.HTML(resp.text)
        paper_content = html.xpath(self.whole_paper_xpath)[0]

        # extract key information from paper content
        result['title'] = paper_content.xpath(self.title_xpath)
        result['author'] = paper_content.xpath(self.author_xpath)

        # check result
        return result



def main():
    app = QiuShiCrawler()

    target_url = 'http://www.qstheory.cn/dukan/qs/2022-06/01/c_1128695652.htm'
    info = app.fetch_info(target_url)
    print(info)


if __name__ == '__main__':
    main()
