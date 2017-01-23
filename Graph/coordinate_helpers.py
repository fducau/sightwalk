import numpy as np
import networkx as nx
import geojson as gj
import gmplot
import copy
import pandas as pd
from math import radians
from math import cos
from math import sin
from math import asin
from math import sqrt


def haversine(latlon1, latlon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Based on: https://stackoverflow.com/questions/15736995/
              how-can-i-quickly-estimate-the-distance-between-
              two-latitude-longitude-points
    """
    # convert decimal degrees to radians
    lon1 = latlon1[0]
    lat1 = latlon1[1]
    lon2 = latlon2[0]
    lat2 = latlon2[1]

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def init_network(network_file='../Graph/road-network_1.txt'):
    with open(network_file, 'r') as f:
        # Read the first line of the file
        n_nodes, n_edges = [int(i) for i in f.readline().strip().split(' ')]
        nodes = range(n_nodes)

        # Read the nodes
        nodes_latlon = []
        for i in range(n_nodes):
            node = [np.double(j) for j in f.readline().strip().split(' ')]
            node = [node[1], node[0]]
            nodes_latlon.append(node)
        # Read the edges
        edges = []
        for line in f.readlines():
            node_1, node_2, d = [np.double(j) for j in line.strip().split(' ')]
            node_1 = int(node_1)
            node_2 = int(node_2)
            if node_1 < node_2:
                edges.append((node_1, node_2, {'weight': d}))
            else:
                edges.append((node_2, node_1, {'weight': d}))

    return np.array(nodes), np.array(nodes_latlon), np.array(edges)


def add_metric_to_edges(edges, i_df, name):
    edges_ = copy.deepcopy(edges)

    for i, e in enumerate(edges_):
        e1 = e[0]
        e2 = e[1]

        if '{}_{}'.format(e1, e2) in i_df.index:
            edges_[i][2][name] = i_df.ix['{}_{}'.format(e1, e2)]
        elif '{}_{}'.format(e2, e1) in i_df.index:
            edges_[i][2][name] = i_df.ix['{}_{}'.format(e2, e1)]
        else:
            edges_[i][2][name] = 0.

    return edges_


def create_graph(nodes, edges):
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    return G


def points_to_geojson(latlon_points):
    nodes_features = []
    for i, n in enumerate(latlon_points):
        nodes_features.append(gj.Feature(id=str(i),
                                         geometry=gj.Point(coordinates=[float(n[0]),
                                                                        float(n[1])])))

    F_nodes = gj.FeatureCollection(features=nodes_features)

    return F_nodes


def edges_to_geojson(edges, nodes_latlon, properties=True):
    gj_edges = []
    for e in edges:
        if properties:
            gj_edges.append(gj.Feature(id=str(e[0]) + '_' + str(e[1]),
                                       geometry=gj.LineString([tuple(nodes_latlon[e[0]]), tuple(nodes_latlon[e[1]])]),
                                       properties=e[2]))
        else:
            gj_edges.append(gj.Feature(id=str(e[0]) + '_' + str(e[1]),
                                       geometry=gj.LineString([tuple(nodes_latlon[e[0]]), tuple(nodes_latlon[e[1]])])))

    F_edges = gj.FeatureCollection(features=gj_edges)
    return F_edges


def write_geojson(filename, obj):
    with open(filename, 'w') as to_dump:
        gj.dump(obj, to_dump, sort_keys=True)
        print('GeoJson saved to {}'.format(to_dump.name))


def plot_path(nodes_list, nodes_latlon, mymap, output='map.html', incremental=False,
              color='r'):
    if not incremental:
        mymap = gmplot.GoogleMapPlotter(40.769390, -73.974990, 10)

    nodes_between_latlon = nodes_latlon[nodes_list]
    nodes_between_lat = [n[1] for n in nodes_between_latlon]
    nodes_between_lon = [n[0] for n in nodes_between_latlon]
    mymap.plot(nodes_between_lat, nodes_between_lon, color)

    source = nodes_list[0]
    target = nodes_list[-1]
    mymap.marker(nodes_latlon[source][1], nodes_latlon[source][0])
    mymap.marker(nodes_latlon[target][1], nodes_latlon[target][0])

    mymap.draw('map.html')


def remove_random_edges(G, percent=.15):
    edges_ = np.array(G.edges())
    remove_edges_idx = np.random.choice(range(len(edges_)), int(len(edges_) * percent))
    remove_edges = edges_[remove_edges_idx]
    remove_edges = [tuple(x) for x in remove_edges]
    G.remove_edges_from(remove_edges)
    return G

def main():
    nodes, nodes_latlon, edges = init_network()
    i_df = pd.read_pickle('../interestingness_v1')
    edges = add_interestingness_to_edges(edges, i_df)

    F_nodes = points_to_geojson(nodes_latlon)
    F_edges = edges_to_geojson(edges, nodes_latlon)

    G = create_graph(nodes, edges)



if __name__ == '__main__':
    main()
