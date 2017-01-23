from bs4 import BeautifulSoup
import urllib2
import urllib
import time
import pandas as pd
import os
import datetime
import dateutil
import signal
from likes_scrapper import TimeoutException
from likes_scrapper import handler

WRITE_MAIN_DIR = "./downloaded/"
control_file = './control_pics_scraper.csv'
update_freq = 5


def photos_getter(flickr_df):
    total = len(flickr_df)
    t = 0
    f = open(control_file, 'a')

    print('Scraping launched')
    for row in flickr_df.iterrows():

        edge = row[1][0]
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
                a = soup.find_all('meta')
                for num in range(0, len(a)):
                    if 'staticflickr' in str(a[num]):
                        link = a[num]["content"]
            except:
                link = ['NA']

            if link != ['NA']:
                try:
                    save_path = WRITE_MAIN_DIR + edge
                    #print edge + ' ' + link
                    download_image(str(link), str(save_path))
                    string = "{}, {}".format(edge, str(link))
                    f.write(string + '\n')
                except Exception as exc:
                    print(exc)
                time.sleep(1)



            time.sleep(1)
        else:
            string = "{}, {}".format(edge, 'NA')
            f.write(string + '\n')
        if not t % update_freq:
            now = datetime.datetime.now(dateutil.tz.tzlocal())
            timestamp = now.strftime('%H:%M:%S')
            print('[{}]{} / {}'.format(timestamp, t, total))

    f.close()



def download_image(source_url, dest_path):
    """Downloads an image from the source url and saves it to the directory.
    Images that were already downloaded are skipped automatically.

    Args:
        source_url The URL of the image.
        dest_dir The directory to save the image in.
    Returns:
        True if the image was downloaded
        False otherwise (including images that were skipped)
    """
    # image url to filepath


    if os.path.isfile(dest_path):
        # skip image that was already downloaded
        print("[Info] Skipped image '%s', was already downloaded" % (source_url))
        return False
    else:
        # create directory if it doesnt exist
        if not os.path.exists(dest_path):
        # download the image
            urllib.urlretrieve(source_url, dest_path)
        return True

def main():

    df_likes = pd.read_pickle('./photos_scrapper_edges.pkl')

    signal.signal(signal.SIGALRM, handler)

    if control_file.split('/')[-1] not in os.listdir('./'):
        photos_getter(df_likes)
    else:
        processed = pd.read_csv(control_file, index_col=0, header=None)
        processed_ixs = processed.index.astype(unicode)
        photos_getter(df_likes[~ df_likes.edges.isin(processed_ixs)])


if __name__ == '__main__':
    main()