from lxml import html
import PyPDF2 as pdf
from PyPDF2.utils import PdfReadError
import io
import itertools
import os
import requests
from requests import Timeout
import urllib
from urllib.error import HTTPError


URL = 'http://www.arxiv.org/'
DIR = '/media/momotkt/49a3ce70-7337-4aa3-bc3e-22cbaf3eae71/tome/pdfs/'


#id is in the form YYMM.NNNN
def pdf_scrape(id, verbose=True):
    link = URL + 'abs/' + id
    local_dir = DIR + id.split('.')[0] + '/'

    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)

    try:
        parsed = html.fromstring(requests.get(link, timeout=10).text)
        #takes the last page (-1 index)
    except (IndexError, IOError, Timeout):
        print('error')
        return
    except ValueError:
        xml = requests.get(link, timeout=10).text.encode('utf-8')
        parsed = html.fromstring(xml)

    try:
        pdf_url = URL + parsed.xpath("//div/div/ul/li[1]/a[@href]")[0].attrib['href'] + '.pdf'
        f_name = local_dir + pdf_url.split('/')[-1]
    except IndexError:
        print(id + " does not exist...")
        return

    if os.path.isfile(f_name):
        print(id + " already exists!")
        return

    if verbose:
        print(pdf_url)
    try:
        r = urllib.request.urlopen(pdf_url)
    except HTTPError:
        print("HTTP error...")
        return

    try:
        input_pdf = pdf.PdfFileReader(io.BytesIO(r.read()))

        output = pdf.PdfFileWriter()

        for page in range(input_pdf.getNumPages()):
            output.addPage(input_pdf.getPage(page))

        with open(f_name, 'wb') as writefile:
            output.write(writefile)

    except (AssertionError, PdfReadError, UnicodeEncodeError):
        return


if __name__ == "__main__":
    digits = [str(i) for i in range(10)]
    ids = list(itertools.product(digits, repeat=4))[::]
    for id in ids:
        pdf_scrape('1409.' + ''.join(id))