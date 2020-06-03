#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2020 by Faive
# CC BY SA

import requests
from api import PGAPI, Player
from flask import Flask, redirect, request
from urllib.parse import urlencode, quote_plus

app = Flask('app')

@app.route('/')
def index():
    return "<a href='/login'>Login via official War Dragons API</a>"

@app.route("/login")
def login():
    params = dict(client_id=PGAPI.CLIENT_ID,
                  scopes='atlas.read,player.public.read')
    auth_url = f'https://{PGAPI.AUTH_SERVER}/api/authorize?client_id={PGAPI.CLIENT_ID}&scopes=atlas.read,player.public.read'
    return redirect(auth_url)

@app.route("/login/callback")
def pglogin_callback():
    player_id = request.args.get('player_id')
    auth_code = request.args.get('auth_code')
    params = dict(auth_code=auth_code,
                  client_id=PGAPI.CLIENT_ID,
                  client_secret=PGAPI.CLIENT_SECRET)
    token_url = f'https://{PGAPI.AUTH_SERVER}/api/dev/retrieve_token?{urlencode(params, quote_via=quote_plus)}'
    resp = requests.get(token_url)
    resp_data = resp.json()
    profile = Player(api_key=resp_data['api_key'])
    return f"The API key for {player_id} is {resp_data['api_key']} (on this app)<p>AuthToken: {resp_data}<p>Test query/own profile: {profile.data}"


if __name__ == "__main__":
	app.run(host='127.0.0.1', port=5000)
