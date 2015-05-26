import requests
import re
import os
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from mimetypes import guess_extension
from fish import ProgressFish

BASE_URL = 'http://www.metacasts.tv/'
SESSION_COOKIE = 'PASTE-YOUR-SESSION-HERE'

class VideoEntry:
    def __init__(self, title, date, href):
        self.title = title
        self.date = date
        self.href = href 

    def get_download_url(self):
        return BASE_URL+self.href+'/download'

    def get_save_name(self):
        return "{0} - {1}".format(datetime.strftime(self.date, '%Y-%m-%d'), self.title)\
                          .replace(':', '-')\
                          .replace('/', '-')

def get_video_entries():
    index_html = requests.get(BASE_URL+'casts?per_page=200')
    soup = BeautifulSoup(index_html.text)
    links = soup.find_all('div', {'class': 'buffer alt tight clearfix'})
    entries = []

    for link in links:
        anchor = link.find('a')
        title = anchor.find('span', {'class': ''}).get_text().strip()
        date = anchor.find('i', {'class': 'glyphicon glyphicon-calendar'}).next_sibling.strip()
        href = anchor.get('href')
        entries.append(VideoEntry(title, 
                                  datetime.strptime(re.sub(r"(st|nd|rd|th),", ",",date),'%B %d, %Y'), 
                                  href))

    return entries

def download_url(url, save_as):
    r = requests.get(url, cookies = {'_metacasts_session': SESSION_COOKIE}, stream=True)
    file_size = int(r.headers['content-length'])
    mime_type = r.headers['content-type']
    downloaded_bytes = 0

    file_name = save_as+guess_extension(mime_type)
    file_mode = 'wb'

    if( os.path.exists(file_name) ):
        existing_size = os.path.getsize(file_name)
        print 'size is {0} vs {1}'.format(existing_size, file_size)
        if( os.path.getsize(file_name) == file_size ):
            print file_name+" already exists. Skipping..."
            return
        else:
            print "File incomplete. Resuming..."
            file_mode = 'ab'
            r = requests.get(url, 
                             cookies = {'_metacasts_session': SESSION_COOKIE}, 
                             headers = {'Range': 'bytes={0}-'.format(existing_size)},
                             stream=True)
            downloaded_bytes = existing_size

            if( int(r.headers['content-length']) != file_size - existing_size ):
                print "File size mismatch. Reset download."
                os.remove(file_name)
                file_mode = 'wb'
                downloaded_bytes = 0
                

    with open(file_name, file_mode) as f:
        print "Downloading {0}...".format(file_name)
        pf = ProgressFish(total=file_size)
        for index, chunk in enumerate(r.iter_content(chunk_size=128*1024)):
            if chunk:
                downloaded_bytes += len(chunk)
                f.write(chunk)
                f.flush()
                pf.animate(amount=downloaded_bytes)

        print "{0} finished download".format(file_name)


def main():
    print "Getting list of videos"
    videos = get_video_entries()
    print "Done. {0} videos found.".format(len(videos))

    start = 1
    end = len(videos) + 1

    if( len(sys.argv) == 3 ):
        try:
            start = int(sys.argv[1])
            end = int(sys.argv[2])
        except TypeError:
            sys.exit("Params must be an integer")

        print "Downloading video {0} - {1}.".format(start, end)
    else:
        print "Downloading all video"

    for index, video in enumerate(videos[start-1:end]):
        print "Downloading video #{0}: {1}".format(start+index, video.get_save_name())
        download_url(video.get_download_url(), video.get_save_name())

if __name__ == '__main__':
    main()
