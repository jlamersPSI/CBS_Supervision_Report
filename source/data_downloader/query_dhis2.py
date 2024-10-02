import os
import datetime

path_to_data_dir = os.path.join(os.getcwd().replace(r'\source',''), 'Data')

today = datetime.datetime.today()

def check_for_data_dir():
    if not os.path.exists(path_to_data_dir):
        os.mkdir(path_to_data_dir)
    else:
        print(f'Data directory exists')

def check_for_org_hierarchy_csv():
    org_hierarchy_file_name = 'org_hierarchy.csv'

    if os.path.exists(os.path.join(path_to_data_dir,org_hierarchy_file_name)):
        print(f'{org_hierarchy_file_name} exists')

        modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(path_to_data_dir,org_hierarchy_file_name)))
        duration = today - modified_date

        if duration.days < 30:
            print(f'\t {org_hierarchy_file_name} is up to date')
        else:
            print(f'\t {org_hierarchy_file_name} is out of date')
    else:
        print(f'Organisational hierarchy does not exist')

def check_for_HF04_indicators_json():
    if not os.path.exists(os.path.join(path_to_data_dir,'HF04_indicators.json')):
        pass
    else:
        print(f'Organisational hierarchy exists and is up to date')

def check_for_clean_CBS_data_json():
    if not os.path.exists(os.path.join(path_to_data_dir,'clean_CBS_data.json')):
        pass
    else:
        print(f'Organisational hierarchy exists and is up to date')

check_for_data_dir()
check_for_org_hierarchy_csv()
#check_for_HF04_indicators_json()
#check_for_clean_CBS_data_json()

