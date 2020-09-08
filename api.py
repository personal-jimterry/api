#!/usr/local/bin/pypy3
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
import hostinfo
import time
from urllib.parse import urlencode, quote_plus
from concurrent.futures import ThreadPoolExecutor as PoolExecutor, wait, as_completed
import util


caching.install_cache('pgapi_cache', backend='sqlite', always_include_get_headers=['X-WarDragons-APIKey'])

class PGApiError(Exception):
    def __init__(self,e):
        self.error = e

"""
def classless_genHeaders(api_key, rate_limit_seconds):
    CLIENT_SECRET = hostinfo.clientSecret
    now = datetime.utcnow()
    msg = ':'.join([CLIENT_SECRET, api_key, str(int(now.timestamp()))]).encode('utf-8')
    generated_signature = hashlib.sha256(msg).hexdigest()
    return {'expires':str(int((now+timedelta(seconds=rate_limit_seconds)).timestamp())),'X-WarDragons-APIKey':api_key, 'X-WarDragons-Request-Timestamp': str(int(now.timestamp())), 'X-WarDragons-Signature':str(generated_signature)}


def classless_fetch(headers, params, api_key, url, rate_limit_seconds):
    headers = classless_genHeaders(api_key)
    #print("PARAMS", params)        
    resp = requests.get(url, headers=headers, params=params)

    #print(working_url, self.genHeaders(), self.params)
    if resp.status_code == 200:

        #return {"cached":resp.from_cache, **resp.json()}
        if isinstance(resp.json(), list):
            return {"cached":resp.from_cache, "data":resp.json()}
        else:
            return {"cached":resp.from_cache, **resp.json()}
    else:
        if resp.json().get('error'):
            raise PGApiError(resp.json().get('error'))
        else:
            raise HTTPError(f"Request to {working_url} failed (HTTP {resp.status_code})\nBody: {resp.text}")
"""

class PGAPI:
    CLIENT_ID = hostinfo.clientID #os.environ.get('PG_CLIENT_ID') or 'app-xxxxxxxxxxxxxxxx'
    CLIENT_SECRET = hostinfo.clientSecret #os.environ.get('PG_CLIENT_SECRET') or 'secret-xxxxxxxxxxxxxx'
    API_SERVER = AUTH_SERVER = 'api-dot-pgdragonsong.appspot.com'
    TOKEN_FRESH_FOR = 115

    # can rotate between pool here



    def getToken(self):
        if time.time() - self.token_time < self.TOKEN_FRESH_FOR:
            return self.token
        auth_code = hostinfo.appEmail + "|" + hostinfo.clientID
        params = dict(auth_code=auth_code,
            client_id=PGAPI.CLIENT_ID,
            client_secret=PGAPI.CLIENT_SECRET)
        token_url = f'https://{PGAPI.AUTH_SERVER}/api/dev/retrieve_token?{urlencode(params, quote_via=quote_plus)}'
        resp = requests.get(token_url)
        self.token = resp.json()
        self.token_time = time.time()
        return self.token

    def __init__(self, autofetch=True, old=False, **kwargs):
        self.autofetch = autofetch
        self.params = None
        self.body = None
        self.rate_limit_seconds = 0
        self.old = old
        self.OLD_API_URL = None
        self.token = None
        self.token_time = 0
        self.rate_limit_items = 0
        self.parallel = False

        if 'api_keys' in kwargs:
            self.api_keys = kwargs.get('api_keys')
        elif 'api_key' in kwargs:
            self.api_key = kwargs.get('api_key')
        else:
            self.token = self.getToken()
            if 'api_key' not in self.token:
                raise ValueError("API key missing")
            else:
                self.api_key = self.token['api_key']

    


    def genHeaders(self,api_key=None):
        if not api_key:
            api_key = self.api_key

        now = datetime.utcnow()
        msg = ':'.join([PGAPI.CLIENT_SECRET, api_key, str(int(now.timestamp()))]).encode('utf-8')
        generated_signature = hashlib.sha256(msg).hexdigest()
        return hostinfo.reduced_headers if self.old else {'expires':str(int((now+timedelta(seconds=self.rate_limit_seconds)).timestamp())),'X-WarDragons-APIKey':api_key, 'X-WarDragons-Request-Timestamp': str(int(now.timestamp())), 'X-WarDragons-Signature':str(generated_signature)}

    def fetch(self, headers=None, params=None, api_key=None):
        if not api_key:
            api_key = self.api_key
        if not params:
            params = self.params

        """
        if time.time() - self.token_time > self.TOKEN_FRESH_FOR:
            self.token = self.getToken()
            self.api_key = self.token['api_key']
        """
        if headers==None:
            headers = self.genHeaders(api_key=api_key)
        working_url = self.API_URL if not (self.old and self.OLD_API_URL) else self.OLD_API_URL
        #print("PARAMS", params)        
        resp = requests.get(working_url, headers=headers, params=params)

        #print(working_url, self.genHeaders(), self.params)
        if resp.status_code == 200:

            #return {"cached":resp.from_cache, **resp.json()}
            return resp.json()
            """
            if isinstance(resp.json(), list):
                return {"cached":resp.from_cache, "data":resp.json()}
            else:
                return {"cached":resp.from_cache, **resp.json()}
            """
        else:
            #print("resp", resp)
            #print("content", resp.content)
            if resp.json().get('error'):
                
                raise PGApiError(resp.json().get('error'))
            else:
                raise HTTPError(f"Request to {working_url} failed (HTTP {resp.status_code})\nBody: {resp.text}")


    

    def parallel_fetch(self, fetch_items=None, prefix=None, params=None, caching_prefix=None, cache_item_size=0):
        if not fetch_items:
            fetch_items = self.items
        if not prefix:
            prefix = self.prefix
        if not params:
            params = self.params
        def run_fn(data, worker):
            instance_params = dict(params)
            if prefix:
                instance_params[prefix] = json.dumps(data)
            return self.fetch(params=instance_params, api_key=worker)
        return util.run_on_items(run_fn, items=fetch_items, batch_size=self.rate_limit_items, rate_limit_time=self.rate_limit_seconds, max_pool=40, workers=self.api_keys, caching_prefix=caching_prefix, cache_item_size=cache_item_size)

    def post(self):
        headers = self.genHeaders()
        headers['Content-Type'] = "application/json"
        working_url = self.API_URL if not self.old else self.OLD_API_URL
        resp = requests.post(working_url, headers=headers, data=self.body)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise HTTPError(f"Request to {working_url} failed (HTTP {resp.status_code})\nBody: {resp.text}")

    def __str__(self):
        return json.dumps(self.data)
    def get_data(self):
        return self.data


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
        self.rate_limit_seconds = 5
        self.rate_limit_items = 25
        self.parallel = True 
        self.caching_prefix = kwargs.get('caching_prefix', None)
        self.cache_item_size = kwargs.get('cache_item_size', 0)

        if not self.query_cont_ids or type(self.query_cont_ids) != type([]):
            raise ValueError("Field <list of str or dict>'cont_ids' missing or not recognized")

        for cont_id in self.query_cont_ids:
            if type(cont_id) == type(str()):
                match = re.search('^1-(\w\d+)-(\d)', cont_id)
                if match:
                    self.cont_ids.append({'cont_idx':int(match.group(2)), 'k_id':1, 'region_id': match.group(1)})
                else:
                    raise ValueError(f"Error parsing castle: <str>'{cont_id}'")
            elif type(cont_id) == type(dict()):

                self.cont_ids.append({**cont_id})

        self.items = self.cont_ids
        #self.params = {'cont_ids': self.cont_ids} #self.cont_ids #{'cont_ids': json.dumps(self.cont_ids)}
        self.params = {}
        self.prefix = 'cont_ids'

        if self.autofetch==True:
            
            #print(self.api_keys)
           # def run_fn(data, worker):
            #    return self.fetch(params=data, api_key=worker)
           # results = util.run_on_items(run_fn, items=self.params, batch_size=self.rate_limit_items, rate_limit_time=self.rate_limit_seconds, workers=self.api_keys)
            self.data = self.parallel_fetch(caching_prefix=self.caching_prefix, cache_item_size=self.cache_item_size)
            #self.data.pop("cached", None)
        else:
            self.data = None


