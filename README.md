# War Dragons API client

## Usage

    git clone https://gitlab.macgenius.me/Faive/WarDragonsAPI

Modify api.py file and with your CLIENT_ID and CLIENT_SECRET.

### API

Response data is always written to Class().data attribute as dict

#### Player(api_key)

Fetches profile of api_key owner

    p = Player(api_key='apikey-xxxxxxxxxxxx')
    p.data.get('name')			#Prints players name

#### CastleInfo(api_key, cont_ids)

cont_ids can lighter be a list of dict's or a list of strings or even a mix of both

    ['1-A123-0', {'k_id':1, 'cont_idx':1, 'region_id':'A123'}]

#### AtlasTeamsMetadata(api_key)
All teams metadata, including rankings and passage

#### AtlasTeam(api_key, team_name)
Given team's metadata

#### AtlasContribution(api_key)
Atlas contribution for api_key owners team (monthly gold, shards, kills)

### APP

Example Flask app implementing OAuth2 authentication against War Dragons API and uses received api_key for an example api.py call

    pip3 install -r requirements.txt
    python3 app.py

