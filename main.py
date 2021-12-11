import requests
from discord.ext import commands, tasks
import discord
from selenium import webdriver
import pandas as pd
import environ
import os
import time
import datetime
import pytz
import json
import sqlite3
from lookups import lookup_player, lookup_team, lookup_player_group, lookup_event_clock, lookup_price_changes, get_team_dict, lookup_event_score, lookup_team_fixtures
from formats import format_identifier
import numpy
import math

env = environ.Env()
environ.Env.read_env()

# tweet_id = ''
gameweek = 0


TOKEN = env("DISCORD_TOKEN")
# BEARER = env("TWITTER_BEARER")
print(env("COMMAND_PREFIX"))

activity = discord.Game(name="{}sync to setup".format(env("COMMAND_PREFIX")))
bot = commands.Bot(command_prefix=env("COMMAND_PREFIX"), activity=activity)


try:
    import secrets
    from secrets import secret_price_prediction
    bot.load_extension('secrets')
    extra = True
except Exception as e:
    print(e)
    extra = False


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected!')


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)


@bot.command(name='test', help='IGNORE THIS COMMAND', hidden=True)
async def test(ctx):
    gameweek1 = 2
    response = requests.get('https://fantasy.premierleague.com/api/event/{}/live/'.format(gameweek1))
    players = []
    for player in response.json()['elements']:
        player['stats'] = json.dumps(player['stats'])
        player['explain'] = json.dumps(player['explain'])
        players.append(player)
    players_df = pd.DataFrame(players)
    con = sqlite3.connect("fplbot.db")
    players_df.to_sql("live", con, if_exists='replace', index=False)
    con.close()


@bot.command(name='db', help='IGNORE THIS COMMAND', hidden=True)
async def db(ctx):
    print("scanning123")
    start_time = time.time()
    gameweek_response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    for event in gameweek_response.json()['events']:
        if event['is_current']:
            global gameweek
            print(gameweek)
            if gameweek != event['id']:
                gameweek = event['id']
                response = requests.get('https://fantasy.premierleague.com/api/event/{}/live/'.format(gameweek))
                players = []
                for player in response.json()['elements']:
                    player['stats'] = json.dumps(player['stats'])
                    player['explain'] = json.dumps(player['explain'])
                    players.append(player)
                players_df = pd.DataFrame(players)
                con = sqlite3.connect("fplbot.db")
                players_df.to_sql("live", con, if_exists='replace', index=False)
                con.close()
            else:
                con = sqlite3.connect("fplbot.db")
                fixture_data = pd.read_sql_query("SELECT * FROM fixtures WHERE event=?", con, index_col='id', params=[gameweek])
                players_data = pd.read_sql_query("SELECT * FROM live", con, index_col='id')
                con.close()
                response = requests.get('https://fantasy.premierleague.com/api/event/{}/live/'.format(gameweek))
                players = []
                teams = get_team_dict()
                for player_new in response.json()['elements']:
                    fixture = fixture_data.loc[player_new['explain'][0]['fixture']]
                    player_old = json.loads(players_data.loc[player_new['id']].explain)
                    if len(player_new['explain'][0]['stats']) == 1:
                        pass
                    else:
                        for item in player_new['explain'][0]['stats'][1:]:
                            if item['identifier'] in ['goals_conceded', 'clean_sheets']:
                                continue
                            if any(p['identifier'] == item['identifier'] and p['value'] == item['value'] for p in player_old[0]['stats']):
                                continue
                            else:
                                player = lookup_player(player_new['id'], ['web_name', 'team'])
                                image = "https://resources.premierleague.com/premierleague/badges/50/t{}.png".format(teams[player['team']]['code'])
                                score = lookup_event_score(fixture['pulse_id'])
                                event_clock = lookup_event_clock(fixture['pulse_id'])
                                player_team = "{} ({})\n{}".format(player['web_name'], teams[player['team']]['short_name'], event_clock)
                                event_info = "{} {} {} - {} {} {}".format(discord.utils.get(ctx.guild.emojis, name='t' + str(teams[fixture['team_h']]['code'])), teams[fixture['team_h']]['short_name'], score[0], score[1], teams[fixture['team_a']]['short_name'], discord.utils.get(ctx.guild.emojis, name='t' + str(teams[fixture['team_a']]['code'])))
                                embed = discord.Embed()
                                embed.set_thumbnail(url=image)
                                embed.add_field(name=format_identifier(item['identifier']), value=player_team, inline=False)
                                embed.add_field(name='\u200b', value=event_info)
                                await ctx.send(embed=embed)
                    player_new['stats'] = json.dumps(player_new['stats'])
                    player_new['explain'] = json.dumps(player_new['explain'])
                    players.append(player_new)
                players_df = pd.DataFrame(players)
                con = sqlite3.connect("fplbot.db")
                players_df.to_sql("live", con, if_exists='replace', index=False)
                con.close()
    print(time.time() - start_time)


