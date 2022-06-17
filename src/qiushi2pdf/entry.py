"""provide a program entry"""

import argparse

from qiushi2pdf import QiuShiCrawler, PDFGenerator

class ArgParse:
    """parse command line arguments with argparse."""
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog='qiushi2pdf',
            description='A naive tool which convert qstheory.com article to pdf file',
            epilog=('You could find more important information in '
                    '[github](https://github.com/fengdongfa1995/qiushi2pdf).'),
        )

        parser.add_argument('url', help='the url of target article')

        self.args = vars(parser.parse_args())

def main():
    """program entry"""
    args = ArgParse().args

    # read target from user's input
    url = args['url']

    crawler = QiuShiCrawler()
    print('fetching paper contents...')
    paper_content = crawler.fetch_info(url)

    pdf_generator = PDFGenerator()
    print('generating tex file...')
    pdf_generator.gen_tex(paper_content)

    print('copying document file...')
    pdf_generator.copy_cls()

    print('generating pdf file...')
    pdf_generator.gen_pdf()

    print('job done!')


if __name__ == '__main__':
    main()
