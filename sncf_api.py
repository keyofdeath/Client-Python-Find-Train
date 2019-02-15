#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import json
import logging.handlers
import os
from datetime import datetime

import requests

PYTHON_LOGGER = logging.getLogger(__name__)
if not os.path.exists("log"):
    os.mkdir("log")
HDLR = logging.handlers.TimedRotatingFileHandler("log/SncfApi.log",
                                                 when="midnight", backupCount=60)
STREAM_HDLR = logging.StreamHandler()
FORMATTER = logging.Formatter("%(asctime)s %(filename)s [%(levelname)s] %(message)s")
HDLR.setFormatter(FORMATTER)
STREAM_HDLR.setFormatter(FORMATTER)
PYTHON_LOGGER.addHandler(HDLR)
PYTHON_LOGGER.addHandler(STREAM_HDLR)
PYTHON_LOGGER.setLevel(logging.DEBUG)

# Absolute path to the folder location of this python file
FOLDER_ABSOLUTE_PATH = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))

# Sncf api token
TOKEN = '84f17708-373d-4da1-b728-233be34f2336'
# Abs path to the stations
STATIONS_DB = os.path.join(FOLDER_ABSOLUTE_PATH, "french_stations.json")


def stations_pages(page_number):
    """
    Get all stations information
    :param page_number: (int) page number
    :return: (request) request of the page
    """
    return requests.get('https://api.sncf.com/v1/coverage/sncf/stop_areas?start_page={}'.format(page_number),
                        auth=(TOKEN, ''))


def api_date_to_python_date(api_date):
    """
    Convert the api string date to python date
    Y-m-d H-M-S
    :param api_date: (string) date to convert
    :return: (datetime)
    """
    return datetime.strptime(api_date.replace('T', ''), '%Y%m%d%H%M%S')


def python_date_to_api_date(python_date):
    """
    Convert a python date to the api date format
    :param python_date: (datetime) date to convert
    :return: (string) Reformat date
    """
    return datetime.strftime(python_date, '%Y%m%dT%H%M%S')


def get_all_station():
    """
    Generate a json file with all the stations and informations
    """
    page_initiale = stations_pages(0)
    item_per_page = page_initiale.json()['pagination']['items_per_page']
    total_items = page_initiale.json()['pagination']['total_result']
    print_done = {}
    json_out_list = []
    # walk throu al pages
    for page in range(int(total_items / item_per_page) + 1):

        stations_page = stations_pages(page)
        stations_page_json = stations_page.json()

        if 'stop_areas' not in stations_page_json:
            continue

        # We get just the intresting information
        for station in stations_page_json['stop_areas']:

            station['lat'] = station['coord']['lat']
            station["lon"] = station['coord']['lon']

            if 'administrative_regions' in station.keys():
                for var_api, var_df in zip(['insee', 'name', 'label', 'id', 'zip_code'],
                                           ['insee', 'region', 'label_region', 'id_region', 'zip_code']):
                    try:
                        station[var_df] = station['administrative_regions'][0][var_api]
                    except KeyError:
                        if var_api not in print_done:
                            PYTHON_LOGGER.info("key '{0}' "
                                               "not here but {1}".format(var_api,
                                                                         ",".join(station['administrative_regions'][0]
                                                                                  .keys())))
                            print_done[var_api] = var_api

            [station.pop(k, None) for k in ['coord', 'links', 'administrative_regions', 'type', 'codes']]

        stations = stations_page_json['stop_areas']
        json_out_list.extend(stations)
        PYTHON_LOGGER.info("Page {} done !".format(page))

    with open(STATIONS_DB, "w") as json_out:
        json_out.write(json.dumps(json_out_list, indent=2, sort_keys=True))


def found_station(station_name):
    """
    Found a sation corespoding with the input name
    :param station_name: (string) name of the station to found
    :return:(list of string) Names of all the station match with the input name
    """
    station_name_reformat = station_name.strip().lower().replace(' ', '-')
    with open(STATIONS_DB) as db_json:
        json_stations = json.load(db_json)

    all_stations_result = []
    for station in json_stations:
        town = station["label"][station["label"].find('(') + 1:station["label"].find(')')].lower().strip()
        station_name_get = station["label"][:station["label"].find('(')].lower().strip()
        if station["label"] == station_name:
            return [station]
        # Look if we have the exact match
        elif station_name_reformat in town or station_name_reformat in station_name_get:
            all_stations_result.append(station)
    return all_stations_result


def get_departures_time(station_start, station_end, date):
    """
    Get departures time of a destination
    :param station_start: (string) Name of the start station
    :param station_end: (string) Name of the destination station
    :param date: (string) YYYY-MM-DD HH:MM date and time you want to go
    :return: (dic) {"departures": list of all the departures houre,
                    "lat_end": Latitiude of the station end,
                    "lon_end": Longitude of the station end,
                    "lat_start": Latitiude of the station start,
                    "lon_start": Longitude of the station start,
                    "station_start_name": Name of the station found,
                    "station_end_name": Name of the station found

    """
    # set the date time to the api format YYYMMDDTHHMMSS
    date = date.replace('-', '').replace(' ', 'T').replace(':', '') + '00'
    try:
        station_start_json = found_station(station_start)[0]
        station_end_json = found_station(station_end)[0]
        station_start_id = station_start_json["id"]
        station_end_id = station_end_json["id"]
    except Exception as e:
        PYTHON_LOGGER.error("No stations found with this name: start {} to {}: {}".
                            format(station_start, station_end, e))
        return None
    # get all the departures
    travel = requests.get('https://api.sncf.com/v1/coverage/sncf/journeys?from={}&to={}&datetime={}'.
                          format(station_start_id, station_end_id, date),
                          auth=(TOKEN, '')).json()

    PYTHON_LOGGER.info("{} to {}:".format(station_start_json["label"], station_end_json["label"]))
    output_json = {"departures": [], "lat_start": station_start_json["lat"], "lon_start": station_start_json["lon"],
                   "lat_end": station_end_json["lat"], "lon_end": station_end_json["lon"],
                   "station_start_name": station_start_json["label"],
                   "station_end_name": station_end_json["label"]}
    for journey in travel['journeys']:
        output_json["departures"].append(api_date_to_python_date(journey['departure_date_time']).strftime("%H:%M:%S"))
        PYTHON_LOGGER.info("Departure time {}".format(api_date_to_python_date(journey['departure_date_time'])))
    return output_json


if __name__ == "__main__":
    get_all_station()