@bot.command(name='sync', help='Run once to make the bot work')
async def sync(ctx):
    if extra:
        if secrets.scrape.is_running() and spam.is_running() and live_data.is_running() and update_table.is_running():
        # if secrets.scrape.is_running() and spam.is_running() and twitter_bot.is_running() and live_data.is_running() and update_table.is_running():
            await ctx.send("Already synced")
        else:
            for channel in ctx.guild.channels:
                if channel.name == env("CHANNEL"):
                    if not secrets.scrape.is_running():
                        secrets.scrape.start()
                    if not spam.is_running():
                        spam.start(channel)
                    # if not twitter_bot.is_running():
                    #     twitter_bot.start(ctx, channel)
                    if not live_data.is_running():
                        live_data.start(channel, ctx.guild)
                    if not update_table.is_running():
                        update_table.start()
                    if secrets.scrape.is_running() and spam.is_running() and live_data.is_running() and update_table.is_running():
                    # if secrets.scrape.is_running() and spam.is_running() and twitter_bot.is_running() and live_data.is_running() and update_table.is_running():
                        await ctx.send("Sync successful")
        if not secrets.scrape.is_running() or not spam.is_running() or not live_data.is_running() or not update_table.is_running():
        # if not secrets.scrape.is_running() or not spam.is_running() or not twitter_bot.is_running() or not live_data.is_running() or not update_table.is_running():
            await ctx.send("Error with sync, make sure there is a text channel called fpl-updates")
    else:
        if spam.is_running() and live_data.is_running() and update_table.is_running():
        # if spam.is_running() and twitter_bot.is_running() and live_data.is_running() and update_table.is_running():
            await ctx.send("Already synced")
        else:
            for channel in ctx.guild.channels:
                if channel.name == env("CHANNEL"):
                    if not spam.is_running():
                        spam.start(channel)
                    # if not twitter_bot.is_running():
                    #     twitter_bot.start(ctx, channel)
                    if not live_data.is_running():
                        live_data.start(channel, ctx.guild)
                    if not update_table.is_running():
                        update_table.start()
                    if spam.is_running() and live_data.is_running() and update_table.is_running():
                    # if spam.is_running() and twitter_bot.is_running() and live_data.is_running() and update_table.is_running():
                        await ctx.send("Sync successful")
        if not spam.is_running() or not live_data.is_running() or not update_table.is_running():
        # if not spam.is_running() or not twitter_bot.is_running() or not live_data.is_running() or not update_table.is_running():
            await ctx.send("Error with sync, make sure there is a text channel called fpl-updates")


