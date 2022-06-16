"""crawl key information from qiushi.com"""

from urllib.parse import urljoin
import os
import re

from lxml import etree
import qrcode
import requests

def add_backslash4space(string: str) -> str:
    """add a backslash before space

    LaTeX ignores spaces by default, unless there is a backslash befor it

    Args:
        string: a string which needs to be modified

    Returns:
        a string after modified
    """
    return string.replace(' ', r'\ ')

def get_img_name(url: str) -> str:
    """extract image name from url

    Args:
        url: target url

    Returns:
        image name
    """
    return url.split('/')[-1]


class QiuShiCrawler:
    """Crawl information from qiushi.com"""
    def __init__(self) -> None:
        # session used for connecting internet
        self.session = requests.Session()

        # regexp for extracting contents between <p> and </p>
        self.paragraph_re = re.compile(r'<p.*?>(.*?)</p>')
        # regexp for extracting url of image, which is a src attribute of img tag
        self.img_src_re = re.compile(r'src="(.*?)"')
        # regexp for dropping font tag
        self.font_tag_re = re.compile(r'<[/]?font.*?>')

        # xpath for extracting paper title
        self.title_xpath = "//h1/text()"
        # xpath for extracting paper volume
        self.volume_xpath = "//span[@class='appellation'][1]/text()"
        # xpath for extracting paper author
        self.author_xpath = "//span[@class='appellation'][2]/text()"
        # xpath for extracting paper contents, just keep not-empty or have a child
        self.content_xpath = "//div[@class='highlight']/p[text() or *]"

        # save QR code to this file path
        self.qrcode_path = 'qrcode.png'

        # make sure that there is a img folder in current working path
        self.img_folder = 'img'
        if not os.path.exists(self.img_folder) or not os.path.isdir(self.img_folder):
            os.mkdir(self.img_folder)

    def gen_qr(self, url: str) -> str:
        """generate QR code image from url

        Args:
            url: target url

        Returns:
            file path of the QR code image
        """
        # source: https://pypi.org/project/qrcode/
        qrcode_obj = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qrcode_obj.add_data(url)
        qrcode_obj.make(fit=True)

        # generate QR code image and save
        img = qrcode_obj.make_image(fill_color="black", back_color="white")
        img_path = os.path.join(self.img_folder, self.qrcode_path)
        img.save(img_path)

        return img_path

    def _download_img(self, url: str) -> str:
        """download image from internet and save it

        Args:
            url: url of image

        Return:
            path of image
        """
        image_bytes = self.session.get(url).content
        image_path = os.path.join(self.img_folder, get_img_name(url))
        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        return image_path

    def fetch_info(self, url: str) -> dict:
        """fecth key information from qiushi.com

        Args:
            url: the url of target paper,
                e.g.: http://www.qstheory.cn/dukan/qs/2022-06/15/c_1128739416.htm

        Returns:
            A dictionary filled with key information of the paper
        """
        # all things will be used for generating pdf files
        result = {'content': []}

        # get source code of html
        resp = self.session.get(url=url)
        resp.encoding = 'utf-8'
        html = etree.HTML(resp.text)

        # extract title from html source code
        paper_title = html.xpath(self.title_xpath)[0].strip()
        paper_title = re.sub(r'\s+', ' ', paper_title)
        result['title'] = add_backslash4space(paper_title)

        # extract volume from html source code
        paper_volume = html.xpath(self.volume_xpath)[0].strip()[3:]  # drop '来源：' from string
        result['volume'] = add_backslash4space(paper_volume)

        # extract author from html source code
        paper_author = html.xpath(self.author_xpath)[0].strip()[3:]  # drop '作者：' from string
        result['author'] = add_backslash4space(paper_author)

        # extract main content of the paper
        block = {}
        for paragraph in html.xpath(self.content_xpath):
            # skip everything before author (include author itself)
            content = paragraph.xpath('string(.)').strip()
            if content == paper_author:
                result['content'] = []
                continue

            # we need keep some tags for formating text, so extract the source code of tag
            raw_code = etree.tostring(paragraph, encoding='utf-8').decode('utf-8')
            # just keep content between <p> and </p>
            content = self.paragraph_re.search(raw_code).group(1).strip()
            # drop <font> and </font>
            content = self.font_tag_re.sub("", content).strip()

            if content.startswith('<img'):
                # if this tag is a img
                img_url = self.img_src_re.search(content).group(1)
                img_url = urljoin(url, img_url)
                block['img'] = self._download_img(img_url)
            else:
                block['text'] = add_backslash4space(content)
                result['content'].append(block)
                block = {}

        # if everything is OK, generate a QR code image
        result['qrcode'] = self.gen_qr(url)
        return result


def main():
    """test function"""
    app = QiuShiCrawler()

    target_url = 'http://www.qstheory.cn/dukan/qs/2022-06/15/c_1128739416.htm'
    info = app.fetch_info(target_url)
    print(info)


if __name__ == '__main__':
    main()
