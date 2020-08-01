#!/usr/local/bin/pypy3

import requests
from api import PGAPI, Player, CastleInfo
from flask import Flask, redirect, request
from urllib.parse import urlencode, quote_plus
import hostinfo

def index():
    return "<a href='/login'>Login via official War Dragons API</a>"


def login():
    params = dict(client_id=PGAPI.CLIENT_ID,
                  scopes='atlas.read,player.public.read')
    auth_url = f'https://{PGAPI.AUTH_SERVER}/api/authorize?client_id={PGAPI.CLIENT_ID}&scopes=atlas.read,player.public.read'
    return redirect(auth_url)

def pglogin_callback():
    player_id = hostinfo.player_id #request.args.get('player_id')

    auth_code = hostinfo.appEmail + "|" + hostinfo.clientID  # "apikey-8wHSIXr8RDqnDMeF8voBEQ" #request.args.get('auth_code')
    params = dict(auth_code=auth_code,
                  client_id=PGAPI.CLIENT_ID,
                  client_secret=PGAPI.CLIENT_SECRET)
    token_url = f'https://{PGAPI.AUTH_SERVER}/api/dev/retrieve_token?{urlencode(params, quote_via=quote_plus)}'
    resp = requests.get(token_url)
    resp_data = resp.json()
    print(resp_data)
    profile = Player(api_key=resp_data['api_key'])
    return f"The API key for {player_id} is {resp_data['api_key']} (on this app)<p>AuthToken: {resp_data}<p>Test query/own profile: {profile.data}"

def get_castle():
	player_id = hostinfo.player_id #request.args.get('player_id')
	auth_code = hostinfo.appEmail + "|" + hostinfo.clientID
	params = dict(auth_code=auth_code,
    	client_id=PGAPI.CLIENT_ID,
    	client_secret=PGAPI.CLIENT_SECRET)
	token_url = f'https://{PGAPI.AUTH_SERVER}/api/dev/retrieve_token?{urlencode(params, quote_via=quote_plus)}'
	resp = requests.get(token_url)
	resp_data = resp.json()
	castle = CastleInfo(api_key=resp_data['api_key'], cont_ids=["1-A3244-0"])
	return castle


print(get_castle())
#print(login())
#print(pglogin_callback())