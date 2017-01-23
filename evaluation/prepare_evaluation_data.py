import matplotlib.pyplot as plt
import shapely.geometry as geom
import numpy as np
import pandas as pd
import geopandas as gpd
import random
import numpy as np
from shapely.geometry import Polygon, Point
import time


def main():
    manhattan = gpd.read_file('manhattan.geojson')
    edges = gpd.read_file('edges2.geojson')
    manhattan_places = gpd.read_file('nyc_places.geojson')
    bound = manhattan.ix[0].geometry

    manhattan_places = manhattan_places[manhattan_places['type'].isin(set(['Landmark or place', 'Museum or exhibition', 'Event', 'Area']))]

    poly = bound

    minx, miny, maxx, maxy = poly.bounds

    longs = np.arange(minx, maxx, 0.00002)
    lats = np.arange(miny, maxy, 0.00002)
    longs = longs.ravel()
    lats = lats.ravel()
    random.shuffle(longs)
    random.shuffle(lats)
    coords = np.array([(x, y) for x, y in zip(longs, lats)])

    random_points_list = []
    for xy in coords:
        if Point(xy).within(poly):
            random_points_list.append((xy[0], xy[1]))

    # Eliminate duplicate edges, again
    edges['node1'], edges['node2'] = edges['id'].str.split('_', 1).str
    edges.node1 = pd.to_numeric(edges.node1)
    edges.node2 = pd.to_numeric(edges.node2)
    df1 = edges[edges.node1 < edges.node2]
    df2 = edges[edges.node2 < edges.node1]
    df2['node1b'] = df2.node2
    df2['node2b'] = df2.node1
    df2.id = df2.node1b.astype(str).str.cat(df2.node2b.astype(str), sep='_')
    df2 = df2[~df2.id.isin(df1.id)]
    df1 = df1.drop(['node1', 'node2'], 1)
    df2 = df2.drop(['node1', 'node2', 'node1b', 'node2b'], 1)
    frames = [df1, df2]
    edges = pd.concat(frames)
    edges = edges.drop_duplicates(subset=['id'])
    edges = edges.reset_index()

    points_series = gpd.GeoSeries(manhattan_places.geometry)

    start = time.time()

    id_list = []
    for i, point in enumerate(points_series):
        neareast_line = np.argmin([point.distance(line) for line in edges.geometry])
        id_list.append(edges.ix[neareast_line].id)
    array = np.array(id_list)
    end = time.time()
    print end - start

    manhattan_places['edge'] = array


    manhattan_places.to_pickle('./touristic_evaluation_source_target.pkl')
    pd.DataFrame(random_points_list).to_pickle('./evaluation_source_target.pkl')


if __name__ == '__main__':
    main()
