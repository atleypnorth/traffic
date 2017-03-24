from multiprocessing import Pool
import cgi
import os
import zipfile

import requests # allows for easy downloading
from bs4 import BeautifulSoup # parses HTML pages and makes it easy to extract data from them


def download(url):
    print('Downloading %s' % url)
    directory = 'midas'
    r = requests.get(url)
    params = cgi.parse_header(r.headers['content-disposition'])[1]
    print('saving to %s', params['filename'])
    zip_file = os.path.join(directory, params['filename'])
    # We download the actual data in chunks instead of all in one go
    with open(zip_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    # Now unzip into the same directory
    print('Unzipping from %s' % zip_file)
    with zipfile.ZipFile(zip_file, 'r') as unzip:
        unzip.extractall(path=directory)
    os.unlink(zip_file)


if __name__ == '__main__':
    server = 'http://tris.highwaysengland.co.uk'
    main_page = requests.get('%s/home/LowerLevelDetails?section=trafficflowdata&name=2014' % server)

    soup = BeautifulSoup(main_page.text, 'html.parser')

    to_download = []
    for link in soup.find_all('a'):
        if link.get('href').startswith('/download'):
            to_download.append('%s%s' % (server, link.get('href')))

    print('%d files to download' % len(to_download))

    with Pool(4) as pool:
        pool.map(download, to_download)
