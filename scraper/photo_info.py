#!/usr/bin/env python
# @Author: Maria Elena Villaobos Ponte
# @Date:   2016-11-07 10:32:30
# @Last Modified by:   Maria Elena Villalobos Ponte
# @Last Modified time: 2016-11-17 19:20:56
import json
import time
import traceback
import flickr_scrape as scrape
from datetime import datetime, date, timedelta

def get_photos(flickr, db_photos):
    """Scrape photos from Flickr and stores it in MongoDB collection.

    Args:
        flickr (flickrapi.FlickrAPI): Instance of the flickrapi class
        db_photos (pymongo.collection.Collection): MongoDB collection to store scraped info
    """
    min_date = datetime.strptime('2015-11-17', "%Y-%m-%d").date()
    year_delta = timedelta(days=365)
    request_delta = timedelta(days=5)
    num_calls = 0
    per_page = 10
    total_inserted = 0

    current_date = min_date
    max_date = min_date + year_delta
    while current_date <= max_date:
        page_num = 1
        total_pages = float('inf')
        end_date = current_date + request_delta

        print('current date', current_date, 'end date', end_date)

        while page_num <= total_pages:
            all_photos = []
            try:
                photos_search = flickr.photos.search(per_page=per_page,
                                                     page = page_num,
                                                     min_taken_date=current_date.strftime("%Y-%m-%d"),
                                                     max_taken_date=end_date.strftime("%Y-%m-%d"),
                                                     place_id='eFEYI5ZQUL_VqqpXvg',  # Manhattan bound box
                                                     has_geo=True,
                                                     media='photos')
                search_response = json.loads(photos_search)

                if page_num == 1:
                    # Get total number of pages and photos from request
                    total_pages = int(search_response["photos"]["pages"])
                    total_photos = int(search_response["photos"]["total"])

                photos_search = search_response['photos']['photo']
                for photo_walk in photos_search:
                    all_photos.append({'photo_id': photo_walk.get('id'),
                                       'secret': photo_walk.get('secret'),
                                       'owner': photo_walk.get('owner')})
                    num_calls += 1

                photo_jsons = []
                for photo in all_photos:
                    print("Getting photo info", photo['photo_id'])
                    photo_info = flickr.photos.getInfo(photo_id=photo['photo_id'], secret=photo['secret'])
                    photo_json = json.loads(photo_info)['photo']

                    # Insert photo info JSON in Mongo Database
                    photo_jsons.append(photo_json)

                num_calls += len(all_photos)
                page_num += 1

            except:
                traceback.print_exc()
                print("Sleeping and restarting num_calls")
                time.sleep(10)
                num_calls = 0
                continue
            else:
                if photo_jsons:
                    db_photos.insert_many(photo_jsons)
                    num_inserted = len(photo_jsons)
                    total_inserted += num_inserted
                    print("inserted:", num_inserted,
                          "page:", page_num - 1,
                          "of", total_pages,
                          "total requests:", num_calls,
                          "total inserted:", total_inserted,
                          "of:", total_photos)

        current_date = end_date + timedelta(days=1)



def main():
    sys.stdout = scrape.Unbuffered(sys.stdout)
    get_photos(scrape.flickr, scrape.db_photos)


if __name__ == "__main__":
    main()
