#!/usr/local/bin/pypy3

import requests
import api
from api import PGAPI, Player, CastleInfo, AtlasTeam
from flask import Flask, redirect, request
from urllib.parse import urlencode, quote_plus
import hostinfo
import plot.mymongo as mymongo
import json
from bson.json_util import dumps
import util


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
    player_id = hostinfo.player_id 


    auth_code = hostinfo.appEmail + "|" + hostinfo.clientID
    print(auth_code)
    auth_codes = [hostinfo.keys[v] +"|" + hostinfo.clientID for v in hostinfo.keys]
    auth_code = auth_codes[1]
    print(auth_code)
    params = dict(auth_code=auth_code,
    	client_id=PGAPI.CLIENT_ID,
    	client_secret=PGAPI.CLIENT_SECRET)
    token_url = f'https://{PGAPI.AUTH_SERVER}/api/dev/retrieve_token?{urlencode(params, quote_via=quote_plus)}'
    resp = requests.get(token_url)
    resp_data = resp.json()
    castle = CastleInfo(api_key=resp_data['api_key'], cont_ids=["1-A3244-0"], old=True)
    return castle

def get_alliance():
    """
    player_id = hostinfo.player_id #request.args.get('player_id')
    auth_code = hostinfo.appEmail + "|" + hostinfo.clientID
    params = dict(auth_code=auth_code,
        client_id=PGAPI.CLIENT_ID,
        client_secret=PGAPI.CLIENT_SECRET)
    token_url = f'https://{PGAPI.AUTH_SERVER}/api/dev/retrieve_token?{urlencode(params, quote_via=quote_plus)}'
    resp = requests.get(token_url)
    resp_data = resp.json()
    """
    alliance = api.AtlasAlliances(old=False)
    return alliance


#print(api.CastleInfo(old=False, cont_ids=["1-A3244-0"]))
db = mymongo.getClient()
api = json.loads(dumps(db["wd"]["api"].find({})))
clientID = [e['value'] for e in api if e['type']=="client_id"][0]
clientSecret = [e['value'] for e in api if e['type']=="client_secret"][0]
auth_codes = [e['value'] for e in api if e['type']=="api_key"]
#castle = CastleInfo(api_keys=[auth_codes[1]], cont_ids=["1-A3244-0"], old=False)
#castle = CastleInfo(api_keys=auth_codes, cont_ids=["1-A3244-0", "1-A3244-1", "1-A3244-2"], old=False)
castle = CastleInfo(api_keys=auth_codes, cont_ids=[{"cont_idx":0, "k_id":1, "region_id":"A3244"}])
print(castle)
exit()

teams = util.all_teams()
#print(teams)
#teams = ["Strikers", "ANGELSnDEM0NS"]

api_teams = AtlasTeam(api_keys=auth_codes, teams=teams, old=False)

f = open("teams.json", "w")
print(api_teams, file=f)



#print(get_castle())
#print(get_castle())
#print(login())
#print(pglogin_callback())