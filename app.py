from flask import Flask, jsonify
import pandas as pd
import numpy as np
import requests
import json
import api
import cookie_api

with open("cookie.json") as f:
    cooks = json.loads(f.read())

with open("tracker.json") as f:
    tracker = json.loads(f.read())
    tracker_df = pd.DataFrame(tracker)

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

def create_list_df(series_id = 1337):
    curr_listings = api.get_pages('/listings.json', {'type': 'mlb_card', 'series_id': series_id})
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
        tmp_dict['link'] = 'https://mlb21.theshow.com/items/' + tmp_dict['uuid']
        curr_listings_format.append(tmp_dict)
    return(pd.DataFrame(curr_listings_format))

# listings_df = create_list_df()

# inv_curr = cookie_api.getInventory(cooks)
# inv_df = pd.DataFrame(inv_curr)

# packs = cookie_api.getPackHistory(cooks)

app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello World!'


@app.route('/sox')
def sox():
    cws = api.get_pages(
        '/listings.json', {'type': 'mlb_card', 'team': 'CWS', 'series_id': 1337})
    return(jsonify(cws))


@app.route('/listings')
def listings():
    players = api.get_pages('/listings.json', {'type': 'mlb_card', 'series_id': 1337})
    return(jsonify(players))


@app.route('/collections')
def collections():
    listings_df = create_list_df()

    inv_curr = cookie_api.getInventory(cooks)
    inv_df = pd.DataFrame(inv_curr)
    inv_df = inv_df.loc[inv_df.series == 'Live']

    df = listings_df.merge(inv_df[['uuid', 'qty']], how='left', on='uuid')
    df = df.loc[df.team != 'Free Agents']
    df['qty'] = df['qty'].fillna(0)
    df_tmp = df.copy()
    df_tmp['needed'] = np.where(df.qty == 0, 1, 0)
    df_tmp['needed_buy'] = df_tmp.best_buy_price * df_tmp.needed
    df_tmp['needed_sell'] = df_tmp.best_sell_price * df_tmp.needed
    df_teams = df_tmp.groupby(['team'])['best_buy_price', 'best_sell_price', 'needed_buy', 'needed_sell'].sum()
    df_teams = df_teams.reset_index()

    df_teams = df_teams.merge(tracker_df, on = 'team')
    df_teams.loc[df_teams.completed == 'Yes', ['needed_buy', 'needed_sell']] = 0
    
    return(pd.DataFrame(df_teams[['best_buy_price', 'best_sell_price', 'needed_buy', 'needed_sell']].sum()).to_html() + '<br>' +
            df_teams.groupby('league')['best_buy_price', 'best_sell_price', 'needed_buy', 'needed_sell'].sum().to_html() + '<br>' +
            df_teams.groupby(['league', 'division'])['best_buy_price', 'best_sell_price', 'needed_buy', 'needed_sell'].sum().to_html() + '<br>' +
            df_teams[['league', 'division', 'team', 'best_buy_price', 'best_sell_price', 'needed_buy', 'needed_sell', 'completed']] \
                .sort_values(['league', 'division', 'team']) \
                .to_html(index=False))

@app.route('/packs')
def packs():
    packs = cookie_api.getPackHistory(cooks)
    pack_cnt = 0
    card_cnt = 0
    pack_list = []
    pack_cards = []
    for i in packs[::-1]:
        pack_cnt += 1
        card_cnt = 0
        i['pack_num'] = pack_cnt
        pack_list.append(i)
        for j in i['cards']:
            card_cnt += 1
            tmp_dict = {}
            tmp_dict['pack_num'] = pack_cnt
            tmp_dict['pack_type'] = i['type']
            tmp_dict['version'] = i['version']
            tmp_dict['open'] = i['open']
            tmp_dict['card_num'] = card_cnt
            tmp_dict['name'] = j['name']
            tmp_dict['url'] = j['url']
            tmp_dict['uuid'] = j['uuid']
            tmp_dict['card_type'] = j['type']
            tmp_dict['rarity'] = j['rarity']
            pack_cards.append(tmp_dict)
    df_packs = pd.DataFrame(pack_list)
    df_cards = pd.DataFrame(pack_cards)
    df_card_max = df_cards.loc[df_cards.card_type == 'MLB Card'].groupby(['pack_num', 'pack_type', 'version'])['rarity'].max()
    df_card_max = df_card_max.reset_index()
    df_card_pivot = df_card_max.pivot_table(values = 'pack_num', index = ['pack_type', 'version'], columns = 'rarity', aggfunc = len, fill_value = 0, margins=True)
    return(df_card_pivot.to_html())

@app.route('/table_test')
def table_test():
    df_1 = pd.DataFrame([{'a':'test', 'b': 123}, {'a': 'Michael', 'b': 1000}])
    df_2 = pd.DataFrame([{'col1':'test', 'col2': 123, 'col3': 'another string'}, {'col1': 'Michael', 'col2': 1000, 'col3': 'baseball'}])
    return(df_1.to_html(index=False) + '<br>' + df_2.to_html())

@app.route('/dupes')
def dupes():
    listings_df = create_list_df(series_id = None)

    inv_curr = cookie_api.getInventory(cooks)
    inv_df = pd.DataFrame(inv_curr)

    df = listings_df.merge(inv_df[['uuid', 'qty']], on='uuid')
    df['qty'] = df['qty'].fillna(0).astype(int)
    df_tmp = df.loc[df.qty > 1]
    df_tmp['dupes'] = df.qty - 1
    df_tmp['amt'] = df_tmp.dupes * df_tmp.best_sell_price
    df_tmp = df_tmp.sort_values('amt', ascending=False)
    return(df_tmp.groupby('rarity')[['amt', 'dupes']].sum().to_html() + '<br>' +
            df_tmp.to_html(render_links = True))

if __name__ == '__main__':
    app.run()
