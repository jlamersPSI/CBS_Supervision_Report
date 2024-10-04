import os
import datetime
import dhis2
import keyring
import get_organisation_hierarchy
import source.data_downloader.get_chw_data

path_to_data_dir = os.path.join(os.getcwd().replace(r'\source',''), 'Data')

service_id = 'CBS_Supervision_Report'

MAGIC_USERNAME_KEY = 'im_the_magic_username_key'

# Initialize the API connection to DHIS2 using the given credentials
api = dhis2.Api('https://sl.dhis2.org/hmis23',
                str(keyring.get_password(service_id, MAGIC_USERNAME_KEY)),
                str(keyring.get_password(service_id, keyring.get_password(service_id, MAGIC_USERNAME_KEY)))
                )

today = datetime.datetime.today()

def check_for_data_dir():
    if not os.path.exists(path_to_data_dir):
        os.mkdir(path_to_data_dir)
    else:
        print(f'Data directory exists')

def update_chw_data_json():
    chw_data_file_name = 'chw_data.json'

    if os.path.exists(os.path.join(path_to_data_dir,'chw_data.json')):
        print(f'{chw_data_file_name} exists')

        modified_date = datetime.datetime.fromtimestamp(
            os.path.getmtime(
                os.path.join(
                    path_to_data_dir,
                    chw_data_file_name
                )
            )
        )
        duration = today - modified_date

        if duration.days < 7:
            print(f'\t {chw_data_file_name} is up to date')
        else:
            print(f'\t {chw_data_file_name} is out of date')
            get_chw_data.fetch_chw_data(api)

    else:
        print(f'Organisational hierarchy exists and is up to date')

#def update_org_hierarchy_csv():
#    org_hierarchy_file_name = 'org_unit_hierarchy.json'

#    if os.path.exists(os.path.join(path_to_data_dir,org_hierarchy_file_name)):
#        print(f'{org_hierarchy_file_name} exists')

#        modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(path_to_data_dir,org_hierarchy_file_name)))
#        duration = today - modified_date

#        if duration.days < 5:
#            print(f'\t {org_hierarchy_file_name} is up to date')
#        else:
#            print(f'\t {org_hierarchy_file_name} is out of date')
#           get_organisation_hierarchy.OrgHierarchyTree(api)
#    else:
#        print(f'Organisational hierarchy does not exist')

#def check_for_HF04_indicators_json():
#    if not os.path.exists(os.path.join(path_to_data_dir,'HF04_indicators.json')):
#        pass
#    else:
#        print(f'Organisational hierarchy exists and is up to date')

check_for_data_dir()
update_chw_data_json()
#update_org_hierarchy_csv()
#check_for_HF04_indicators_json()
#check_for_clean_CBS_data_json()