@tasks.loop(seconds=60 * 5)
async def update_table():
    fixture_data_old = []
    fixture_response = requests.get('https://fantasy.premierleague.com/api/fixtures/')
    for fixture in fixture_response.json():
        fixture['stats'] = json.dumps(fixture['stats'])
        fixture_data_old.append(fixture)
    fixture_data_old_df = pd.DataFrame(fixture_data_old)
    con = sqlite3.connect("fplbot.db")
    fixture_data_old_df.to_sql("fixtures", con, if_exists="replace")
    fixture_data = pd.read_sql_query("SELECT * FROM fixtures WHERE finished=1", con)
    con.close()
    teams = dict([(x, []) for x in range(1, 21)])
    fixtures = fixture_data.values.tolist()
    for fixture in fixtures:
        away_team = [fixture[10]]
        home_team = [fixture[12]]
        if fixture[11] > fixture[13]:
            teams[away_team[0]].append(numpy.array([1, 1, 0, 0, fixture[11], fixture[13], fixture[11] - fixture[13], 3]).astype(int))
            teams[home_team[0]].append(numpy.array([1, 0, 0, 1, fixture[13], fixture[11], fixture[13] - fixture[11], 0]).astype(int))
        elif fixture[11] < fixture[13]:
            teams[away_team[0]].append(numpy.array([1, 0, 0, 1, fixture[11], fixture[13], fixture[11] - fixture[13], 0]).astype(int))
            teams[home_team[0]].append(numpy.array([1, 1, 0, 0, fixture[13], fixture[11], fixture[13] - fixture[11], 3]).astype(int))
        else:
            teams[away_team[0]].append(numpy.array([1, 0, 1, 0, fixture[11], fixture[13], fixture[11] - fixture[13], 1]).astype(int))
            teams[home_team[0]].append(numpy.array([1, 0, 1, 0, fixture[11], fixture[13], fixture[11] - fixture[13], 1]).astype(int))
    for team in teams:
        teams[team] = numpy.sum(teams[team], axis=0)
    teams_df_old = pd.DataFrame.from_dict(teams, orient='index', columns=['played', 'w', 'd', 'l', 'gf', 'ga', 'gd', 'points'])
    teams_df = teams_df_old.sort_values(by=['points', 'gd', 'gf'], ascending=False)
    con = sqlite3.connect("fplbot.db")
    teams_df.to_sql("standings", con, if_exists="replace")
    con.close()
    print("League table updated")


@tasks.loop(seconds=60)
async def spam(channel):
    change_data = []
    player_data = []
    spamspam = []
    change_data_new = []
    response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    for player in response.json()['elements']:
        change_data.append([player['web_name'], player['now_cost'], player['cost_change_event'], player['first_name']])
        player_data.append(player)
        if player['cost_change_event'] != 0:
            change_data_new.append(player)
    player_data_df = pd.DataFrame(player_data)
    con = sqlite3.connect("fplbot.db")
    player_data_df.to_sql("players", con, if_exists="replace")
    con.close()
    if change_data_new:
        try:
            con = sqlite3.connect("fplbot.db")
            change_data_old_temp = pd.read_sql_query("SELECT * FROM changes", con, index_col='index')
            change_data_old = change_data_old_temp.values.tolist()
            con.close()
        except Exception as e:
            change_data_old = ['placeholder']
            print("No change data in db")
            print(e)
        change_data_new_df = pd.DataFrame(change_data_new)
        con = sqlite3.connect("fplbot.db")
        change_data_new_df.to_sql("changes", con, if_exists="replace")
        con.close()
        diff_change_data = []
        offset = 0
        for index, player in enumerate(change_data_new_df.values.tolist()):
            try:
                if player[2] == change_data_old[index - offset][2] and player[3] == change_data_old[index - offset][3]:
                    continue
                else:
                    if player[3] == 1 or player[3] == -1:
                        offset += 1
                    diff_change_data.append(player)
            except IndexError:
                diff_change_data.append(player)
        print("Missing players are:\n{}".format(diff_change_data))
        if diff_change_data:
            up_change = "```\n"
            down_change = "```\n"
            for player in diff_change_data:
                if player[3] > 0:
                    up_change += "{} - £{}m\n".format(player[35], player[18] / 10)
                elif player[3] < 0:
                    down_change += "{} - £{}m\n".format(player[35], player[18] / 10)
            if up_change == "```\n" and down_change == "```\n":
                pass
            else:
                if up_change == "```\n":
                    up_change += "None\n```"
                else:
                    up_change += "```"
                if down_change == "```\n":
                    down_change += "None\n```"
                else:
                    down_change += "```"
                embed = discord.Embed()
                embed.add_field(name='Price Rises', value=up_change)
                embed.add_field(name='Price Falls', value=down_change)
                await channel.send(embed=embed)
    else:
        for week in response.json()['events']:
            if week['is_previous']:
                try:
                    con = sqlite3.connect("fplbot.db")
                    change_data_old_temp = pd.read_sql_query("SELECT * FROM changes", con)
                    gw_name = "changesgw{:02d}".format(week['id'])
                    change_data_old_temp.to_sql(gw_name, con, if_exists="append")
                    cur = con.cursor()
                    cur.execute("DELETE FROM changes")
                    con.commit()
                    con.close()
                except Exception as e:
                    pass


