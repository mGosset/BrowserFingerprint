import os

from dotenv import load_dotenv, find_dotenv
import logging
import re

from src import CSV_DELIMITER
from src import utils
from src.fingerprint import Fingerprint



def get_id_to_consistency(cur):
    BATCH_SIZE = 5000
    id_to_oses = dict()
    id_to_browsers = dict()
    id_to_nb_inconsistencies = dict()
    id_to_nb_fps = dict()
    number_re = re.compile(r"[+-]?([0-9]*[.])?[0-9]+")

    cur.execute("SELECT max(counter) as nb_fps from extensionData")
    nb_fps = cur.fetchone()["nb_fps"] +1
    logger = logging.getLogger(__name__)

    for i in range(0, nb_fps, BATCH_SIZE):
        logger.info("Detecting inconsistencies fingerprints: {:d}".format(i))
        sql = "SELECT * FROM extensionData where counter < %s and counter > %s"
        cur.execute(sql, (i + BATCH_SIZE, i))
        fps = cur.fetchall()
        for fp_dict in fps:
            try:
                fp = Fingerprint(fp_dict)
                if fp.getId() in id_to_oses:
                    id_to_oses[fp.getId()].add(fp.getOs())
                else:
                    id_to_oses[fp.getId()] = set()
                    id_to_oses[fp.getId()].add(fp.getOs())

                if fp.getId() in id_to_browsers:
                    id_to_browsers[fp.getId()].add(fp.getBrowser())
                else:
                    id_to_browsers[fp.getId()] = set()
                    id_to_browsers[fp.getId()].add(fp.getBrowser())

                if len(id_to_browsers[fp.getId()]) > 1 or len(id_to_oses[fp.getId()]) > 1:
                    id_to_nb_inconsistencies[fp.getId()] = 100000000

                if fp.getOs() == "Android" or fp.getOs() == "iOS" or \
                fp.getOs() == "Windows Phone" or fp.getOs() == "Firefox OS" or \
                fp.getOs() == "Windows 95":
                    id_to_nb_inconsistencies[fp.getId()] = 10000000000

                if fp.getBrowser() == "Safari" or fp.getBrowser() == "IE" or \
                fp.getBrowser()== "Edge" or fp.getBrowser() == "Googlebot":
                    id_to_nb_inconsistencies[fp.getId()] = 10000000

                if fp.hasPlatformInconsistency():
                    if fp.getId() in id_to_nb_inconsistencies:
                        id_to_nb_inconsistencies[fp.getId()] += 5
                    else:
                        id_to_nb_inconsistencies[fp.getId()] = 5

                # custom rules for extension only
                if fp.getOs() == "Nintendo Wii":
                    id_to_nb_inconsistencies[fp.getId()] = 1000000
                elif fp.getOs() == "oMbyWlGAKlXD9wFfSs2wUM":
                    id_to_nb_inconsistencies[fp.getId()] = 1000000
                elif fp.getOs() == "masking-agent":
                    id_to_nb_inconsistencies[fp.getId()] = 1000000
                elif fp.getOs() == "x86":
                    id_to_nb_inconsistencies[fp.getId()] = 1000000

                if number_re.fullmatch(fp.getLanguages()) is not None:
                    id_to_nb_inconsistencies[fp.getId()] = 1000000

                if fp.getId() in id_to_nb_fps:
                    id_to_nb_fps[fp.getId()] += 1
                else:
                    id_to_nb_fps[fp.getId()] = 1

                # Seems weird but made on purpose !
                if fp.getId() not in id_to_nb_inconsistencies:
                    id_to_nb_inconsistencies[fp.getId()] = 0

                if fp.getId() == "bc19c32d-a271-4dd7-b5e6-62d36d1a3128":
                    id_to_nb_inconsistencies[fp.getId()] = 100

                # encodingHttp=NaN
                elif fp.getId() == "74fcb14e-2bff-428f-b7a3-82b0ed2a8397":
                    id_to_nb_inconsistencies[fp.getId()] = 100000
                elif fp.getId() == "91bd68b4-4ba0-4479-8ab2-ac98357b51e1":
                    id_to_nb_inconsistencies[fp.getId()] = 100000
                elif fp.getId() == "be8f292f-aeae-4d7a-ac65-8ff7797e1ca0":
                    id_to_nb_inconsistencies[fp.getId()] = 100000

                # languageHttp=NaN
                elif fp.getId() == "6f6a85bd-482e-496c-a314-1a791d5ae86a":
                    id_to_nb_inconsistencies[fp.getId()] = 100000
                elif fp.getId() == "73c677d0-50b3-42a8-b61f-46a3b73a98ad":
                    id_to_nb_inconsistencies[fp.getId()] = 100000
                elif fp.getId() == "a57972d8-6bf8-44fd-a7b7-12d76f4aabe1":
                    id_to_nb_inconsistencies[fp.getId()] = 100000
                elif fp.getId() == "d93dcb55-49a0-4185-a1a8-060371b61a32":
                    id_to_nb_inconsistencies[fp.getId()] = 100000

                # userAgentHttp=NaN

                # platformJS=NaN


                elif fp.getUserAgent() == "this is a test":
                    id_to_nb_inconsistencies[fp.getId()] = 100000
                elif fp.getUserAgent() == "PlayStation 4 3.15":
                    id_to_nb_inconsistencies[fp.getId()] = 100000

            except Exception as e:
                print(e)
                id_to_nb_inconsistencies[fp_dict["id"]] = 1000000

    user_id_consistent = [x for x in id_to_nb_fps if
                          float(id_to_nb_inconsistencies[x])/float(id_to_nb_fps[x]) < 0.02]

    cur.execute("SELECT id, count(distinct canvasJSHashed) as count, count(canvasJSHashed) as \
                nb_fps FROM extensionData group by id having count(distinct canvasJSHashed)/count(canvasJSHashed) > 0.35 \
                and count(canvasJSHashed) > 5 order by id")
    rows = cur.fetchall()
    poisoner_ids = [row["id"] for row in rows]
    user_id_consistent = [user_id for user_id in user_id_consistent if user_id not in poisoner_ids]

    cur.execute("SELECT DISTINCT(id) FROM extensionData")
    print(len(user_id_consistent))
    user_id_to_consistency = dict()
    user_ids = cur.fetchall()
    for row in user_ids:
        user_id = row["id"]
        if user_id in user_id_consistent:
            user_id_to_consistency[user_id] = True
        else:
            user_id_to_consistency[user_id] = False

    return user_id_to_consistency


