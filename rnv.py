#!/usr/bin/env python3
"""
rnv

Usage:
    rnv departures IDENTIFIER [-f FILTER | --filter=FILTER] [-n COUNT]
    rnv stations

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
    transport_filter = args.get('FILTER', None)
    if args['IDENTIFIER'].isnumeric():
        json_data = rnv_api.get_departures(int(args['IDENTIFIER']),
                                           transport_filter=transport_filter)
        print("Current Time: {0}".format(json_data['time']))
        if json_data.get('ticker', False):
            print("Ticker: {0}".format(json_data['ticker']))
        if args.get('-n', False):
            n = int(args.get('COUNT', 0))
            for dep in json_data['listOfDepartures'][:n]:
                print(dump_json(dep))
        else:
            for dep in json_data['listOfDepartures']:
                print(dump_json(dep))


def main():
    arguments = docopt.docopt(__doc__)
    if arguments.get('departures', False):
        get_departures_from_arg(arguments)
    elif arguments.get('stations', False):
        json_data = rnv_api.get_stations()
        print(json.dumps(json_data,
                         indent=4,
                         ensure_ascii=False,
                         sort_keys=True))

if __name__ == '__main__':
    main()
