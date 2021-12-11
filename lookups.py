import sqlite3
import pandas as pd
import json
import requests


def lookup_player_group(team_id, columns):
    con = sqlite3.connect("fplbot.db")
    player_data_temp = pd.read_sql_query("SELECT * FROM players WHERE team=?", con, params=[team_id])
    con.close()
    player_data = player_data_temp.to_dict(orient='index')
    # print(player_data)
    result = {}
    for player in player_data:
        result[player_data[player]['id']] = {}
        for column_name in columns:
            result[player_data[player]['id']][column_name] = player_data[player][column_name]
    return result


def lookup_player(player_id, columns):
    con = sqlite3.connect("fplbot.db")
    player_data = pd.read_sql_query("SELECT * FROM players WHERE id=?", con, params=[player_id])
    con.close()
    if len(columns) == 1:
        return player_data[columns[0]][0]
    else:
        result = {}
        for column_name in columns:
            result[column_name] = player_data[column_name][0]
        return result


def lookup_team(team_id, columns):
    con = sqlite3.connect("fplbot.db")
    team_data = pd.read_sql_query("SELECT * FROM teams WHERE id=?", con, params=[team_id])
    con.close()
    if len(columns) == 1:
        return team_data[columns[0]][0]
    else:
        result = {}
        for column_name in columns:
            result[column_name] = team_data[column_name][0]
        return result


def lookup_event_clock(fixture_id):
    # url = 'https://footballapi.pulselive.com/football/fixtures/66353/textstream/EN?pageSize=100&sort=desc'
    url = 'https://footballapi.pulselive.com/football/fixtures/{}'.format(fixture_id)
    headers = {
        'Origin': 'https://www.premierleague.com'
    }
    response = requests.get(url, headers=headers)
    return response.json()['clock']['label']


def lookup_event_score(fixture_id):
    url = 'https://footballapi.pulselive.com/football/fixtures/{}'.format(fixture_id)
    headers = {
        'Origin': 'https://www.premierleague.com'
    }
    response = requests.get(url, headers=headers)
    return [response.json()['teams'][0]['score'], response.json()['teams'][1]['score']]


def lookup_price_changes(player_id, guild):
    con = sqlite3.connect("fplbot.db")
    tables_old = pd.read_sql_query("SELECT tbl_name FROM sqlite_master WHERE type='table' AND name LIKE 'changes%' ORDER BY tbl_name", con)
    result = []
    tables = tables_old.values.tolist()
    # print(tables)
    tables.append(tables.pop(tables.index(['changes'])))
    # print(tables)
    for table in tables:
        sql = "SELECT cost_change_event FROM {} WHERE id=?".format(table[0])
        temp = pd.read_sql_query(sql, con, params=[player_id])
        if not table[0][7:]:
            table[0] = 'changesgw' + str(format(len(tables_old.values), '02d'))
        if not temp.empty:
            result.append([table[0][7:], temp['cost_change_event'][0]])
        else:
            result.append([table[0][7:], 0])
    final_result = '|'
    for item in result:
    # for item in reversed(result):
        final_result = final_result + ' {} {} |'.format(item[0].upper(), item[1])
    con.close()
    return final_result


def get_team_dict():
    con = sqlite3.connect("fplbot.db")
    team_data_old = pd.read_sql_query("SELECT * FROM teams", con)
    team_data = team_data_old.to_dict(orient='index')
    con.close()
    result = {}
    for team in team_data:
        result[team_data[team]['id']] = {'name': team_data[team]['name'], 'short_name': team_data[team]['short_name'], 'code': team_data[team]['code']}
    return result


def lookup_team_fixtures(team_id):
    fixtures = []
    teams = {}
    con = sqlite3.connect("fplbot.db")
    team_data_temp = pd.read_sql_query("SELECT * FROM teams", con)
    fixture_data_temp = pd.read_sql_query("SELECT * FROM fixtures", con)
    con.close()
    team_data = team_data_temp.values.tolist()
    fixture_data = fixture_data_temp.values.tolist()
    for team in team_data:
        teams[team[4]] = team[6]
    if team_id > 0 and team_id < 21:
        for fixture in fixture_data:
            if not fixture[3]:
                if not pd.isna(fixture[2]):
                    if team_id == fixture[10]:
                        print(fixture)
                        fixtures.append([fixture[2], teams[fixture[12]], 'A'])
                    elif team_id == fixture[12]:
                        print(fixture)
                        fixtures.append([fixture[2], teams[fixture[10]], 'H'])
    return fixtures
