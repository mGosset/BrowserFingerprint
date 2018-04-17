import pandas as pd
import numpy as np

def get_number_distinct_values(cur, attributes):
    res = dict()
    for attribute in attributes:
        cur.execute("SELECT COUNT(DISTINCT(" + attribute + ")) as nb FROM Fingerprint")
        res_query = cur.fetchone()
        res[attribute] = res_query['nb']

    return res


def get_number_missing_values(cur, attributes):
    res = dict()
    for attribute in attributes:
        cur.execute("SELECT COUNT(DISTINCT(" + attribute + ")) as nb FROM extensionData WHERE " + attribute + " IS NULL")
        res_query = cur.fetchone()
        res[attribute] = res_query['nb']

    return res


def compute_entropy(df, attribute):
    entropy = 0
    tmp_stats = []
    grouped = df.groupby(['id'])

    for name, group in grouped:
        different_values = group[attribute].unique()
        tmp_stats += [{"id": name, attribute: value} for value in different_values]

    df_stats = pd.DataFrame(tmp_stats)
    serie = df_stats[attribute].value_counts()

    if len(serie) == 1:
        return 0

    total_values = serie.sum()
    for index, value in serie.iteritems():
        pi = float(value) / float(total_values)
        entropy += pi * np.log2(pi)

    return -entropy


def compute_normalized_entropy(df, attribute):
    number_distinct = df[attribute].value_counts().sum()

    if number_distinct == 1:
        return 0

    pi_worst = 1.0 / float(number_distinct)
    worst_case = -number_distinct * pi_worst * np.log2(pi_worst)

    df[attribute].value_counts().count()
    entropy = compute_entropy(df, attribute)
    return entropy / worst_case

