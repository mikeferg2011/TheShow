import requests
import json
import pandas as pd

base_url = 'https://mlb21.theshow.com/apis'
card_types = ['mlb_card', 'stadium', 'equipment',
              'sponsorship', 'unlockable', 'perks']

metadata_url = base_url + '/meta_data.json'
items_url = base_url + '/items.json'
listings_url = base_url + '/listings.json'
roster_updates_url = base_url + '/roster_updates.json'
roster_update_url = base_url + '/roster_update.json'

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

def get_roster_updates():
    resp = requests.get(
        base_url + '/roster_updates.json',
        proxies=proxies)
    parsed = json.loads(resp.text)
    return(parsed['roster_updates'])

def get_roster_update(id):
    resp = requests.get(
        base_url + '/roster_update.json',
        params={'id': id},
        proxies=proxies)
    parsed = json.loads(resp.text)
    att_changes = parsed['attribute_changes']
    item_list = []
    for i in att_changes:
        tmp_dict = {}
        tmp_dict['uuid'] = i['item']['uuid']
        tmp_dict['current_rank'] = i['current_rank']
        tmp_dict['current_rarity'] = i['current_rarity']
        tmp_dict['old_rank'] = i['old_rank']
        tmp_dict['old_rarity'] = i['old_rarity']
        item_list.append(tmp_dict)
        # print(i['item']['uuid'], i['item']['name'])
    df = pd.DataFrame(item_list)

    df.loc[df.current_rarity == 'Common', 'current_rarity'] = '1 - Common'
    df.loc[df.current_rarity == 'Bronze', 'current_rarity'] = '2 - Bronze'
    df.loc[df.current_rarity == 'Silver', 'current_rarity'] = '3 - Silver'
    df.loc[df.current_rarity == 'Gold', 'current_rarity'] = '4 - Gold'
    df.loc[df.current_rarity == 'Diamond', 'current_rarity'] = '5 - Diamond'

    df.loc[df.old_rarity == 'Common', 'old_rarity'] = '1 - Common'
    df.loc[df.old_rarity == 'Bronze', 'old_rarity'] = '2 - Bronze'
    df.loc[df.old_rarity == 'Silver', 'old_rarity'] = '3 - Silver'
    df.loc[df.old_rarity == 'Gold', 'old_rarity'] = '4 - Gold'
    df.loc[df.old_rarity == 'Diamond', 'old_rarity'] = '5 - Diamond'
    
    return(df)