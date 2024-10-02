import json
import pandas as pd

from tqdm import tqdm

with open('dataframes.json') as f:
    d = json.load(f)

org_hierarchy = pd.read_csv('org_hierarchy.csv')

columns_to_add = [
    "National",
    "District",
    "Council",
    "Chiefdom",
    "Clinic",
    "CHW"
]

for key, val in tqdm(d.items()):

    matching_row = org_hierarchy[org_hierarchy['Organisation unit'] == key]
    matching_row.reset_index(inplace=True)

    if len(matching_row) == 1:

        for i in columns_to_add:
            d[key]["columns"].append(i)

            for idx , z in enumerate(d[key]["data"]):
                d[key]["data"][idx][i] = matching_row.loc[0,i]
    else:
        print(
            f"Row match error for {key} the number of matchs in org_hierarchy.csv were: {len(matching_row)}"
        )

    # Assuming your DataFrame is called 'df', the column is 'org_unit', and the variable is 'key'
    #

    #print(matching_row)

    #df = pd.DataFrame(val["data"])
    #df.index = df["index"]
    #df.drop("index",axis=1,inplace=True)

    #df.to_csv('test.csv')

# Save the dictionary as a JSON file
with open('clean_CBS_data.json', 'w') as f:
    json.dump(d, f)