@tasks.loop(seconds=10)
async def live_data(channel, guild):
    print("scanning123")
    start_time = time.time()
    gameweek_response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    for event in gameweek_response.json()['events']:
        if event['is_current']:
            global gameweek
            print(gameweek)
            if gameweek != event['id']:
                gameweek = event['id']
                response = requests.get('https://fantasy.premierleague.com/api/event/{}/live/'.format(gameweek))
                players = []
                for player in response.json()['elements']:
                    player['stats'] = json.dumps(player['stats'])
                    player['explain'] = json.dumps(player['explain'])
                    players.append(player)
                players_df = pd.DataFrame(players)
                con = sqlite3.connect("fplbot.db")
                players_df.to_sql("live", con, if_exists='replace', index=False)
                con.close()
            else:
                con = sqlite3.connect("fplbot.db")
                fixture_data = pd.read_sql_query("SELECT * FROM fixtures WHERE event=?", con, index_col='id', params=[gameweek])
                players_data = pd.read_sql_query("SELECT * FROM live", con, index_col='id')
                con.close()
                response = requests.get('https://fantasy.premierleague.com/api/event/{}/live/'.format(gameweek))
                players = []
                teams = get_team_dict()
                for player_new in response.json()['elements']:
                    try:
                        fixture = fixture_data.loc[player_new['explain'][0]['fixture']]
                    except IndexError as e:
                        # print("IndexError: {}".format(e))
                        continue
                    try:
                        player_old = json.loads(players_data.loc[player_new['id']].explain)
                    except KeyError as e:
                        # print("Key Error: {}".format(e))
                        continue
                    if len(player_new['explain'][0]['stats']) == 1:
                        pass
                    else:
                        for item in player_new['explain'][0]['stats'][1:]:
                            if item['identifier'] in ['goals_conceded', 'clean_sheets']:
                                continue
                            if any(p['identifier'] == item['identifier'] and p['value'] == item['value'] for p in player_old[0]['stats']):
                                continue
                            else:
                                player = lookup_player(player_new['id'], ['web_name', 'team'])
                                image = "https://resources.premierleague.com/premierleague/badges/50/t{}.png".format(teams[player['team']]['code'])
                                score = lookup_event_score(fixture['pulse_id'])
                                event_clock = lookup_event_clock(fixture['pulse_id'])
                                player_team = "{} ({})\n{}".format(player['web_name'], teams[player['team']]['short_name'], event_clock)
                                event_info = "{} {} {} - {} {} {}".format(discord.utils.get(guild.emojis, name='t' + str(teams[fixture['team_h']]['code'])), teams[fixture['team_h']]['short_name'], score[0], score[1], teams[fixture['team_a']]['short_name'], discord.utils.get(guild.emojis, name='t' + str(teams[fixture['team_a']]['code'])))
                                embed = discord.Embed()
                                embed.set_thumbnail(url=image)
                                embed.add_field(name=format_identifier(item['identifier']), value=player_team, inline=False)
                                embed.add_field(name='\u200b', value=event_info)
                                await channel.send(embed=embed)

                    player_new['stats'] = json.dumps(player_new['stats'])
                    player_new['explain'] = json.dumps(player_new['explain'])
                    players.append(player_new)
                players_df = pd.DataFrame(players)
                con = sqlite3.connect("fplbot.db")
                players_df.to_sql("live", con, if_exists='replace', index=False)
                con.close()
    print(time.time() - start_time)

############################################
# OLD LIVE DATA SCANNING FIXTURES ENDPOINT #
############################################


