import numpy as np
import networkx as nx
import gmplot
import copy
import pandas as pd
from coordinate_helpers import *
import astar

from interestigness_user import interestigness
from interestigness_user import node_potentials


class CityNode(object):
    def __init__(self, ID, latlon, potential=0.):
        self.name = ID
        self.latlon = latlon
        self.potential = potential

    def __str__(self):
        return str(self.name)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):

        if hasattr(other, 'name'):
            return self.name == other.name
        return False


class City(nx.Graph):
    def __init__(self, nodes, edges, nodes_latlon, photo_stats=None):
        super(City, self).__init__()

        self.photo_stats = photo_stats
        self.edge_scores = interestigness(self.photo_stats)
        self.potentials = node_potentials(self.edge_scores)

        self.nodes_raw = np.array([CityNode(i, nodes_latlon[i], potential=self.potentials.ix[i]) for i in nodes])
        edges1 = []
        for e in edges:
            edges1.append([self.nodes_raw[e[0]], self.nodes_raw[e[1]], e[2]])

        self.edges_raw = np.array(edges1)
        self.nodes_latlon = nodes_latlon

        self.add_nodes_from(self.nodes_raw)
        self.add_edges_from(self.edges_raw)
        self.add_score_to_edges('inter_score')
        self.map = gmplot.GoogleMapPlotter(40.769390, -73.974990, 10)

    def add_score_to_edges(self, name):
        self.keep_probability = np.zeros(len(self.edges()))
        for i, e in enumerate(self.edges()):
            e1 = e[0]
            e2 = e[1]
            if '{}_{}'.format(e1, e2) in self.edge_scores.index:
                val = self.edge_scores.ix['{}_{}'.format(e1, e2)]
                self.edge[e1][e2][name] = val
                self.edge[e2][e1][name] = val
                self.keep_probability[i] = val

            elif '{}_{}'.format(e2, e1) in self.edge_scores.index:
                val = self.edge_scores.ix['{}_{}'.format(e2, e1)]
                self.edge[e1][e2][name] = val
                self.edge[e2][e1][name] = val
                self.keep_probability[i] = val

            else:
                self.edge[e1][e2][name] = 0.
                self.edge[e2][e1][name] = 0.
                self.keep_probability[i] = 0.
        return

    def _subgraph_edges(self, nodes):
        return ([x for x in self.edges_raw if x[0] in nodes and x[1] in nodes],
                [x for x in self.nodes_raw if x in nodes])

    def score_path(self, path, weight):
        score = 0
        for i in xrange(len(path) - 1):
            inter = self.edge[path[i]][path[i + 1]][weight]
            score += inter

        return score

    def _remove_random_edges(self, percent=.15, multinomial=False, name='inter'):

        edges_ = np.array(self.edges())

        if not multinomial:
            remove_edges_idx = np.random.choice(range(len(edges_)),
                                                int(len(edges_) * percent),
                                                replace=False)
        else:
            keep_edges_idx = np.random.choice(range(len(edges_)),
                                              len(edges_) - int(len(edges_) * percent),
                                              replace=False,
                                              p=self.keep_probability)
            remove_edges_idx = np.array(list(set(np.arange(len(edges_))) - set(keep_edges_idx)))

        remove_edges = edges_[remove_edges_idx]
        remove_edges = [tuple(x) for x in remove_edges]

        saved = []
        for e in remove_edges:
            saved.append(e)
            e1 = e[0]
            e2 = e[1]
            self.edge[e2][e1]['weight'] = np.inf
            self.edge[e1][e2]['weight'] = np.inf

        return saved

    def _restore_removed_edges(self, recover, edge_orig):
            if not recover:
                return
            for e in recover:
                e1 = e[0]
                e2 = e[1]
                self.edge[e1][e2]['weight'] = edge_orig[e1][e2]['weight']
                self.edge[e2][e1]['weight'] = edge_orig[e2][e1]['weight']
            return

    def latlon_to_node_idx(self, latlon_tuple):
        point = np.array(latlon_tuple)
        return ((self.nodes_latlon - point) ** 2).sum(1).argmin()

    def latlon_to_node(self, latlon_tuple):
        index = self.latlon_to_node_idx(latlon_tuple)
        return self.nodes_raw[index]

    def shortest_path(self, source, target):
        if not source == int:
            # Coordinates were received.
            # Need to convert to node indices
            source = self.latlon_to_node_idx(source)
            source = self.nodes_raw[source]
            target = self.latlon_to_node_idx(target)
            target = self.nodes_raw[target]

        shortest_len = nx.shortest_path_length(self, source,
                                               target, weight='weight')
        shortest_path = nx.shortest_path(self, source,
                                         target, weight='weight')


        score = self.score_path(shortest_path, weight='inter_score')
        return self._path_output(shortest_path, shortest_len, score)

    def randomized_optimal_path(self, source, target,
                                touristic_level=0.5,
                                popular_level=0.5,
                                distance_tol=2.0,
                                randomization=0.15,
                                multinomial=False):
        if not source == int:
            # Coordinates were received.
            # Need to convert to node indices
            source = self.latlon_to_node(source)
            target = self.latlon_to_node(target)

        self.edge_scores = interestigness(self.photo_stats,
                                          touristic_level,
                                          popular_level)
        self.add_score_to_edges('inter_score')

        shortest_len = nx.shortest_path_length(self, source,
                                               target, weight='weight')
        shortest_path = nx.shortest_path(self, source,
                                         target, weight='weight')
        max_len = distance_tol * shortest_len

        paths = []
        lengths = []
        paths.append(shortest_path)
        lengths.append(shortest_len)
        edge_orig = copy.deepcopy(self.edge)
        for i in range(15):
            recover = self._remove_random_edges(percent=randomization,
                                                multinomial=multinomial)
            try:
                p = nx.shortest_path(self, source, target, weight='weight')
                p_len = nx.shortest_path_length(self, source,
                                                target, weight='weight')
            except nx.NetworkXNoPath:
                pass
                print '{} path not connected'.format(i)
            else:
                if p_len < max_len:
                    paths.append(p)
                    lengths.append(p_len)

            self._restore_removed_edges(recover, edge_orig)

        scores = []
        for p in paths:
            scores.append(self.score_path(p, weight='inter_score'))

        scores = np.array(scores)
        scores_argsort = scores.argsort()[::-1]

        scores_sorted = [scores[i] for i in scores_argsort]
        paths_sorted = [paths[i] for i in scores_argsort]
        lengths_sorted = [lengths[i] for i in scores_argsort]

        output = [self._path_output(p, l, s) for p, l, s in zip(paths_sorted[:3],
                                                                lengths_sorted[:3],
                                                                scores_sorted[:3])]
        return output

    def _path_output(self, path_nodes, length, score):
        path_edges_output = [(path_nodes[i].name, path_nodes[i + 1].name) for i in range(len(path_nodes) - 1)]
        nodes_output = [n.name for n in path_nodes]

        path_gj = edges_to_geojson(path_edges_output, self.nodes_latlon, properties=False)

        pics = self.get_pictures_from_path(path_edges_output)

        return {'geojson': path_gj,
                'distance': length,
                'score': score,
                'time': (length / 2.9634) * 60.0,
                'edges': path_edges_output,
                'nodes': nodes_output,
                'photos': pics}

    @staticmethod
    def heuristic(a, target, mult=100000000.0):
        dist = haversine(a.latlon, target.latlon)
        heu = dist - a.potential * mult
        return heu

    def heuristic_optimal_path(self, source, target,
                               touristic_level=0.5,
                               popular_level=0.5,
                               distance_tol=2.0,
                               weight='inter_score',
                               randomization=0.15):

        self.edge_scores = interestigness(self.photo_stats,
                                          touristic_level,
                                          popular_level)

        self.add_score_to_edges('inter_score')

        if not source == int:
            # Coordinates were received.
            # Need to convert to node indices
            source = self.latlon_to_node(source)
            target = self.latlon_to_node(target)

        shortest_len = nx.shortest_path_length(self,
                                               source,
                                               target,
                                               weight='weight')
        freedom = 10000000000.0
        paths = []
        lengths = []
        scores = []
        edge_orig = copy.deepcopy(self.edge)
        while 1:
            recover = self._remove_random_edges(percent=0.05,
                                                multinomial=False)

            sp = astar.astar_path(self, source, target, heuristic=self.heuristic,
                                  weight='weight', mult=distance_tol * freedom)

            sp_len = self.score_path(sp, weight='weight')
            sp_int = self.score_path(sp, weight=weight)

            if sp_len <= shortest_len * distance_tol:
                paths.append(sp)
                lengths.append(sp_len)
                scores.append(sp_int)

            freedom = freedom / 100.

            self._restore_removed_edges(recover, edge_orig)

            if len(paths) >= 3:
                break

        scores = np.array(scores)
        scores_argsort = scores.argsort()[::-1]

        scores_sorted = [scores[i] for i in scores_argsort]
        paths_sorted = [paths[i] for i in scores_argsort]
        lengths_sorted = [lengths[i] for i in scores_argsort]

        output = [self._path_output(p, l, s) for p, l, s in zip(paths_sorted,
                                                                lengths_sorted,
                                                                scores_sorted)]
        return output

    def get_pictures_from_path(self, path):
        # photo_stats: pd.DataFrame indexed by edges n1_n2
        #              and with a column called url_static
        # path: list of CityNode objects

        edges_path = [(p[0], p[1]) for p in path]
        urls = self.photo_stats[['views_tourist', 'views_ny', 'url_static']]
        urls.loc[:, 'total_views'] = urls.loc[:, 'views_tourist'] + urls.loc[:, 'views_ny']

        urls = urls.sort_values('total_views', ascending=False).url_static
        urls = urls[urls != ' NA']
        n = 0
        pics = []
        for edge in urls.index:
            e = edge.split('_')
            e = tuple(int(i) for i in e)
            er = (e[1], e[0])

            if e in edges_path:
                pics.append(urls.ix[edge][1:])
                n += 1
            elif er in edges_path:
                pics.append(urls.ix[edge][1:])
                n += 1

            if n == 4:
                break
        return pics


def initialize(file_path='./data_by_edge_final.pkl'):
    nodes, nodes_latlon, edges = init_network()
    i_df = pd.read_pickle(file_path)
    G = City(nodes, edges, nodes_latlon, photo_stats=i_df)

    return G


if __name__ == '__main__':
    main()

