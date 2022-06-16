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

        # xpath for extracting paper title
        self.title_xpath = "//h1/text()"
        # xpath for extracting paper volume
        self.volume_xpath = "//span[@class='appellation'][1]/text()"
        # xpath for extracting paper author
        self.author_xpath = "//span[@class='appellation'][2]/text()"
        # xpath for extracting paper contents, not empty paragraph or have a child
        self.content_xpath = "//div[@class='highlight']/p[text() or *]"

    def fetch_info(self, url: str) -> dict:
        """fecth key information from qiushi.com"""
        result = {'content': []}

        # get source code of html
        resp = self.session.get(url=url)
        resp.encoding = 'utf-8'
        html = etree.HTML(resp.text)

        # extract title from html source code
        paper_title = html.xpath(self.title_xpath)[0].strip()
        paper_title = re.sub(r'\s+', ' ', paper_title)
        result['title'] = paper_title

        # extract volume from html source code
        paper_volume = html.xpath(self.volume_xpath)[0].strip()[3:]  # drop '来源：' from string
        result['volume'] = paper_volume

        # extract author from html source code
        paper_author = html.xpath(self.author_xpath)[0].strip()[3:]  # drop '作者：' from string
        result['author'] = paper_author


        # get content of paper
        block = {}
        for paragraph in html.xpath(self.content_xpath):
            # skip everything before author (include author itself)
            content = paragraph.xpath('string(.)').strip()
            if content == paper_author:
                result['content'] = []
                continue

            raw_code = etree.tostring(paragraph, encoding='utf-8').decode('utf-8')
            # just keep content between <p> and </p>
            content = self.paragraph_re.search(raw_code).group(1).strip()
            # drop <font> and </font>
            content = self.font_tag_re.sub("", content).strip()
            
            if content.startswith('<img'):
                # if this tag is a img
                img_url = self.img_src_re.search(content).group(1)
                block['img_url'] = urljoin(url, img_url)
            else:
                block['text'] = content.replace(' ', r'\ ')
                result['content'].append(block)
                block = {}

        return result


def main():
    """test function"""
    app = QiuShiCrawler()

    target_url = 'http://www.qstheory.cn/dukan/qs/2022-06/15/c_1128739416.htm'
    info = app.fetch_info(target_url)
    print(info)


if __name__ == '__main__':
    main()
