# ----------------------------------------------------------------------------
# "THE SCOTCH-WARE LICENSE" (Revision 42):
# <DonMarco42@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a scotch whisky in return
# Marco 'don' Kaulea
# ----------------------------------------------------------------------------

import requests
import json
import functools

USER_AGENT = 'easy.GO Client Android v1.2.1 '\
    '(Mozilla/5.0 (Linux; Android 4.4.4; Nexus 4 Build/KTU84Q) '\
    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 '\
    'Mobile Safari/537.36)'

API_DOMAIN = 'http://rnv.the-agent-factory.de:8080'
SITE_URL = '/easygo2/rest/regions/rnv/modules/'
DEPARTURES_URL = 'stationmonitor/element'
STATIONS_URL = 'stations/packages/1'

dump_json = functools.partial(json.dumps,
                              indent=4,
                              ensure_ascii=False,
                              sort_keys=True)
stations = None


def find_station_by_short_name(name):
    if stations is None:
        get_stations()
    name = name.upper()
    station = next((item for item in stations if item['shortName'] == name))
    return station


def find_station_by_long_name(name):
    if stations is None:
        get_stations()
    name = name.casefold()
    matches = (item for item in stations if item['longName'].casefold() == name)
    return next(matches)


def find_stations_by_long_name(name):
    if stations is None:
        get_stations()
    name = name.casefold()
    return (item for item in stations if name in item['longName'].casefold())


def get_hafasid_from_name(name):
    hafasid = None
    if len(name) == 4 and name.isupper():
        return find_station_by_short_name(name)['hafasID']
    else:
        return find_station_by_long_name(name)['hafasID']
    return hafasid


def get_departures(hafasID,
                   transport_filter=None,
                   time=None,
                   ui_source='LINE'):
    payload = {'hafasID': hafasID,
               'transportFilter': transport_filter,
               'time': time if time is not None else 'null',
               'usSource': ui_source}
    headers = {'Accept': 'application/json',
               'Accept-Language': 'de',
               'User-Agent': USER_AGENT}
    r = requests.get("".join([API_DOMAIN, SITE_URL, DEPARTURES_URL]),
                     params=payload,
                     headers=headers)
    if r.status_code != 200:
        raise Exception(r)
    else:
        r.encoding = 'utf-8'
        data = json.loads(r.text)
        if data.get('color', 0x464d59) != 0x464d59:
            return data
        else:
            raise Exception("Not Found")


def get_stations():
    data = json.loads(get_stations_raw())
    global stations
    stations = data['stations']
    return stations


def get_stations_raw():
    headers = {'Accept': 'application/json',
               'Accept-Language': 'de',
               'User-Agent': USER_AGENT}
    r = requests.get("".join([API_DOMAIN, SITE_URL, STATIONS_URL]),
                     headers=headers)
    if r.status_code != 200:
        raise Exception(r)
    else:
        r.encoding = 'utf-8'
        return r.text
