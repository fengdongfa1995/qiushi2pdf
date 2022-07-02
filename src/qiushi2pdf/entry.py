"""provide a program entry"""

import argparse

from qiushi2pdf import QiuShiCrawler, PDFGenerator
    
crawler = QiuShiCrawler()
pdf_generator = PDFGenerator()

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
        parser.add_argument(
            '-l', '--list', action='store_true',
            help='try to find a article list and download all articles.',
        )

        self.args = vars(parser.parse_args())

def download_single_article(url: str) -> None:
    """download an article from internet
    
    Args:
        url: article url
    """
    print(f'fetching paper contents from {url}')
    paper_content = crawler.fetch_info(url)
    if not paper_content:
        return

    print('generating tex file...')
    pdf_generator.gen_tex(paper_content)

    print('copying document file...')
    pdf_generator.copy_cls()

    print('generating pdf file...')
    pdf_generator.gen_pdf()
    # repeat to draw QR code
    pdf_generator.gen_pdf()

    print('cleaning temporary file...')
    pdf_generator.clean_rubbish()

def main():
    """program entry"""
    args = ArgParse().args

    # read target from user's input
    if args['list']:
        for url in crawler.fetch_urls(args['url']):
            download_single_article(url)
    else:
        download_single_article(args['url'])

    print('job done!')


if __name__ == '__main__':
    main()