# @tasks.loop(seconds=10)
# async def live_data(channel, guild):
#     print("scanning")
#     response = requests.get('https://fantasy.premierleague.com/api/fixtures/')
#     con = sqlite3.connect("fplbot.db")
#     fixture_data = pd.read_sql_query("SELECT * FROM fixtures", con)
#     con.close()
#     fixture_data_new = []
#     for index1, game in enumerate(response.json()):
#         change_data = []
#         new_change_data = []
#         if not game['started']:
#             game['stats'] = json.dumps(game['stats'])
#             fixture_data_new.append(game)
#             continue
#         temp = fixture_data.iloc[index1]
#         game_data = json.loads(temp['stats'])
#         if game['stats'] != game_data:
#             for index2, stat in enumerate(game['stats']):
#                 try:
#                     if stat != game_data[index2]:
#                         if stat['a']:
#                             for item in stat['a']:
#                                 if game_data[index2]['a']:
#                                     if item not in game_data[index2]['a']:
#                                         new_change_data.append(['a', stat['identifier'], item])
#                                 else:
#                                     new_change_data.append(['a', stat['identifier'], item])
#                         if stat['h']:
#                             for item in stat['h']:
#                                 if game_data[index2]['h']:
#                                     if item not in game_data[index2]['h']:
#                                         new_change_data.append(['h', stat['identifier'], item])
#                                 else:
#                                     new_change_data.append(['h', stat['identifier'], item])
#                         change_data.append([stat['identifier'], stat['a'], stat['h'], index2])
#                 except IndexError:
#                     change_data.append([stat['identifier'], stat['a'], stat['h'], index2])
#                     if stat['a']:
#                         for item in stat['a']:
#                             new_change_data.append(['a', stat['identifier'], item])
#                     if stat['h']:
#                         for item in stat['h']:
#                             new_change_data.append(['h', stat['identifier'], item])
#             if new_change_data:
#                 on = sqlite3.connect("fplbot.db")
#                 away = lookup_team(game['team_a'], ['name', 'short_name', 'code'])
#                 away_players = lookup_player_group(game['team_a'], ['web_name', 'event_points'])
#                 home = lookup_team(game['team_h'], ['name', 'short_name', 'code'])
#                 home_players = lookup_player_group(game['team_h'], ['web_name', 'event_points'])
#                 con.close()
#                 # embed = discord.Embed(description='event')
#                 for value in new_change_data:
#                     if value[1] != 'bps':
#                         embed = discord.Embed()
#                         event_clock = lookup_event_clock(game['pulse_id'])
#                         if value[0] == 'a':
#                             image = "https://resources.premierleague.com/premierleague/badges/50/t{}.png".format(away['code'])
#                             print("{} {}: {} - {} for player {}".format(value[0], away['name'], value[1], value[2]['value'], away_players[value[2]['element']]['web_name']))
#                             if value[1] == 'bonus':
#                                 player_team = "{} - {} ({})".format(value[2]['value'], away_players[value[2]['element']]['web_name'], away['short_name'])
#                             else:
#                                 player_team = "{} ({})\n{}".format(away_players[value[2]['element']]['web_name'], away['short_name'], event_clock)
#                         elif value[0] == 'h':
#                             image = "https://resources.premierleague.com/premierleague/badges/50/t{}.png".format(home['code'])
#                             print("{} {}: {} - {} for player {}".format(value[0], home['name'], value[1], value[2]['value'], home_players[value[2]['element']]['web_name']))
#                             if value[1] == 'bonus':
#                                 player_team = "{} - {} ({})".format(value[2]['value'], home_players[value[2]['element']]['web_name'], home['short_name'])
#                             else:
#                                 player_team = "{} ({})\n{}".format(home_players[value[2]['element']]['web_name'], home['short_name'], event_clock)
#                         event_info = "{} {} {} - {} {} {}".format(discord.utils.get(guild.emojis, name='t' + str(home['code'])), home['short_name'], game['team_h_score'], game['team_a_score'], away['short_name'], discord.utils.get(guild.emojis, name='t' + str(away['code'])))
#                         embed.set_thumbnail(url=image)
#                         embed.add_field(name=format_identifier(value[1]), value=player_team, inline=False)
#                         embed.add_field(name='\u200b', value=event_info)
#                         await channel.send(embed=embed)
#                     else:
#                         print(value)
#             game['stats'] = json.dumps(game['stats'])
#             fixture_data_new.append(game)
#         else:
#             game['stats'] = json.dumps(game['stats'])
#             fixture_data_new.append(game)
#     fixture_data_df = pd.DataFrame(fixture_data_new)
#     con = sqlite3.connect("fplbot.db")
#     fixture_data_df.to_sql("fixtures", con, if_exists="replace")
#     con.close()

############################################
# OLD LIVE DATA SCANNING FIXTURES ENDPOINT #
############################################


# @tasks.loop(seconds=10)
# async def twitter_bot(ctx, channel):
#     global tweet_id
#     tweet_data = []
#     headers = {
#         'Authorization': 'Bearer ' + BEARER
#     }
#     if tweet_id:
#         url = 'https://api.twitter.com/2/users/761568335138058240/tweets?max_results=5&since_id=' + tweet_id
#     else:
#         url = 'https://api.twitter.com/2/users/761568335138058240/tweets?max_results=5'
#     try:
#         response = requests.get(url, headers=headers)
#         print("twitter working")
#         print(response)
#         if response.json()['meta']['result_count'] != 0:
#             tweet_id = response.json()['data'][0]['id']
#             for tweet in response.json()['data']:
#                 if 'Goal' in tweet['text'] and 'Assist' in tweet['text']:
#                     embed = discord.Embed(description=tweet['text'])
#                     await channel.send(embed=embed)
#     except Exception as e:
#         await ctx.send("Error connecting to twitter API: {}".format(e))


