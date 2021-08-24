import sqlite3
import pandas as pd
import json


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
    result = {}
    for column_name in columns:
        result[column_name] = player_data[column_name][0]
    return result


def lookup_team(team_id, columns):
    con = sqlite3.connect("fplbot.db")
    team_data = pd.read_sql_query("SELECT * FROM teams WHERE id=?", con, params=[team_id])
    con.close()
    result = {}
    for column_name in columns:
        result[column_name] = team_data[column_name][0]
    return result
