#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2020 by Faive
# CC BY SA

import requests
from requests.exceptions import HTTPError
import hashlib
import json
import re
from datetime import datetime
from urllib.parse import quote


class PGAPI:
    CLIENT_ID = 'app-xxxxxxxxxxxxxxxx'
    CLIENT_SECRET = 'secret-xxxxxxxxxxxxxx'
    API_SERVER = AUTH_SERVER = 'api-dot-pgdragonsong.appspot.com'

    def __init__(self, autofetch=True, **kwargs):
        self.autofetch = autofetch
        self.params = None
        if 'api_key' in kwargs:
            self.api_key = kwargs.get('api_key')
        else:
            raise ValueError("API key missing")

    def genHeaders(self):
        now = datetime.now().timestamp()
        msg = ':'.join([PGAPI.CLIENT_SECRET, self.api_key, str(int(now))]).encode('utf-8')
        generated_signature = hashlib.sha256(msg).hexdigest()
        return {'X-WarDragons-APIKey':self.api_key, 'X-WarDragons-Request-Timestamp': str(int(now)), 'X-WarDragons-Signature':str(generated_signature)}

    def fetch(self):
        resp = requests.get(self.API_URL, headers=self.genHeaders(), params=self.params)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise HTTPError(f"Request to {self.API_URL} failed (HTTP {resp.status_code})")

    def __str__(self):
        return json.dumps(self.data)


class Player(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/player/public/my_profile'
        self.data = kwargs.get('data') or self.fetch() if self.autofetch==True else None


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
                    raise ValueError(f"Error parsing castle: <str>'{self.cont_id}'")
            elif type(cont_id) == type(dict()):
                self.cont_ids.append({**cont_id})

        self.params = {'cont_ids': json.dumps(self.cont_ids)}
        print(self.params)          
        self.data = self.fetch() if self.autofetch==True else None


class AtlasTeamsMetadata(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/teams/metadata/macro?k_id=1&realm_name=Celestial_Haven'
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



class AtlasContribution(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/team/contribution'

        self.data = self.fetch() if self.autofetch==True else None
        print(self.data)
        for player in self.data['entries']:
            setattr(self, player['for_name'], player['stats'])
