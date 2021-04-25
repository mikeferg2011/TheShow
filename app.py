from flask import Flask, jsonify
import pandas as pd
import numpy as np
import requests
import json
import api
import cookie_api

with open("cookie.txt") as f:
    cooks =json.loads(f.read())

player_series = {
    'Live': 1337,
    'Default': 10000,
    'Rookie': 10001,
    'Breakout': 10002,
    'Veteran': 10003,
    'All-Star': 10004,
    'Awards': 10005,
    'Postseason': 10006,
    'Future Stars': 10008,
    'Prime': 10013,
    'Prospect': 10015,
    'Topps Now': 10017,
    '2nd Half': 10020,
    '42 Series': 10021,
    'Milestone': 10022
}

curr_listings = api.get_pages('/listings.json', {'type': 'mlb_card','series_id': 1337})
curr_listings_format = []
for i in curr_listings:
    tmp_dict = {}
    tmp_dict["best_buy_price"] = i["best_buy_price"]
    tmp_dict["best_sell_price"] = i["best_sell_price"]
    tmp_dict['uuid'] = i['item']['uuid']
    tmp_dict['rarity'] = i['item']['rarity']
    tmp_dict['name'] = i['item']['name']
    tmp_dict['overall'] = i['item']['ovr']
    tmp_dict['team'] = i['item']['team']
    curr_listings_format.append(tmp_dict)
list_df = pd.DataFrame(curr_listings_format)

inv_curr = cookie_api.getInventory(cooks)
inv_df = pd.DataFrame(inv_curr)
inv_df = inv_df.loc[inv_df.series == 'Live']

df = list_df.merge(inv_df[['uuid', 'qty']], how = 'left', on='uuid')
df = df.loc[df.team != 'Free Agents']
df['qty'] = df['qty'].fillna(0)

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/sox')
def sox():
    cws = api.get_pages('/listings.json', {'type': 'mlb_card', 'team': 'CWS','series_id': 1337})
    return(jsonify(cws))

@app.route('/listings')
def listings():
    players = api.get_pages('/listings.json', {'type': 'mlb_card','series_id': 1337})
    return(jsonify(players))

@app.route('/test_pandas')
def test_pandas():
    all_packs = cookie_api.getPackHistory(cooks)
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
    print(pack_history.head())
    return(pack_history.head().to_html())

@app.route('/collections')
def collections():
    df_tmp = df.copy()
    df_tmp['needed'] = np.where(df.qty == 0, 1, 0)
    df_tmp['needed_buy'] = df_tmp.best_buy_price * df_tmp.needed
    df_tmp['needed_sell'] = df_tmp.best_sell_price * df_tmp.needed
    df_teams = df_tmp.groupby(['team'])['best_buy_price', 'best_sell_price', 'needed_buy', 'needed_sell'].sum()
    return(df_teams.to_html())

if __name__ == '__main__':
    app.run()