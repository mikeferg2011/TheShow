import requests
import json

base_url = 'https://mlb21.theshow.com/apis'
card_types = ['mlb_card', 'stadium', 'equipment',
              'sponsorship', 'unlockable', 'perks']

metadata_url = base_url + '/meta_data.json'
items_url = base_url + '/items.json'
listings_url = base_url + '/listings.json'

proxies={'http':'http://172.23.137.193:8080', 'https':'http://172.23.137.193:8080'}

def get_pages(endpoint, params=None):
    page = 1
    total_pages = 1
    total_items = []
    while page <= total_pages:
        print(page)
        params['page'] = page
        resp = requests.get(
            base_url + endpoint,
            params=params,
            proxies=proxies)
        parsed = json.loads(resp.text)
        page = parsed['page']
        total_pages = parsed['total_pages']
        items = parsed[endpoint[1:len(endpoint)-5]]
        total_items += items
        page += 1
    print(len(total_items))
    return(total_items)
