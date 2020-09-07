#!/usr/local/bin/python

import requests
import hostinfo
from math import ceil as ceil
from concurrent.futures import ThreadPoolExecutor as PoolExecutor, wait, as_completed
import time 
import random
import json
import sys
import traceback
import time
"""
import logging

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""

politenessList = ["--polite", "ANGELSnDEM0NS", "Hard2Own", "TrueValar", "DragonOfKorea"] #frens
max_cont = 28

def get_token():
	auth_code = hostinfo.appEmail + "|" + hostinfo.clientID
	params = dict(auth_code=auth_code,
    	client_id=PGAPI.CLIENT_ID,
    	client_secret=PGAPI.CLIENT_SECRET)
	token_url = f'https://{PGAPI.AUTH_SERVER}/api/dev/retrieve_token?{urlencode(params, quote_via=quote_plus)}'
	resp = requests.get(token_url)
	resp_data = resp.json()
	return resp_data

#works
def get_metadata():
	params = {'realm_name':'Celestial_Haven', 'k_id':1}
	url = 'https://'+hostinfo.hostname+'/ext/dragonsong/world/macro_view/get_metadata'
	return requests.get(url=url, params=params)

# needs info
def get_team(team):
	url = 'https://'+hostinfo.hostname+'/guild/info'
	#cookie method data = {'guild_name':team} #, 'player_id':hostinfo.player_id}
	data = {'guild_name':team, 'player_id':hostinfo.player_id, 'session_token':hostinfo.session_token}
	return requests.post(url=url, data=data, headers=hostinfo.reduced_headers_guild)#, headers=hostinfo.headers_guild)

# needs info
def get_passage(team):
	#cookie method params = { "guild_name":team}
	url = 'https://'+hostinfo.hostname+'/ext/dragonsong/world/team/alliance/free_passage'
	params = {"guild_name":team, 'player_id':hostinfo.player_id, 'session_token':hostinfo.session_token}
	return requests.get(url=url, params=params, headers=hostinfo.reduced_headers)

# needs info
def get_castle(cont_ids):
	contString = "[" + ",".join(cont_ids) + "]"
	params = {"session_token":hostinfo.session_token, "cont_ids":contString, "player_id":hostinfo.player_id, "drake_locs":hostinfo.drakeString}				
	url = 'https://'+hostinfo.hostname+'/ext/dragonsong/world/area/get'
	response = requests.get(url=url, params=params, headers=hostinfo.reduced_headers, timeout=15)
	print(response.content)
	return response


def get_castles(cont_ids):
	strings = ['{"cont_idx":' + str(lookup['cont_idx']) + ',"k_id":'+str(lookup['k_id'])+',"region_id":"'+str(lookup['region_id']) + '"}' for lookup in cont_ids]
	contString = "[" + ",".join(strings) + "]"
	params = {"session_token":hostinfo.session_token, "cont_ids":contString, "player_id":hostinfo.player_id, "drake_locs":hostinfo.drakeString}				
	url = 'https://'+hostinfo.hostname+'/ext/dragonsong/world/area/get'
	response = requests.get(url=url, params=params, headers=hostinfo.reduced_headers, timeout=15)
	#print(response.content)
	return response

#works
def get_contribs(team):
	params = {"guild_name":team, "mini_lb_name":"WorldMapTeamContributionLeaderboard"}
	response = requests.get(url='https://'+hostinfo.hostname+'/leaderboard/mini/get_stats_for_team', params=params, headers=hostinfo.cookieless_headers)
	return response

# works
def get_troops(pgids):
	params = {"sig_ver":2, "sig_ts":time.time(), "ids":str(['drg-worldmap-shipcount-' + k for k in pgids]).replace('\'', '\"') }
	url = 'https://'+hostinfo.hostname+'/leaderboard/view_entry'
	response = requests.get(url=url, params=params, headers=hostinfo.cookieless_headers)
	return response


# needs cookie
def get_profiles(pgids, decode=True):
	"""
	pgids = json.dumps(pgids)
	params = {"ids":pgids}
	url = 'https://'+hostinfo.hostname+'/player/profile'
	response = requests.get(url=url, headers=hostinfo.headers, params=params)
	"""
	url = 'https://'+hostinfo.hostname+'/leaderboard/view_entry'
	params = {"sig_ver":2, "sig_ts":time.time(), "ids":str(['individual-trophies-alltime-' + k for k in pgids]).replace('\'', '\"'), 'omit_profile':0, 'omit_entry':0}
	response = requests.get(url=url, params=params, headers=hostinfo.cookieless_headers)
	if not decode:
		return response
	response = response.content.decode("utf-8").replace('"{', '{').replace('}"', '}').replace('\\\"', "\"").replace("\\\\", "\\")
	response = json.loads(response) 
	response = {p['profile']['pgid']:p['profile'] for p in response if 'profile' in p}
	return response

#needs ids
def get_battle_log(cursor=None):
	params = {"session_token":hostinfo.and_session_token, "player_id":hostinfo.and_player_id, "player_only":0}
	if cursor:
		params['cursor'] = cursor
	url = "https://" + hostinfo.hostname + "/ext/dragonsong/world/battle/reports"
	response = requests.get(url, headers=hostinfo.cookieless_headers, params=params)
	return response

#needs cookie
def get_current_base_event():
	#params = {}
	url = "https://"+hostinfo.hostname+"/ext/dragonsong/event/about"
	params = {'player_id':hostinfo.player_id, 'session_token':hostinfo.session_token}
	eventHeaders = dict(hostinfo.reduced_headers)
	"""
	for key in ["Accept", "Content-Type", "Accept-Language"]:
		del eventHeaders[key]
	"""
	response = requests.get(url=url, params=params, headers=eventHeaders)
	return response

#needs info
def get_current_atlas_event():
	url = "https://"+hostinfo.hostname+"/ext/dragonsong/world/get_params"
	params = {"player_id":hostinfo.player_id, "session_token":hostinfo.session_token}
	eventHeaders = dict(hostinfo.reduced_headers)
	"""
	for key in ["Accept", "Content-Type", "Accept-Language"]:
		del eventHeaders[key]
	"""
	response = requests.get(url=url, params=params, headers=eventHeaders)
	return response

# works
def get_event_scores(team, eventName):

	url = "https://"+hostinfo.hostname+"/leaderboard/mini/get_stats_for_team"
	params = {"guild_name":team, "mini_lb_name":"drg-gameevent-"+eventName+"-player-global"}
	tries = 0
	max_tries = 3
	response = None
	while tries < max_tries:
		try:
			response = requests.get(url=url, params=params, headers=hostinfo.cookieless_headers)
			tries = max_tries
		except:
			tries += 1
	return response

#works
def get_leaderboard_lifetime_kills(n=100):
	url = 'https://'+hostinfo.hostname+'/leaderboard/view'
	data = {'omit_profile':0, 'n':n, 'omit_entry':0, 'board':'drg-worldmap-killship-alltime'}
	response = requests.get(url=url, params=data, headers=hostinfo.cookieless_headers)
	return response

#works
def get_seasonal_rank(teams):
	quotedTeams = ["\""+t+"\"" for t in teams]
	params = {"teams":"["+",".join(quotedTeams)+"]"}
	url = 'https://'+hostinfo.hostname+'/ext/dragonsong/world/season/rounds/leaderboard/entry'
	response = requests.get(url=url, params=params, headers=hostinfo.cookieless_headers)
	return response

#works
def get_team_profiles(teams, decode=True):
	"""
	url = 'https://'+hostinfo.hostname+'/guild/profile'
	data = {'ids':json.dumps(teams)}
	headers = hostinfo.headers
	headers['Cache-Control'] = 'no-cache'
	response = requests.get(url=url, params=data, headers=headers)
	"""
	teams = ["guild-elo-alltime-"+team for team in teams]
	url = 'https://'+hostinfo.hostname+'/leaderboard/view_entry'
	params = {'sig_ver':2, 'omit_profile':0, 'omit_entry':0, 'sig_ts':time.time(), 'ids':json.dumps(teams)}
	headers = hostinfo.cookieless_headers
	response = requests.get(url=url, params=params, headers=headers)
	if not decode:
		return response

	response = response.content.decode("utf-8").replace('"{', '{').replace('}"', '}').replace('\\\"', "\"").replace("\\\\", "\\")
	response = json.loads(response)  # .replace("\\","").replace('\\\\\\\"', '\\\''))
	#response = response.content.decode("utf-8")
#	https://525-dot-pgdragonsong.appspot.com/leaderboard/view_entry?sig_ver=2&ids=%5B%22guild-elo-alltime-DerpyBlobs%22%5D&sig_ts=1597968242.898174&omit_profile=0&sig_nonce=-963513914&omit_entry=0&sig=8264424f059a81669e866393c9e56d0fe5e91ef8f344ab5a08a726845c76f454
	return response

def all_teams():
	f = open("existingTeams.txt", "r")
	teams = f.readline().strip('\n').split(",")
	f.close()
	return teams

def run_on_items(run_fn, items, batch_size=0, rate_limit_time=0, rate_limit_items=0, total_time=0, noise=False, max_pool=4, workers=[]):
	results = []

	batches = []
	batch_size = max(batch_size, rate_limit_items) #lol
	if batch_size:		
		for i in range(0, len(items), batch_size):
			batch = items[i:i + batch_size]
			batches.append(batch)
	else:
		batches = items

	n_batches = len(batches)
	n_workers = len(workers)
	time_per_request = max(rate_limit_time, total_time / max(n_batches - 1, 1))
	buffer_time = 1

	def run_linearly_on_batches(batches, worker=None, noise=noise):
		linear_results = []
		for i, batch in enumerate(batches):
			start_time = time.time()
			#print("yo: ", batch, worker, run_fn)
			def fetch_batch():
				batch_result = run_fn(batch) if worker == None else run_fn(data=batch, worker=worker)
				return batch_result 
			result = tryN(fetch_batch, 1)

			linear_results.append(result)
			end_time = time.time()
			sleep_time = time_per_request - (end_time - start_time) % time_per_request
			if noise and time_per_request > rate_limit_time:
				sign = random.randint(0, 1)
				sign = (sign - 1) + sign
				noise = sign * random.uniform(0, sleep_time / 4)
				sleep_time = max(rate_limit_time, sleep_time + noise)
				noise = sign * random.uniform(0, sleep_time / 4)
				sleep_time = max(rate_limit_time, sleep_time + noise)
				#print(sleep_time)
			if i != n_batches - 1:
				sleep_time = max(sleep_time, 0)
				time.sleep(sleep_time)
		return linear_results

	if (rate_limit_time == 0 and total_time == 0) or workers:

		pool = PoolExecutor(min(n_batches, max(n_workers, max_pool)))
		if workers:
			worker_slice_size = int(n_batches / n_workers) if (n_batches % n_workers == 0) else int((n_batches / n_workers)+1)
			worker_slices = []
			for i in range(0, n_batches, worker_slice_size):
				worker_slices.append(batches[i:i+worker_slice_size])
			zipped_slices = zip(workers, worker_slices)
			def zipped_fn(zipped):
				return run_linearly_on_batches(zipped[1], worker=zipped[0])
			# current idea: fun_fn must take a worker argument
			"""
			def zipped_fn(worker, arg):
				return run_fn()
			# how do you apply the worker function? 
			#zip workers and slices together
			def worker_fn(worker_slice):
				results = []
				for batch in worker_slice:
					result = run_fn(batch)
					results.append(result)
			"""
			futures = [pool.submit(zipped_fn,zipped) for zipped in zipped_slices]
			results = [r.result() for r in as_completed(futures)]
			results = [i for sublist in results for i in sublist] #flatten slices
		else:

			futures = [pool.submit(run_fn,batch) for batch in batches]
			results = [r.result() for r in as_completed(futures)]
	else:
		results = run_linearly_on_batches(batches)
	return results

def sleepFn(tries):
	time.sleep(tries*2)
	return

def print_exception(e):
	print(e)
	print(sys.exc_info()[0])
	traceback.print_exc()
	return



def tryN(fn, max_tries, exceptFn=sleepFn):
	result = None
	tries = 0
	while tries < max_tries:
		try:

			result = fn()
			print("success")
			tries = max_tries
		except Exception as e:
			print (e)
			print(sys.exc_info()[0])
			traceback.print_exc()
			if exceptFn:
				exceptFn(tries)
			tries += 1
			if tries >= max_tries:
				exit()
	return result
