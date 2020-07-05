import tepco_scraper as ts
import json
from google.cloud import storage
from google.cloud import bigquery
from google.api_core import retry

BQ = bigquery.Client()
BQ_DATASET = 'japan-grid-carbon-api'
BQ_TABLE = 'tepco_data'

CS = storage.Client()
BUCKET_NAME = 'scraper_data'
BLOB_NAME = 'tepco_historical_data.csv'


def tepco_scraper(request):
    df = ts.get_tepco_as_dataframe()
    csvText = ts.convert_tepco_df_to_csv(df)
    request_json = request.get_json()

    _upload_blob_to_storage(BUCKET_NAME, csvText, BLOB_NAME)

    _insert_into_bigquery(df)
    return f'Success!'


def _upload_blob_to_storage(bucket_name, blob_text, destination_blob_name):
    """Uploads a file to the bucket."""
    bucket = CS.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(blob_text)

    print('Scraped Data Uploaded to {}.'.format(
        destination_blob_name))


def _insert_into_bigquery(dataframe):
    row = ts.convert_tepco_df_to_json(dataframe)
    table = BQ.dataset(BQ_DATASET).table(BQ_TABLE)
    errors = BQ.insert_rows_json(table,
                                 json_rows=[row],
                                 retry=retry.Retry(deadline=30))
    if errors != []:
        raise BigQueryError(errors)


class BigQueryError(Exception):
    '''Exception raised whenever a BigQuery error happened'''

    def __init__(self, errors):
        super().__init__(self._format(errors))
        self.errors = errors

    def _format(self, errors):
        err = []
        for error in errors:
            err.extend(error['errors'])
        return json.dumps(err)
