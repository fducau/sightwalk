import pandas as pd
import numpy as np

default_list = [' NEW YORK', ' NJ', ' NY', ' NYC', ' New York', ' Zoo York City', ' ny', 'ASTORIA NY',
                'BROOOOOOOOOKLYNNNN!!!!', 'Brooklyn. NY', 'NEW YORK', 'NY', 'NYC', 'New York', 'New York ',
                'New York -- for the most part.',
                'New York / Paris ', 'New York City', 'New York City & Long Island', 'New York City / Brooklyn',
                'New York City baby!',
                'new york', 'new york city', 'nyc', '  NY', ' NY', ' NY ', ' NY 10003', ' NY 10065', ' NYC',
                ' New York',
                ' New York 11787', ' New York City', ' in New York', ' ny', 'Astoria', 'Astoria - NY', 'BROOKLYN',
                'Bronx',
                'Brooklyn', 'Brooklyn/Paris', 'Manhattan', 'Manhattan NY', 'NEW YORK', 'NEW YORK CITY', 'NICE', 'NJ',
                'NRW', 'NY', 'NY / NJ', 'NYC', 'NYC ', 'NYC Metro ', 'NYC Metropolitan area', 'NYC!', 'New Yok',
                'New York',
                'New York ', 'New York & Los Angeles ', 'New York City', 'New York City ', 'New York City Metro Area',
                'New York NY',
                'New York and Austin', 'New York city', 'New York/Atlanta', 'New York/Gainesvilee',
                'New york / Brooklyn',
                'QUEENS NY', 'Queens', 'The City of New York', 'nYc', 'new york', 'new york city', 'none', 'nyc',
                'yonkers', ' New York',
                ' Brooklyn', ' NY', ' NYC', ' New York', 'New York', 'New York City', 'New York City & Hancock', 'NYC ',
                'NYC | Roxbury', 'new york', 'New York']


def data_preprocesser(likes_csv_path, photos_pickle_path, ny_list=default_list):
    """ Receives:
    - likes_csv is scrapped likes by photo
    - photos_pickle is a pickled dataframe with photos features (already mapped to edges)
    - ny_list is a list of string corresponding to NYC locations
    Returns:
    - PD Dataframe with processed metrics by edge
    """
    # Read Likes CSV and pre-process
    likes = pd.read_csv(likes_csv_path, header=None)
    likes.columns = [['idm', 'likes']]
    likes.idm = likes.idm.astype(str)
    likes.likes = likes.likes.str.strip()
    likes = likes[likes.likes != 'NA']
    likes.drop_duplicates('idm', inplace=True)

    # Read photos Pickle

    df_manhattan = pd.read_pickle(photos_pickle_path)
    to_exclude = set(df_manhattan[(df_manhattan.lon == -74.0064) & (df_manhattan.lat == 40.7142)].id)
    df_manhattan = df_manhattan[~df_manhattan.id.isin(to_exclude)]

    # Merge both by photo ID
    manhattan_likes = df_manhattan.merge(likes, how='left', left_on='id', right_on='idm',
                                         suffixes=('_manhattan', '_likes'), copy=True)

    # Cast likes to numeric
    manhattan_likes.likes = pd.to_numeric(manhattan_likes.likes)

    # Split Account holder location by comma
    func = lambda x: pd.Series([i for i in reversed(x.split(','))])
    rev = manhattan_likes.owner_location.apply(func)

    # Get dataframe of photos from NYC accounts
    set_ny = set(ny_list)
    rev['is_ny'] = 0
    rev.loc[rev[rev[0].isin(set_ny)].index, 'is_ny'] = 1
    rev.loc[rev[rev[1].isin(set_ny)].index, 'is_ny'] = 1
    rev.loc[rev[rev[2].isin(set_ny)].index, 'is_ny'] = 1
    rev.loc[rev[rev[3].isin(set_ny)].index, 'is_ny'] = 1
    rev.loc[rev[rev[4].isin(set_ny)].index, 'is_ny'] = 1

    # Append the new NYC market to original Manhattan Dataframe
    manhattan_likes.ix[rev[rev.is_ny == 1].index, 'is_ny'] = 1

    # Get the count of photos by edge
    photos_count = manhattan_likes.groupby('edges').count().id
    # Get the total number of comments and views by edge
    num_comments_views_likes = manhattan_likes.groupby('edges').sum()[['num_comments', 'views', 'likes']]
    # Get the count of photos by edge for NY users
    num_comments_views_likes_ny = manhattan_likes[manhattan_likes.is_ny == 1].groupby('edges').sum()[
        ['num_comments', 'views', 'likes']]
    # Get the total number of comments and views by edge for NY users
    photos_count_ny = manhattan_likes[manhattan_likes.is_ny == 1].groupby('edges').count().id
    # Get the top photo for each edge according to number of views.
    top_photos = manhattan_likes.ix[manhattan_likes.groupby('edges').views.idxmax().values][['url', 'edges']].set_index(
        'edges')

    # Join all these Series to create a Dataframe with metrics by Edge
    manhattan_byedge = num_comments_views_likes.join(num_comments_views_likes_ny, rsuffix='_ny').join(
        photos_count).join(photos_count_ny, rsuffix='_ny').join(top_photos)

    # Create remanining metrics for non-NY users (tourists)
    manhattan_byedge = manhattan_byedge.fillna(value=0)
    manhattan_byedge['views_tourist'] = manhattan_byedge.views - manhattan_byedge.views_ny
    manhattan_byedge['num_comments_tourist'] = manhattan_byedge.num_comments - manhattan_byedge.num_comments_ny
    manhattan_byedge['id_tourist'] = manhattan_byedge.id - manhattan_byedge.id_ny
    manhattan_byedge['likes_tourist'] = manhattan_byedge.likes - manhattan_byedge.likes_ny
    manhattan_byedge.drop(['num_comments', 'views', 'likes', 'id'], 1, inplace=True)

    # Get summary DF by edge
    manhattan_byedge.replace(to_replace=0, value=0.1, inplace=True)

    return manhattan_byedge, manhattan_byedge.url
