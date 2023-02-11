import private

SEARCH_KEY = private.api
SEARCH_ID = private.engine_id
COUNTRY = "us"

SEARCH_URL = "https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={query}&start={start}&gl=" + COUNTRY
RESULT_COUNT = 20