@bot.command(name='changes', help='Show all price changes from the current gameweek')
async def hwang(ctx):
    con = sqlite3.connect("fplbot.db")
    changes = pd.read_sql_query("SELECT * FROM changes", con)
    con.close()
    up_change = '```\n'
    down_change = '```\n'
    for player in changes.values.tolist():
        # current gameweeks code
        # print(player[4], player[36])
        if player[4] > 0:
            up_change += '{} {}\n'.format(player[4], player[36])
        elif player[4] < 0:
            down_change += '{} {}\n'.format(player[4], player[36])
        else:
            print("this should never print ever")
        # old gameweeks code
        # print(player[5], player[37])
        # if player[5] > 0:
        #     up_change += '{} {}\n'.format(player[5], player[37])
        # elif player[5] < 0:
        #     down_change += '{} {}\n'.format(player[5], player[37])
        # else:
        #     print("this should never print ever")
    up_change += '```'
    down_change += '```'
    # embed = discord.Embed()
    # embed.add_field(name='Price Rises', value=up_change)
    # embed.add_field(name='Price Falls', value=down_change)
    embed = discord.Embed(title='Price Rises', description=up_change)
    await ctx.send(embed=embed)
    embed = discord.Embed(title='Price Falls', description=down_change)
    await ctx.send(embed=embed)


@bot.command(name='table', help='Show the current league standings')
async def table(ctx):
    try:
        con = sqlite3.connect("fplbot.db")
        standings = pd.read_sql_query("SELECT * FROM standings", con)
        con.close()
        result = '```\n|Pos|Clb|Ply| W | D | L |GF |GA |GD |Pts|\n|---+---+---+---+---+---+---+---+---+---|\n'
        for index, team in enumerate(standings.values.tolist(), 1):
            team[0] = lookup_team(team[0], ['short_name'])
            team[7] = '{0:+d}'.format(team[7])
            team.insert(0, index)
            team_result = '|'
            for item in team:
                team_result = team_result + ' ' * math.floor((-len(str(item)) * 0.5) + 1.5) + str(item) + ' ' * math.ceil((-len(str(item)) * 0.5) + 1.5) + '|'
            result = result + team_result + '\n'
        result = result + '```'
        embed = discord.Embed(title='Premier League Table', description=result)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("No data found")
        print(e)


@bot.command(name='search', aliases=['s'], help='Lookup a specific player')
async def search(ctx, *, player_search):
    found = 0
    con = sqlite3.connect("fplbot.db")
    player_data_temp = pd.read_sql_query("SELECT * FROM players", con)
    con.close()
    player_data = player_data_temp.values.tolist()
    for player in player_data:
        if player_search.lower() == player[36].lower():
            found += 1
            if player[26] == 'a':
                status = "Availible"
            elif player[26] == 'u':
                status = "Unavailible"
            elif player[26] == 'd':
                status = "Doubtful"
            elif player[26] == 'i':
                status = "Injured"
            elif player[26] == 'n':
                status = "Not in Squad"
            elif player[26] == 's':
                status = "Suspended"
            else:
                status = "Unknown"
            if player[17] != player[17]:
                news = "None"
            else:
                news = player[17]
            if player[1] != player[1]:
                chance = 100
            else:
                chance = int(player[1])
            player_result = "```\nStatus: {} ({}% chance of playing)\nNews: {}\nPoints-GW: {}\nPoints-Total: {}```".format(status, chance, news, player[12], player[29])
            image = 'https://resources.premierleague.com/premierleague/photos/players/110x140/p' + (player[20].split('.'))[0] + '.png\n'
            title = "{} {} - £{}m".format(player[13], player[22], player[19] / 10)
            if extra:
                price_changes_name = 'Price Changes ({})'.format(secret_price_prediction(player[36]))
            else:
                price_changes_name = 'Price Changes'
            player_fixtures = lookup_team_fixtures(player[27])
            fixtures = "```\n"
            for x in range(0, 5):
                # print(player_fixtures[x])
                fixtures += "GW-{:02d}: {} ({})\n".format(int(player_fixtures[x][0]), player_fixtures[x][1], player_fixtures[x][2])
            fixtures += "```"
            changes = "```\n" + lookup_price_changes(player[15], ctx.guild) + "\n```"
            embed = discord.Embed(title=title)
            embed.set_thumbnail(url=image)
            embed.add_field(name='Info', value=player_result)
            embed.add_field(name='Upcoming Fixtures', value=fixtures, inline=False)
            embed.add_field(name=price_changes_name, value=changes, inline=False)
            await ctx.send(embed=embed)
    if found == 0:
        await ctx.send("Couldn't find that player.")


