import os

from dotenv import load_dotenv, find_dotenv
import logging

from src import CSV_DELIMITER
from src import utils
from src.fingerprint import Fingerprint


def get_fingerprints_experiments(cur, min_nb_fingerprints, limit_test=300000):
    sql_query = ("SELECT *, NULL as canvasJS FROM extensionData WHERE \
                id in (SELECT id FROM extensionData WHERE counter < %s GROUP BY \
                id having count(*) > %s)\
                ORDER by counter ASC")
    cur.execute(sql_query, (limit_test, min_nb_fingerprints))
    fps = cur.fetchall()
    fingerprints = []
    for fp in fps:
        try:
            fingerprints.append(Fingerprint(fp))
        except Exception as e:
            print(e)

    return fingerprints


def write_fingerprint_dataset_to_csv(fingerprints, file_path):
    file_content = [CSV_DELIMITER.join(Fingerprint.ANALYSIS_ATTRIBUTES)]
    for fingerprint in fingerprints:
        row = []
        for attribute in Fingerprint.ANALYSIS_ATTRIBUTES:
            row.append(str(fingerprint.val_attributes[attribute]))
        file_content.append(CSV_DELIMITER.join(row))

    with open(file_path, 'w+') as f:
        f.write('\n'.join(file_content))


def main():
    db_info = utils.get_db_info_from_env()
    con, cur = utils.connect_to_database(db_info)
    fingerprints = get_fingerprints_experiments(cur, 0, limit_test=300000)

    file_path = "/".join([project_dir, 'data', 'processed', 'fingerprint_dataset.csv'])
    write_fingerprint_dataset_to_csv(fingerprints, file_path)

    logger = logging.getLogger(__name__)
    logger.info("Wrote fingerprint dataset to {}".format(file_path))

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    load_dotenv(find_dotenv())
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    main()




