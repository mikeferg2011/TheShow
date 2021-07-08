from bs4 import BeautifulSoup
import pandas as pd
import requests
import json

proxies = {'http':'http://172.23.137.193:8080', 'https':'http://172.23.137.193:8080'}

def isNextPage(req):
    return(req.text.find('next_page disabled') == -1)


def getPackPage(cooks, page_num, url='https://mlb21.theshow.com/packs/open_pack_history'):
    return(requests.get(url, params={'page': page_num}, cookies=cooks, proxies=proxies))


def parsePackPage(req):
    soup = BeautifulSoup(req.text, features="html.parser")
    packs = soup.find_all('div', {"class": "section-pack-history"})
    pack_list = []
    for pack in packs:
        pack_dict = {}
        a = pack.find('div', {'class': 'section-pack-history-secondary'})

        pack_long = a.h3.string
        pack_dict['type'] = pack_long.split(' - ', 1)[0]
        if len(pack_long.split(' - ', 1)) > 1:
            pack_dict['version'] = pack_long.split(' - ', 1)[1]
        else:
            pack_dict['version'] = ''

        pack_dict['open'] = a.p.string

        table_body = a.table.tbody
        rows = table_body.find_all('tr')
        pack_dict['cards'] = []
        for row in rows:
            card_dict = {}
            cols = row.find_all('td')

            card_dict['name'] = cols[1].text.strip()
            card_dict['url'] = cols[1].a.get('href')
            card_dict['uuid'] = cols[1].a.get('href').rsplit('/', 1)[1]
            card_dict['type'] = cols[2].text.strip()

            rarity = cols[3].img.get('src').rsplit('/', 1)[1]
            if rarity == 'shield-common.png':
                card_dict['rarity'] = '1 - Common'
            elif rarity == 'shield-bronze.png':
                card_dict['rarity'] = '2 - Bronze'
            elif rarity == 'shield-silver.png':
                card_dict['rarity'] = '3 - Silver'
            elif rarity == 'shield-gold.png':
                card_dict['rarity'] = '4 - Gold'
            elif rarity == 'shield-diamond.png':
                card_dict['rarity'] = '5 - Diamond'

            pack_dict['cards'].append(card_dict)
        pack_list.append(pack_dict)
    return(pack_list)


def getPackHistory(cooks):
    all_packs = []  # empty array to append all packs in page
    check = True
    page_num = 1
    while check:
        print(page_num)
        page = getPackPage(cooks, page_num)
        all_packs += parsePackPage(page)
        page_num += 1
        check = isNextPage(page)
    return(all_packs)


def getInventoryPage(cooks, page_num, url='https://mlb21.theshow.com/inventory'):
    return(requests.get(url, params={'ownership': 'owned', 'page': page_num}, cookies=cooks, proxies=proxies))


def parseInventoryPage(req):
    soup = BeautifulSoup(req.text, features="html.parser")
    inv = soup.find('div', {"class": "section-block"})

    table_body = inv.table.tbody

    rows = table_body.find_all('tr')
    card_list = []
    for row in rows:
        card_dict = {}
        cols = row.find_all('td')

        card_dict['name'] = cols[1].text.strip()
        card_dict['url'] = cols[1].a.get('href')
        card_dict['uuid'] = cols[1].a.get('href').rsplit('/', 1)[1]

        card_dict['overall'] = cols[2].text.strip()
        rarity = cols[2].img.get('src').rsplit('/', 1)[1]
        if rarity == 'shield-common.png':
            card_dict['rarity'] = '1 - Common'
        elif rarity == 'shield-bronze.png':
            card_dict['rarity'] = '2 - Bronze'
        elif rarity == 'shield-silver.png':
            card_dict['rarity'] = '3 - Silver'
        elif rarity == 'shield-gold.png':
            card_dict['rarity'] = '4 - Gold'
        elif rarity == 'shield-diamond.png':
            card_dict['rarity'] = '5 - Diamond'

        card_dict['series'] = cols[3].text.strip()
        card_dict['set'] = cols[4].text.strip()
        card_dict['team'] = cols[5].text.strip()
        card_dict['position'] = cols[6].text.strip()
        card_dict['qty'] = cols[7].text.strip()[1:]
        card_list.append(card_dict)

    return(card_list)


def getInventory(cooks):
    all_cards = []  # empty array to append all cards in page
    check = True
    page_num = 1
    while check:
        print(page_num)
        page = getInventoryPage(cooks, page_num)
        all_cards += parseInventoryPage(page)
        page_num += 1
        check = isNextPage(page)
    return(all_cards)


if __name__ == '__main__':
    with open("cookie.json") as f:
        cooks = json.loads(f.read())

    all_packs = getPackHistory(cooks)
    pack_history = pd.DataFrame()
    pack_num = 1
    for pack in reversed(all_packs):
        card_num = 1
        for card in pack['cards']:
            pack_history = pack_history.append({'pack_nbr': pack_num,
                                                'pack_open': pack['open'],
                                                'pack_type': pack['type'],
                                                'pack_ver': pack['version'],
                                                'card_nbr': card_num,
                                                'card_nm': card['name'],
                                                'card_url': card['url'],
                                                'card_uuid': card['uuid'],
                                                'card_type': card['type'],
                                                'card_rarity': card['rarity']},
                                               ignore_index=True)
            card_num += 1
        pack_num += 1
    pack_history.to_csv('./csv/pack_history.csv', index=False)
    print(pack_history.head())

    inv_list = getInventory(cooks)
    inv_df = pd.DataFrame(inv_list)
    inv_df.to_csv('./csv/inventory.csv', index=False)
    print(inv_df.head())
