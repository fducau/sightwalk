import numpy as np
import pandas as pd
from coordinate_helpers import init_network as inn

def standarizer(series):
    # Standarizer for Pandas Series (values of feature sum to 1)
    return series / series.sum()


def interestigness(df_input, touristic=0.5, popular=0.5, smooth=None, spike_uniqueness=True):
    """
    Compute user defined interestingess based on pre-processed social metrics by edge
    Receives:
    - df_input is a DataFrame generated by data_preprocessing.py
    - touristic: User parameter between 0 and 1. The closser to 0 the more "Local",
    the closer to 1, the more "Touristic"
    - popular: User parameter between 0 and 1. The closser to 0 the more "Unique",
    the closer to 1, the more "Popular"
    - Optional: smooth='ln' uses natural logarithm to smooth interestigness metrics

    Returns
    - Pandas DF with interestigness by edge. Total interestigness of city sums to 1.

    """

    df = df_input.drop(['url', 'url_static'], 1)
    if touristic > 1 or touristic < 0:
        raise ValueError('Touristic vs. Local must be between 0 and 1')
    if popular > 1 or popular < 0:
        raise ValueError('Popular vs. Unique must be between 0 and 1')

    ny_norm_ratio = df.id_tourist.sum() / df.id_ny.sum()

    df['likes'] = touristic * df.likes_tourist + (1 - touristic) * df.likes_ny * ny_norm_ratio
    df['views'] = touristic * df.views_tourist + (1 - touristic) * df.views_ny * ny_norm_ratio
    df['n_photos'] = touristic * df.id_tourist + (1 - touristic) * df.id_ny * ny_norm_ratio
    df['n_comments'] = touristic * df.num_comments_tourist + (1 - touristic) * df.num_comments_ny * ny_norm_ratio
    df['comments_likes'] = df.likes + df.n_comments

    if spike_uniqueness:
        df['uniqueness'] = df.comments_likes / df.n_photos**2
    else:
        df['uniqueness'] = df.comments_likes / df.n_photos

    if smooth == 'ln':
        df = np.log(df * 100)

    df = df.apply(standarizer)
    df['interestingness'] = popular * df.n_photos + (1 - popular) * df.uniqueness

    df = df.apply(standarizer)

    interestingness = df.interestingness
    _, _, edges = inn()

    edges = pd.DataFrame(edges)[[0, 1]].drop_duplicates().astype(str)
    edges = edges[0].str.cat(others=edges[1], sep='_')
    values = np.ones(len(edges)) * interestingness.min()
    new_edges = pd.DataFrame(values, np.array(edges))

    new_edges = new_edges[0]
    new_edges = new_edges[~new_edges.index.isin(interestingness.index)]

    interestingness = interestingness.append(new_edges)

    interestingness = interestingness / interestingness.sum()
    interestingness.index.name = u'edges'
    return interestingness


def node_melter(df, node):
    melted = pd.melt(df, id_vars=[node], value_vars=[0])
    melted = melted.groupby([node, 'variable']).sum()
    melted = melted.reset_index().pivot(index=node, columns='variable', values='value')
    return melted.reset_index().set_index(node)


def node_potentials(interestingness_df):
    i = pd.DataFrame(interestingness_df).reset_index()
    i['node1'], i['node2'] = i.edges.str.split('_', 1).str
    node1 = node_melter(i, 'node1')
    node2 = node_melter(i, 'node2')
    i = node1.add(node2, fill_value=0)

    i.index = pd.to_numeric(i.index)
    return standarizer(i[0]).sort_index()