class CastleMetadata(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rate_limit_seconds = 60
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/castles/metadata/macro'
        self.params = {'k_id':1, 'realm_name':'Celestial_Haven'}
        self.data = self.fetch() if self.autofetch==True else None


##### Teams API #####

class AtlasContribution(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/team/contribution'
        self.rate_limit_seconds = 60
        self.data = self.fetch() if self.autofetch==True else None
        for player in self.data['entries']:
            setattr(self, player['for_name'], player['stats'])


class AtlasTeamsMetadata(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rate_limit_seconds = 60
        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/teams/metadata/macro'
        self.params = {'k_id':1, 'realm_name':'Celestial_Haven'}
        self.data = self.fetch() if self.autofetch==True else None


class AtlasTeam(PGAPI):

    def __init__(self, teams, **kwargs):
        super().__init__(**kwargs)
        self.params = teams
        self.teams = teams

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/teams/metadata'
        self.params = {'k_id':1, 'realm_name':'Celestial_Haven'}
        self.rate_limit_seconds = 60
        self.rate_limit_items = 100
        #if kwargs.get('teams'):
            #self.params['teams'] = json.dumps(kwargs.get('teams'))

        self.items = teams
        self.prefix = "teams"
        self.data = self.parallel_fetch() if self.autofetch==True else None
        #self.data.pop("cached", None)


class AtlasBattles(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/team/battles'
        self.params = {}
        self.rate_limit_seconds = 60
        if kwargs.get('cursor'):
            self.params['cursor'] = kwargs.get('cursor')
        self.data = self.fetch() if self.autofetch==True else None


class AtlasMonthlyKills(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/teams/monthly_kill_count'
        self.body = {"teams": []}
        self.rate_limit_seconds = 40
        if kwargs.get('teams') and isinstance(kwargs.get('teams'),list):
            self.body = json.dumps({"teams": kwargs.get('teams')})
        else:
            raise ValueError("Required argument teams missing or not of type <list>")
            return
        self.data = self.post() if self.autofetch==True else None

class AllAtlasMonthlyKills(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/teams/monthly_kill_count'
        self.rate_limit_seconds = 40
        self.body = json.dumps({"teams":list((json.load(open("/Library/WebServer/CGI-Executables/map/map.json", "r")))['metadata']['teams'].keys())})
        self.data = self.post() if self.autofetch==True else None




class AtlasTroopCount(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/team/troop_count'
        self.params = {}
        self.rate_limit_seconds = 600
        self.data = self.fetch() if self.autofetch==True else None


class AtlasAlliances(PGAPI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/alliance/teams'
        self.params = {}
        self.rate_limit_seconds = 3600
        self.data = self.fetch() if self.autofetch==True else None


class AtlasEventScore(PGAPI): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.API_URL = f'https://{PGAPI.API_SERVER}/api/v1/atlas/player/event/score'
        self.params = {}
        self.rate_limit_seconds = 60
        self.data = self.fetch() if self.autofetch==True else None