def write_fingerprint_dataset_to_csv(cur, file_path, user_id_to_consistency):
    BATCH_SIZE = 10000

    file_content = [CSV_DELIMITER.join(Fingerprint.ANALYSIS_ATTRIBUTES + [Fingerprint.CONSISTENT])]
    cur.execute("SELECT max(counter) as nb_fps from extensionData")
    nb_fps = cur.fetchone()["nb_fps"] + 1
    logger = logging.getLogger(__name__)

    for i in range(0, nb_fps, BATCH_SIZE):
        logger.info("Fetching fingerprints: {:d}".format(i))
        sql = "SELECT * FROM extensionData where counter < %s and counter > %s"
        cur.execute(sql, (i + BATCH_SIZE, i))
        fps = cur.fetchall()
        for fp in fps:
            try:
                row = []
                fingerprint = Fingerprint(fp)
                for attribute in Fingerprint.ANALYSIS_ATTRIBUTES:
                    row.append(str(fingerprint.val_attributes[attribute]))

                row.append(str(user_id_to_consistency[fingerprint.getId()]))
                file_content.append(CSV_DELIMITER.join(row))
            except Exception as e:
                logger.error(e)

    with open(file_path, 'w+') as f:
        f.write('\n'.join(file_content))


def main():
    db_info = utils.get_db_info_from_env()
    con, cur = utils.connect_to_database(db_info)
    user_id_to_consistency = get_id_to_consistency(cur)
    file_path = "/".join([project_dir, 'data', 'processed', 'fingerprint_dataset.csv'])
    write_fingerprint_dataset_to_csv(cur, file_path, user_id_to_consistency)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    load_dotenv(find_dotenv())
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    main()




