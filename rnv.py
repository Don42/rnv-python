#!/usr/bin/env python3
"""
rnv

Usage:
    rnv departures IDENTIFIER [-f FILTER -n COUNT -t TIME]
    rnv stations
    rnv news [count | show]
    rnv ticker [count | show]


-f FILTER --filter=FILTER  Define transport filter
-n COUNT --count=COUNT     Only display first COUNT connections
-t TIME --time=TIME        Query connection at TIME

"""

import docopt
import json
import functools

import rnv_api


dump_json = functools.partial(json.dumps,
                              indent=4,
                              ensure_ascii=False,
                              sort_keys=True)


def get_departures_from_arg(args):
    """Gets departures from arguments and prints them

    Gets arguments from dictionary, if necessary retrieves the HafasID from
    station name and calls the api to get the departure data.

    """
    transport_filter = args.get('--filter', None)
    time = args.get('--time', None)
    if args['IDENTIFIER'].isnumeric():
        hafas_id = int(args['IDENTIFIER'])
    else:
        hafas_id = int(rnv_api.get_hafasid_from_name(args['IDENTIFIER']))

    json_data = rnv_api.get_departures(hafas_id,
                                       transport_filter=transport_filter,
                                       time=time)
    print("Current Time: {0}".format(json_data['time']))
    if json_data.get('ticker', False):
        print("Ticker: {0}".format(json_data['ticker']))
    if args.get('--count', False):
        n = int(args.get('--count', 0))
        for dep in json_data['listOfDepartures'][:n]:
            print(dump_json(dep))
    else:
        for dep in json_data['listOfDepartures']:
            print(dump_json(dep))


def get_news_from_arg(args):
    """Get news from arguments

    Differntiates between 'count' and 'show', calls the API
    and prints the result.

    """
    if(args.get('count', False)):
        count = rnv_api.get_news_count()
        print("{} news items available".format(count))
    else:
        news = rnv_api.get_news()
        if news:
            print(dump_json(news))
        else:
            print("No news available")


def get_ticker_from_arg(args):
    """Get ticker from arguments

    Differntiates between 'count' and 'show', calls the API
    and prints the result.

    """
    if(args.get('count', False)):
        count = rnv_api.get_ticker_count()
        print("{} ticker items available".format(count))
    else:
        ticker = rnv_api.get_ticker()
        if ticker:
            print(dump_json(ticker))
        else:
            print("New ticker items available")


def main():
    """Differentiates between commands

    """
    arguments = docopt.docopt(__doc__)
    if arguments.get('departures', False):
        get_departures_from_arg(arguments)
    elif arguments.get('stations', False):
        json_data = rnv_api.get_stations()
        print(dump_json(json_data))
    elif arguments.get('news', False):
        get_news_from_arg(arguments)
    elif arguments.get('ticker', False):
        get_ticker_from_arg(arguments)

if __name__ == '__main__':
    main()
