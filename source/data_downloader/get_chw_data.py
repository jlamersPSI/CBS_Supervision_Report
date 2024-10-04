from logging import exception
import json
from tqdm import tqdm

def fetch_chw_data(api):
    query_string = (
        'analytics.json?dimension=pe:LAST_MONTH'
        '&dimension=dx:nufVxEfy3Ps.EXPECTED_REPORTS'
        '&dimension=ou:LEVEL-6;'
    )

    response = api.get(query_string)

    list_of_chws = response.json()["metaData"]["dimensions"]["ou"]

    dimension_string = '%3A'

    with open('HF04_indicators.json') as file:
        HF04_indicators = json.loads(file.read())

    first = True
    for key, val in HF04_indicators.items():
        if first:
            dimension_string = dimension_string + val
            first = False
        else:
            dimension_string = dimension_string + '%3B' + val

    chw_data = {}

    for chw_code in tqdm(list_of_chws):
        try:
            query_string = (
                f'analytics.json?dimension=pe:LAST_12_MONTHS'
                f'&hierarchyMeta=true'
                f'&dimension=dx{dimension_string}'
                f'&dimension=ou:{chw_code};'
            )

            response = api.get(query_string)

            chw_data.update({chw_code: response.json()})
        except exception as e:
            print(f'Error occurred for the CHW with the code {chw_code}')
            print(e)

    with open('chw_data.json', 'w') as f:
        json.dump(chw_data, f)