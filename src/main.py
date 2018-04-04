#importation de la fonction Fingerprint du programme fingerprint
from src.fingerprint import Fingerprint

#importation du package MySQLdb
import MySQLdb as mdb
# importation du package MySQLdb
import MySQLdb as mdb

from src.fingerprint import Fingerprint


#création d'une fonction
def get_fingerprints_experiments(cur, min_nb_fingerprints, attributes, limitTest=300000):
    cur.execute("SELECT *, NULL as canvasJS FROM extensionData WHERE \
                id in (SELECT id FROM extensionData WHERE counter < "+str(limitTest)+" GROUP BY \
                id having count(*) > "+str(min_nb_fingerprints)+")\
                ORDER by counter ASC")
    fps = cur.fetchall()
    fp_set = []
    for fp in fps:
        try:
            fp_set.append(Fingerprint(attributes, fp))
        except Exception as e:
            print(e)

    return fp_set

#connection à la base de donnée appelé fingerprint avec le mot de passe bdd
#on se limite à 10 empreintes par personne et à un curseur de 50000
def main():
    con = mdb.connect('localhost', 'root', 'bdd', 'fingerprint')
    cur = con.cursor(mdb.cursors.DictCursor)
    attributes = Fingerprint.MYSQL_ATTRIBUTES
    fingerprints = get_fingerprints_experiments(cur, 10, attributes, limitTest=50000)
    print(fingerprints)

#mettre des arguments dans le main
if __name__ == "__main__":
    main()
