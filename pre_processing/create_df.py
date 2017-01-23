""""
This script is to run in the CIMS server. It calls the MongoDB where we stored the Flickr photos metadata and
retrieves the relevant columns including comments, number of photos, tags, etc. It stores it in a pandas Dataframe
and saves it as a pickle
"""
import pymongo as pm
import pandas as pd
client = pm.MongoClient('crunchy6.cims.nyu.edu')
db = client.sightWalk
db_photos = db.photos


photos = []
for photo in db_photos.find():
    mongo_id = photo['_id']
    try:
        lon = float(photo['location']['longitude'])
        lat = float(photo['location']['latitude'])
        neigh = photo['location']['neighbourhood']['_content']
    except:
        lon, lat, neigh = None, None, None
    has_people = photo['people']['haspeople']
    date = photo['dateuploaded']
    owner_id = photo['owner']['nsid']
    owner_location = photo['owner']['location']
    id = photo['id']
    title = photo['title']['_content']
    tags = photo['tags']['tag']
    num_tags = len(tags)
    tags = [tag['raw'] for tag in tags]
    num_comments = int(photo['comments']['_content'])
    description = photo['description']['_content']
    views = int(photo['views'])
    date_taken = photo['dates']['taken']
    urls_list = photo['urls']['url']
    url = [url['_content'] for url in urls_list if url['type']=='photopage'][0]
    photos.append([mongo_id, id, lon, lat, neigh, has_people, date, owner_id, owner_location, title, num_tags, tags, num_comments, description, views, date_taken, url])

photos_df = pd.DataFrame(photos)
photos_df.columns = [['mongo_id', 'id', 'lon', 'lat', 'neigh', 'has_people', 'date', 'owner_id', 'owner_location', 'title', 'num_tags', 'tags', 'num_comments', 'description', 'views', 'date_taken', 'url']]
pd.to_pickle('photos_df')