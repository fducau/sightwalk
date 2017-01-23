from bs4 import BeautifulSoup
import urllib2
import re
import time
import pandas as pd
import os
import datetime
import dateutil
import signal


class TimeoutException(Exception):
    pass


def handler(signum, frame):
    """Register an handler for the timeout"""
    print "Timeout reached!"
    raise TimeoutException()


update_freq = 5
filename = './file.csv'


def likes_getter(flickr_df):
    total = len(flickr_df)
    t = 0
    f = open(filename, 'a')

    print('Scraping launched')
    for row in flickr_df.iterrows():

        id = row[1][0]
        url = row[1][1]
        t += 1

        todoOK = 0
        while not todoOK:
            todoOK = 1
            try:
                signal.alarm(10)
                pageFile = urllib2.urlopen(str(url))
                signal.alarm(0)
            except KeyboardInterrupt:
                raise
            except urllib2.HTTPError:
                pageFile = None
            except TimeoutException:
                pageFile = None
                print('Timeout in: {}'.format(url))
            except:
                print('Stucked, retrying... {}'.format(url))
                time.sleep(5)
                todoOK = 0
            else:
                todoOK = 1

        if pageFile is not None:
            try:
                signal.alarm(10)
                pageHtml = pageFile.read()
                pageFile.close()
                signal.alarm(0)
            except:
                pass

            try:
                soup = BeautifulSoup("".join(pageHtml), 'lxml')
                sAll = soup.findAll('span', {'class': 'fave-count-label'})
                number = re.findall(r'\d+', str(sAll[0]))
            except:
                number = ['NA']

            string = "{}, {}".format(id, str(number[0]))
            f.write(string + '\n')

            time.sleep(1)
        else:
            string = "{}, {}".format(id, 'NA')
            f.write(string + '\n')
        if not t % update_freq:
            now = datetime.datetime.now(dateutil.tz.tzlocal())
            timestamp = now.strftime('%H:%M:%S')
            print('[{}]{} / {}'.format(timestamp, t, total))

    f.close()


if __name__ == '__main__':
    df_likes = pd.read_pickle('df_new2')

    signal.signal(signal.SIGALRM, handler)

    if filename.split('/')[-1] not in os.listdir('./'):
        likes_getter(df_likes)
    else:
        saved = pd.read_csv(filename, index_col=0, header=None)
        saved_ixs = saved.index.astype(unicode)
        likes_getter(df_likes[~ df_likes.id.isin(saved_ixs)])
