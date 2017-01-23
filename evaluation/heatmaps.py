import numpy as np
import pandas as pd 
import networkx as nx
import matplotlib.pyplot as plt
import geojson as gj
import json
import copy
import geojson as gj
import os
import inspect
import sys
import time

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
base_dir = "/".join(current_dir.split('/')[:-1])
sys.path.insert(0, base_dir)

from Graph.coordinate_helpers import *
from Graph.path_optimization import *


def main():

    G = initialize('../Graph/data_by_edge_final.pkl')
    edges = G.edges()
    gj_edges = []
    for e in G.edges():
        gj_edges.append(gj.Feature(id=str(e[0].name) + '_' + str(e[1].name),
                                   geometry=gj.LineString([list(e[0].latlon), list(e[1].latlon)]),
                                   properties={'stroke-opacity': G.edge[e[0]][e[1]]['inter_score']*7000.,
                                               'stroke':"#FE4100"}))

    F_edges = gj.FeatureCollection(features=gj_edges)

    with open('./edges.geojson', 'w') as to_dump:
            gj.dump(F_edges, to_dump, sort_keys=True)


if __name__ == '__main__':
    main()