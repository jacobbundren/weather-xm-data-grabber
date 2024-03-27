import requests
import datetime
import json
from pathlib import Path

headers = {}
station_list = []
user_id = ''
historical_data = []
auth_error = 'Unsuccessful authentication'
user_info_error = 'Failed to retrieve user information'
station_data_error = 'Failed to retrieve station data'
historical_data_error = 'Failed to retrieve historical data'
file_write_error = 'Error creating historical data files'


def authenticate(username, password):
    """
    Authenticates user with WeatherXM REST API
    :param username: WeatherXM account username
    :param password: WeatherXM account password
    :return: auth tokens for authenticated user
    """
    json_body = {
        'password': password,
        'username': username
    }
    resp = requests.post(
        'https://api.weatherxm.com/api/v1/auth/login',
        json=json_body
    )
    error_check(resp, error_message=auth_error)
    return resp.json()


def error_check(response, error_message):
    """
    Checks basic 200 error code for network calls
    :param response: response returned from request.method network call
    :param error_message: error message to display in case of error
    :return: none
    """
    if response.status_code != 200:
        exit(error_message)


def get_user_id():
    """
    Gets user ID from WeatherXM REST API
    :return: WeatherXM User ID
    """
    resp = requests.get('https://api.weatherxm.com/api/v1/me', headers=headers)
    error_check(resp, error_message=user_info_error)
    json_resp = resp.json()
    if 'id' not in json_resp:
        exit(user_info_error)
    return json_resp['id']


def get_user_stations():
    """
    Get weather stations associated to authenticated user's WeatherXM account
    :return: list of user's WXM stations
    """
    stations = []
    resp = requests.get('https://api.weatherxm.com/api/v1/me/devices', headers=headers)
    error_check(resp, error_message=station_data_error)
    json_resp = resp.json()
    if not json_resp:
        exit(station_data_error)
    for s in json_resp:
        stations.append(
            {
                'id': s['id'],
                'name': s['name'],
                'location': s['location']
            }
        )
    return stations


def get_historical_data(s):
    """
    Gets previous 7 days of data for the WXM station passed in and sets it to historical_data property on object
    :param s: WXM weather station {id, name, location} // TODO Needs to be stored OO
    :return: none
    """
    today = datetime.date.today()
    date_end = today - datetime.timedelta(days=1)
    date_start = today - datetime.timedelta(days=8)
    resp = requests.get(
        f'https://api.weatherxm.com/api/v1/me/devices/{s["id"]}/history?fromDate={date_start}&toDate={date_end}',
        headers=headers
    )
    error_check(resp, error_message=historical_data_error)
    station.update({
        'historical_data': resp.json()
    })


def write_station_data():
    """
    Writes station data to file using station ID as <id>.json
    :return:
    """
    try:
        Path('data/').mkdir(exist_ok=True)
        for s in station_list:
            with open(f'data/{s["id"]}.json', 'w', encoding='utf-8') as f:
                json.dump(s, f, ensure_ascii=False, indent=4)
    except Exception as ex:
        print(ex)
        exit(file_write_error)


if __name__ == '__main__':
    # Authenticate
    username_input = input('Enter WeatherXM username: ')
    password_input = input('Enter WeatherXM password: ')
    auth_resp = authenticate(username=username_input, password=password_input)
    token = f'Bearer {auth_resp["token"]}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token
    }

    # Get user info
    user_id = get_user_id()

    # Get station list for user
    station_list = get_user_stations()
    for station in station_list:
        get_historical_data(s=station)

    # Write to file
    write_station_data()