@bot.command(name='team', help='Show the remaining fixtures for a team')
async def team(ctx, *, team_search):
    found = False
    teams = {}
    fixtures = "```\n"
    con = sqlite3.connect("fplbot.db")
    team_data_temp = pd.read_sql_query("SELECT * FROM teams", con)
    fixture_data_temp = pd.read_sql_query("SELECT * FROM fixtures", con)
    con.close()
    team_data = team_data_temp.values.tolist()
    fixture_data = fixture_data_temp.values.tolist()
    for team in team_data:
        teams[team[4]] = team[6]
        if team_search.lower() == team[6].lower():
            team_search_id = team[4]
            found = True
            image = "https://resources.premierleague.com/premierleague/badges/50/t{}.png".format(team[1])
    if found:
        for fixture in fixture_data:
            if not pd.isna(fixture[2]):
                if not fixture[3]:
                    if team_search_id == fixture[10]:
                        fixtures += "GW-{:02d}: {} (A)\n".format(int(fixture[2]), teams[fixture[12]] + ' ' * (14 - len(teams[fixture[12]])))
                    elif team_search_id == fixture[12]:
                        fixtures += "GW-{:02d}: {} (H)\n".format(int(fixture[2]), teams[fixture[10]] + ' ' * (14 - len(teams[fixture[10]])))
                else:
                    if team_search_id == fixture[10] or team_search_id == fixture[12]:
                        if fixture[11] > fixture[13]:
                            win = fixture[10]
                        elif fixture[11] < fixture[13]:
                            win = fixture[12]
                        else:
                            win = 0
                        if win == 0:
                            win_loss_emoji = '\U000026AA'
                        elif team_search_id == win:
                            win_loss_emoji = '\U0001F7E2'
                        else:
                            win_loss_emoji = '\U0001F534'
                        fixtures += "GW-{:02d}: {} {} - {} {} {}\n".format(int(fixture[2]), ' ' * (14 - len(teams[fixture[12]])) + teams[fixture[12]], int(fixture[13]), int(fixture[11]), teams[fixture[10]] + ' ' * (14 - len(teams[fixture[10]])), win_loss_emoji)
        fixtures += "```"
        embed = discord.Embed(title='{} Fixtures'.format(teams[team_search_id]), description=fixtures)
        embed.set_thumbnail(url=image)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Team not found")


@bot.command(name='dump', help='IGNORE THIS COMMAND', hidden=True)
async def dump_test(ctx):
    team_data = []
    fixture_data = []
    response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    fixture_response = requests.get('https://fantasy.premierleague.com/api/fixtures/')
    for team in response.json()['teams']:
        team_data.append(team)
    for fixture in fixture_response.json():
        fixture['stats'] = json.dumps(fixture['stats'])
        # if fixture['code'] == 2210282:
        #     # fixture['stats'] = '[]'
        #     # fixture['stats'] = json.dumps(fixture['stats'][0])
        #     fixture['stats'] = '[{"identifier": "goals_scored", "a": [], "h": [{"value": 1, "element": 42}]}, {"identifier": "assists", "a": [], "h": [{"value": 1, "element": 38}]}]'
        fixture_data.append(fixture)
    con = sqlite3.connect("fplbot.db")
    team_data_df = pd.DataFrame(team_data)
    team_data_df.to_sql("teams", con, if_exists="replace")
    fixture_data_df_temp = pd.DataFrame(fixture_data)
    fixture_data_df_temp.to_sql("fixtures", con, if_exists="replace")
    con.close()
    await ctx.send('all team and fixture data dumped into sqlite db')


bot.run(TOKEN)
