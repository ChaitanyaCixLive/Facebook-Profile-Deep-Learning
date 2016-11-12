import os
import pickle

import facebook
import requests
import wget
from fake_useragent import UserAgent

UA = UserAgent()


def profile_exists(profile_id):
    """We don't rely on a GraphAPIError because we want to minimize the number of calls to the GraphAPI.
    Mainly because of the API limits."""
    # FULL NAME
    headers = {'User-Agent': UA.chrome}
    try:
        r = requests.get('http://facebook.com/profile.php?id={}'.format(profile_id), headers=headers)
    except:
        return False
    return not r.status_code == 404


def query_profile_with_graph_api(profile_id, access_token):
    """Limited to 4800 calls per day. Not sure though."""
    graph = facebook.GraphAPI(access_token)
    profile = graph.get_object(profile_id)
    return profile


def get_last_profile_id(default):
    last_profile_id = recover_last_known_profile_id()
    if last_profile_id is not None:
        print('Found photos in {}. Resuming from {}'.format('data', last_profile_id))
        return last_profile_id
    else:
        print('Could not find any photos. Starting from {}.'.format(default))
        return default


def recover_last_known_profile_id():
    try:
        files = sorted(os.listdir('data'))
        return int(files[-1].split('.')[0])
    except:
        return None


def extract_information(profile_id, access_token):
    if profile_exists(profile_id):
        profile = query_profile_with_graph_api(profile_id, access_token)
        pickle.dump(profile, open('data/{}.txt'.format(profile_id), 'wb'))
        url = 'https://graph.facebook.com/{}/picture?width=500'.format(profile_id)
        output_filename = 'data/{}.jpg'.format(profile_id)
        wget.download(url, out=output_filename, bar=None)
