"""crawl key information from qiushi.com"""

import re
from urllib.parse import urljoin

from lxml import etree
import requests


class QiuShiCrawler:
    """Crawl information from qiushi.com"""
    def __init__(self):
        self.session = requests.Session()

        # re
        self.paragraph_re = re.compile(r'<p.*?>(.*?)</p>')
        self.img_src_re = re.compile(r'src="(.*?)"')
        self.font_tag_re = re.compile(r'<[/]?font.*?>')

        # xpath
        self.title_xpath = "string(//div[@class='highlight']/p[1])"
        self.author_xpath = "string(//div[@class='highlight']/p[2])"
        self.content_xpath = "//div[@class='highlight']/p[position()>2]"

    def fetch_info(self, url: str) -> dict:
        """fecth key information from qiushi.com"""
        result = {'content': []}

        # download html from internet
        resp = self.session.get(url=url)
        resp.encoding = 'utf-8'

        # extract paper content from html source code
        html = etree.HTML(resp.text)

        # get title and author of paper
        result['title'] = html.xpath(self.title_xpath)
        result['author'] = html.xpath(self.author_xpath)

        # get content of paper
        block = {}
        for paragraph in html.xpath(self.content_xpath):
            raw_code = etree.tostring(paragraph, encoding='utf-8').decode('utf-8')
            content = self.paragraph_re.search(raw_code).group(1).strip()
            content = self.font_tag_re.sub("", content).strip()
            
            if content.startswith('<img'):
                img_url = self.img_src_re.search(content).group(1)
                block['img_url'] = urljoin(url, img_url)
            else:
                block['text'] = content
                result['content'].append(block)
                block = {}

        return result


def main():
    """test function"""
    app = QiuShiCrawler()

    target_url = 'http://www.qstheory.cn/dukan/qs/2022-06/01/c_1128695652.htm'
    info = app.fetch_info(target_url)
    print(info)


if __name__ == '__main__':
    main()
