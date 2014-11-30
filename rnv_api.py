# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# "THE SCOTCH-WARE LICENSE" (Revision 42):
# <DonMarco42@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a scotch whisky in return
# Marco 'don' Kaulea
# ----------------------------------------------------------------------------
"""Bindings for the Web-API from rnv.

Attributes:
    USER_AGENT (string): User agent sent to the server.
    API_DOMAIN (string): Protocol, host, and port of the URL.
    SITE_URL (string): Part of the URL that stays the same for all requests.
    DEPARTURES_URL (string): Part of the URL to query the departures.
    STATIONS_URL (string): Part of the URL to query the stations.
    NEWS_URL (string): Part of the URL to query news.
    NEWS_COUNT_URL (string): Part of the URL to query the news count.
    TICKER_URL (string): Part of the URL to query tickers.
    TICKER_COUNT_URL (string): Part of the URL to query ticker count
        to prettyfied json.
    stations (list): Cache of all stations.
        It is filled and updated by get_stations().

"""
import requests
import json
import re

USER_AGENT = 'easy.GO Client Android v1.2.1 '\
    '(Mozilla/5.0 (Linux; Android 4.4.4; Nexus 4 Build/KTU84Q) '\
    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 '\
    'Mobile Safari/537.36)'

API_DOMAIN = 'http://rnv.the-agent-factory.de:8080'
SITE_URL = '/easygo2/rest/regions/rnv/modules/'
DEPARTURES_URL = 'stationmonitor/element'
STATIONS_URL = 'stations/packages/1'
NEWS_URL = 'news'
NEWS_COUNT_URL = 'news/numberOfNewEntries/0'
TICKER_URL = 'ticker'
TICKER_COUNT_URL = 'ticker/numberOfNewEntries/0'

stations = None


def find_station_by_short_name(name):
    """Find a station by its short name

    Matches are case insensitiv.
    Only the first of several matches is returned.
    Args:
        name (string): short name of the station.
        The string has to be a valid short name.

    Returns:
        dict: Station object  if found

    Raises:
        StopIteration: If no station is found

    """
    if stations is None:
        get_stations()
    name = name.upper()
    station = next((item for item in stations if item['shortName'] == name))
    return station


def find_station_by_long_name(name):
    """Find a station by its long name

    Matches are case insensitiv.
    Only the first of several matches is returned.
    Args:
        name (string): long name of the station.

    Returns:
        dict: Station object  if found

    Raises:
        StopIteration: If no station is found

    """
    if stations is None:
        get_stations()
    name = name.casefold()
    matches = (item for item in stations if item['longName'].casefold() == name)
    return next(matches)


def find_stations_by_long_name(name):
    """Find stations by their long name

    Matches are case insensitiv.
    Args:
        name (string): long name of the station.

    Returns:
        generator: This generator allows to iterate over all matches.

    """
    if stations is None:
        get_stations()
    name = name.casefold()
    return (item for item in stations if name in item['longName'].casefold())


def get_hafasid_from_name(name):
    """Find the hafas id by searching the stations vor a provied name

    Args:
        name (string): Either short or long name

    Returns:
        string: hafas id

    Raises:
        StopIteration: If no station is found

    """
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
    """Get departures by hafas id

    Args:
        hafasID (int): This can be looked up by get_hafasid_from_name.
        transport_filter (string, optional): Filter departure by line.
            Defaults to None.
        time (string): Query departures from specific time. This has
            to be a complete ISO-Date "YYYY-MM-DD HH:MM"

    Returns:
        list: List of departure dictionaries

    Raises:
        Exception: If there are no departures

    """
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
    """Retrieves stations and store into cache

    Returns:
        list: List of stations dictionaries

    """
    data = json.loads(get_stations_raw())
    global stations
    stations = data['stations']
    return stations


def get_stations_raw():
    """Retrieves stations

    Returns:
        string: Unparsed content from the API

    Raises:
        Exception: If the status code is not 200

    """
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


def get_news():
    """Retrieves news

    Returns:
        list: List of news dictionaries

    Raises:
        Exception: If the status code is not 200

    """
    headers = {'Accept': 'application/json',
               'Accept-Language': 'de',
               'User-Agent': USER_AGENT}
    r = requests.get("".join([API_DOMAIN, SITE_URL, NEWS_URL]),
                     headers=headers)
    if r.status_code != 200:
        raise Exception(r)
    else:
        r.encoding = 'utf-8'
        return json.loads(r.text)


def get_news_count():
    """Retrieves number of news items.

    Returns:
        int: Number of news items

    Raises:
        Exception: If the status code is not 200

    """
    headers = {'Accept': 'application/json',
               'Accept-Language': 'de',
               'User-Agent': USER_AGENT}
    r = requests.get("".join([API_DOMAIN, SITE_URL, NEWS_COUNT_URL]),
                     headers=headers)
    if r.status_code != 200:
        raise Exception(r)
    else:
        r.encoding = 'utf-8'
        pattern = re.compile(r'\{number:"(\d+)"\}')
        m = pattern.fullmatch(r.text)
        return m.group(1)


def get_ticker():
    """Retrieves ticker.

    Returns:
        list: List of ticker dictionaries

    Raises:
        Exception: If the status code is not 200

    """
    headers = {'Accept': 'application/json',
               'Accept-Language': 'de',
               'User-Agent': USER_AGENT}
    r = requests.get("".join([API_DOMAIN, SITE_URL, TICKER_URL]),
                     headers=headers)
    if r.status_code != 200:
        raise Exception(r)
    else:
        r.encoding = 'utf-8'
        return json.loads(r.text)


def get_ticker_count():
    """Retrieves number of ticker items.

    Returns:
        int: Number of ticker items

    Raises:
        Exception: If the status code is not 200

    """
    headers = {'Accept': 'application/json',
               'Accept-Language': 'de',
               'User-Agent': USER_AGENT}
    r = requests.get("".join([API_DOMAIN, SITE_URL, TICKER_COUNT_URL]),
                     headers=headers)
    if r.status_code != 200:
        raise Exception(r)
    else:
        r.encoding = 'utf-8'
        pattern = re.compile(r'\{number:"(\d+)"\}')
        m = pattern.fullmatch(r.text)
        return m.group(1)
