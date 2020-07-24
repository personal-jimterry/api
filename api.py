#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2020 by Faive
# CC BY SA

import requests
import caching
from requests.exceptions import HTTPError
import hashlib
import json
import re
import os
from datetime import datetime, timedelta
from urllib.parse import quote


caching.install_cache('pgapi_cache', backend='sqlite', always_include_get_headers=['X-WarDragons-APIKey'])

class PGApiError(Exception):
    pass

class PGAPI:
    CLIENT_ID = os.environ.get('PG_CLIENT_ID') or 'app-xxxxxxxxxxxxxxxx'
    CLIENT_SECRET = os.environ.get('PG_CLIENT_SECRET') or 'secret-xxxxxxxxxxxxxx'
    API_SERVER = AUTH_SERVER = 'api-dot-pgdragonsong.appspot.com'

    def __init__(self, autofetch=True, **kwargs):
        self.autofetch = autofetch
        self.params = None
        self.body = None
        self.rate_limit_seconds = 300
        if 'api_key' in kwargs:
            self.api_key = kwargs.get('api_key')
        else:
            raise ValueError("API key missing")

    def genHeaders(self):
        now = datetime.utcnow()
        msg = ':'.join([PGAPI.CLIENT_SECRET, self.api_key, str(int(now.timestamp()))]).encode('utf-8')
        generated_signature = hashlib.sha256(msg).hexdigest()
        return {'expires':str(int((now+timedelta(seconds=self.rate_limit_seconds)).timestamp())),'X-WarDragons-APIKey':self.api_key, 'X-WarDragons-Request-Timestamp': str(int(now.timestamp())), 'X-WarDragons-Signature':str(generated_signature)}

    def fetch(self):
        resp = requests.get(self.API_URL, headers=self.genHeaders(), params=self.params)
        if resp.status_code == 200:
            return {"cached":resp.from_cache, **resp.json()}
        else:
            if resp.json().get('error'):
                print(resp.from_cache)
                raise PGApiError(resp.json().get('error'))
            else:
                raise HTTPError(f"Request to {self.API_URL} failed (HTTP {resp.status_code})\nBody: {resp.text}")

    def post(self):
        resp = requests.post(self.API_URL, headers=self.genHeaders(), data=self.body)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise HTTPError(f"Request to {self.API_URL} failed (HTTP {resp.status_code})\nBody: {resp.text}")

    def __str__(self):
        return json.dumps(self.data)


##### Personal API #####

class Player(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rate_limit_seconds = 300
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/player/public/my_profile'
        self.data = kwargs.get('data') or self.fetch() if self.autofetch==True else None


##### Castle API #####

class CastleInfo(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/castle_info'
        self.query_cont_ids = kwargs.get('cont_ids')
        self.cont_ids = []
        if not self.query_cont_ids or type(self.query_cont_ids) != type([]):
            raise ValueError("Field <list of str or dict>'cont_ids' missing or not recognized")

        for cont_id in self.query_cont_ids:
            if type(cont_id) == type(str()):
                match = re.search('^1-(\w\d+)-(\d)', cont_id)
                if match:
                    self.cont_ids.append({'cont_idx':match.group(2), 'k_id':1, 'region_id': match.group(1)})
                else:
                    raise ValueError(f"Error parsing castle: <str>'{cont_id}'")
            elif type(cont_id) == type(dict()):

                self.cont_ids.append({**cont_id})

        self.params = {'cont_ids': json.dumps(self.cont_ids)}        
        self.data = self.fetch() if self.autofetch==True else None


class CastleMetadata(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/castles/metadata/macro'
        self.params = {'k_id':1, 'realm_name':'Celestial_Haven'}
        self.data = self.fetch() if self.autofetch==True else None


##### Teams API #####

class AtlasContribution(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/team/contribution'

        self.data = self.fetch() if self.autofetch==True else None
        print(self.data)
        for player in self.data['entries']:
            setattr(self, player['for_name'], player['stats'])

class AtlasTeamsMetadata(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/teams/metadata/macro'
        self.params = {'k_id':1, 'realm_name':'Celestial_Haven'}
        self.data = self.fetch() if self.autofetch==True else None


class AtlasTeam(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/teams/metadata'
        self.params = {'k_id':1, 'realm_name':'Celestial_Haven'}
        if kwargs.get('team_name'):
            self.params['team_name'] = kwargs.get('team_name')
        self.data = self.fetch() if self.autofetch==True else None


class AtlasBattles(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/team/battles'
        self.params = {}
        if kwargs.get('cursor'):
            self.params['cursor'] = kwargs.get('cursor')
        self.data = self.fetch() if self.autofetch==True else None


class AtlasMonthlyKills(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/teams/monthly_kill_count'
        self.body = {"teams": []}
        if kwargs.get('teams') and type(kwargs.get('teams')) == list():
            self.body = {"teams": [kwargs.get('teams')]}
            self.params['cursor'] = kwargs.get('cursor')
        else:
            raise ValueError("Required argument teams missing or not of type <list>")
            return
        self.data = self.post() if self.autofetch==True else None


class AtlasTroopCount(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/team/troop_count'
        self.params = {}
        self.rate_limit_seconds = 600
        self.data = self.fetch() if self.autofetch==True else None