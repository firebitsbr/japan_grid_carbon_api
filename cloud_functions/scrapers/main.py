import json
import copy
import werkzeug.datastructures
from flask import Flask
app = Flask(__name__)

from scrapers.area_data.AreaDataScraper import AreaDataScraper


headers = {}

# Standard Response Messages for Errors
BAD_UTILITY = 'Invalid Utility Specified'


def scrapers(request):
    with app.app_context():
        headers = werkzeug.datastructures.Headers()
        for key, value in request.headers.items():
            headers.add(key, value)
        with app.test_request_context(method=request.method, base_url=request.base_url, path=request.path, query_string=request.query_string, headers=headers, data=request.data):
            try:
                rv = app.preprocess_request()
                if rv is None:
                    rv = app.dispatch_request()
            except Exception as e:
                rv = app.handle_user_exception(e)
            response = app.make_response(rv)
            return app.process_response(response)


@app.route('/area_data/<utility>')
def area_data(utility):
    response = {}

    s = AreaDataScraper(utility)

    if s.scraper == None:
        return BAD_UTILITY, 400, headers

    numRows = s.scrape()

    response = {
        "result": "success",
        "rows": numRows,
        "utility": utility
    }

    return json.dumps(response), 200, headers
