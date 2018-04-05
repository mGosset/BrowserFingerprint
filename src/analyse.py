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



