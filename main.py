import requests
# from bs4 import BeautifulSoup
from discord.ext import commands, tasks
import discord
from selenium import webdriver
import pandas as pd
import environ
import os
# import time
import datetime
import pytz
import json
import sqlite3
from lookups import lookup_player, lookup_team, lookup_player_group, lookup_event_clock, lookup_price_changes
from formats import format_identifier

env = environ.Env()
environ.Env.read_env()

# True scrapes the site, False uses the local data.csv
# live = env("DEBUG_OPTION")
# if live:
#     print("True")
# else:
#     print("False")

tweet_id = ''


TOKEN = env("DISCORD_TOKEN")
BEARER = env("TWITTER_BEARER")
print(env("COMMAND_PREFIX"))

activity = discord.Game(name="{}sync to setup".format(env("COMMAND_PREFIX")))
bot = commands.Bot(command_prefix=env("COMMAND_PREFIX"), activity=activity)


try:
    import secrets
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


@bot.command(name='db')
async def db(ctx):
    # con = sqlite3.connect("fplbot.db")
    # # cur = con.cursor()
    # # cur.execute('''CREATE TABLE players (firstname text, secondname text, cost real)''')
    # # cur.execute("INSERT INTO players VALUES ('John','Malovic',9.4)")
    # # con.commit()
    # db_df = pd.read_csv("current.csv")
    # db_df.to_sql("changes", con, if_exists="replace")
    # con.close()
    # print(lookup_player(42, ['web_name', 'second_name', 'now_cost']))
    # print(lookup_player_group(2, ['web_name', 'event_points']))
    # temp = lookup_player('Mendy', ['web_name', 'second_name', 'now_cost'])
    # print(lookup_team(11, ['name', 'short_name']))
    # url = 'https://footballapi.pulselive.com/football/fixtures/66353/textstream/EN?pageSize=100&sort=desc'
    # headers = {
    #     'Origin': 'https://www.premierleague.com',
    # }
    # response = requests.get(url, headers=headers)
    # print(response.json())
    # print(response.json()['events']['pageInfo'])
    # print(response.json()['fixture']['clock'])
    # print(lookup_event_clock(66353))
    # for emoji in ctx.guild.emojis:
    #     print(emoji)
    # print(emoji.id)
    # print(discord.utils.get(ctx.guild.emojis, name='t4'))
    print(lookup_price_changes(413))
    print(lookup_price_changes(95))
    # change_data = []
    # codes = [
    #     47431,
    #     54694,
    #     59966,
    #     98745,
    #     156074,
    #     195735,
    #     223340,
    #     154138,
    #     82263,
    #     124183,
    #     165153,
    #     219847,
    #     212319,
    #     173515,
    #     245419,
    #     157882,
    #     204716,
    #     214285,
    #     74208,
    #     141746,
    #     148225,
    #     172649,
    #     180184,
    #     209243,
    #     78830,
    #     57531,
    #     86934,
    #     172841
    # ]
    # player_data = []
    # response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    # for player in response.json()['elements']:
    #     if player['code'] in codes:
    #         # print(player['cost_change_event'])
    #         if player['cost_change_event'] == 0:
    #             player['cost_change_event'] = player['cost_change_start']
    #             player['cost_change_event_fall'] = player['cost_change_start_fall']
    #         if player['cost_change_start'] == -2 or player['cost_change_start'] == 2:
    #             player['cost_change_start'] = player['cost_change_event']
    #             player['cost_change_start_fall'] = player['cost_change_event_fall']
    #             # player['cost_change_start'] == 0
    #             # player['cost_change_start_fall'] == 0
    #         player_data.append(player)
    # player_data_df = pd.DataFrame(player_data)
    # con = sqlite3.connect("fplbot.db")
    # player_data_df.to_sql("changesgw1", con, if_exists="replace")
    # con.close()
    # players = []
    # for code in codes:
    #     con = sqlite3.connect("fplbot.db")
    #     player = pd.read_sql_query("SELECT * FROM players WHERE code=?", con, params=[code])
    #     players.append(player)
    #     # print(player)
    #     con.close()
    # df = players[0]
    # for player in players:
    #     df = df.append(player)
    # print(df)

    # con = sqlite3.connect("fplbot.db")
    # # player = pd.read_sql_query("SELECT * FROM players WHERE code IN (?)", con, params=[codes])
    # player = pd.read_sql_query("SELECT * FROM players WHERE code IN (47431, 54694, 59966, 98745, 156074, 195735, 223340, 154138, 82263, 124183, 165153, 219847, 212319, 173515, 245419, 157882, 204716, 214285, 74208, 141746, 148225, 172649, 180184, 209243, 78830, 57531, 86934, 172841)", con)
    # for p in player:
    #     print(p)
    # player.to_sql("changesgw1", con, if_exists='replace')
    # con.close()
    # change_data_old_temp = pd.read_sql_query("SELECT * FROM changes", con)
    # gw_name = "changesgw{}".format(week['id'])
    # change_data_old_temp.to_sql(gw_name, con, if_exists="replace")
    # change_data_old = change_data_old_temp.values.tolist()
    # con.close()


@bot.command(name='sync', help='Run once to make the bot work')
async def sync(ctx):
    if extra:
        if secrets.scrape.is_running() and spam.is_running() and twitter_bot.is_running() and live_data.is_running():
            await ctx.send("Already synced")
        else:
            for channel in ctx.guild.channels:
                if channel.name == env("CHANNEL"):
                    if not secrets.scrape.is_running():
                        secrets.scrape.start()
                    if not spam.is_running():
                        spam.start(channel)
                    if not twitter_bot.is_running():
                        twitter_bot.start(ctx, channel)
                    if not live_data.is_running():
                        live_data.start(channel, ctx.guild)
                    if secrets.scrape.is_running() and spam.is_running() and twitter_bot.is_running() and live_data.is_running():
                        await ctx.send("Sync successful")
        if not secrets.scrape.is_running() or not spam.is_running():
            await ctx.send("Error with sync, make sure there is a text channel called fpl-updates")
    else:
        if spam.is_running() and twitter_bot.is_running() and live_data.is_running():
            await ctx.send("Already synced")
        else:
            for channel in ctx.guild.channels:
                if channel.name == env("CHANNEL"):
                    if not spam.is_running():
                        spam.start(channel)
                    if not twitter_bot.is_running():
                        twitter_bot.start(ctx, channel)
                    if not live_data.is_running():
                        live_data.start(channel, ctx.guild)
                    if spam.is_running() and twitter_bot.is_running() and live_data.is_running():
                        await ctx.send("Sync successful")
        if not spam.is_running() or not twitter_bot.is_running() or not live_data.is_running():
            await ctx.send("Error with sync, make sure there is a text channel called fpl-updates")


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
            # new_vals.append(player)
        # elif player['cost_change_event'] < 0:
        #     spamspam.append(player)
            # new_vals.append(player)
    player_data_df = pd.DataFrame(player_data)
    con = sqlite3.connect("fplbot.db")
    player_data_df.to_sql("players", con, if_exists="replace")
    con.close()
    # new_vals = []
    # for i in change_data:
    #     if i[2] > 0:
    #         new_vals.append([i[0], i[1] / 10, '(' + i[3] + ')', i[2]])
    #     elif i[2] < 0:
    #         new_vals.append([i[0], i[1] / 10, '(' + i[3] + ')', i[2]])
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
        # print("############OLD")
        # print(change_data_old)
        # print("############NEW")
        # print(pd.DataFrame(change_data_new).values.tolist())
        # print(change_data_new)
        # try:
        #     temp_csv = pd.read_csv('current.csv')
        #     old_vals = temp_csv.values.tolist()
        # except:
        #     old_vals = ['bloat']
        #     print("No csv data exists, all changes added")
        # if len(old_vals) > len(new_vals):
        #     for week in response.json()['events']:
        #         if week['is_previous']:
        #             temp_csv.to_csv('gameweek{}.csv'.format(week['id']))
        #     old_vals = ['bloat']
        # change_csv = pd.DataFrame(new_vals)
        # change_csv.to_csv('current.csv', index=None)
        change_data_new_df = pd.DataFrame(change_data_new)
        con = sqlite3.connect("fplbot.db")
        change_data_new_df.to_sql("changes", con, if_exists="replace")
        con.close()
        # diff_vals = []
        # offset = 0
        # for i in new_vals:
        #     try:
        #         if i == old_vals[new_vals.index(i) - offset]:
        #             continue
        #         else:
        #             offset += 1
        #             diff_vals.append(i)
        #     except IndexError:
        #         diff_vals.append(i)
        # print("Missing players are:\n{}".format(diff_vals))
        diff_change_data = []
        offset = 0
        # for index, player in enumerate(change_data_new):
        for index, player in enumerate(change_data_new_df.values.tolist()):
            # print(index)
            try:
                # print(player)
                # print(change_data_old[index - offset])
                # if player == change_data_old[change_data_new.index(player) - offset]:
                if player[2] == change_data_old[index - offset][2]:
                    continue
                else:
                    offset += 1
                    diff_change_data.append(player)
            except IndexError:
                diff_change_data.append(player)
        # print("Missing players are:\n{}".format(diff_change_data))
        print("Missing players are:\n{}".format(diff_change_data))
        # up_change = "```\n"
        # down_change = "```\n"
        # for z in diff_vals:
        #     if z[3] > 0:
        #         up_change += "{} - £{}m\n".format(z[0], z[1])
        #     elif z[3] < 0:
        #         down_change += "{} - £{}m\n".format(z[0], z[1])
        # if up_change == "```\n" and down_change == "```\n":
        #     pass
        # else:
        #     if up_change == "```\n":
        #         up_change += "None\n```"
        #     else:
        #         up_change += "```"
        #     if down_change == "```\n":
        #         down_change += "None\n```"
        #     else:
        #         down_change += "```"
        #     embed = discord.Embed()
        #     embed.add_field(name='Price Rises', value=up_change)
        #     embed.add_field(name='Price Falls', value=down_change)
        #     await channel.send(embed=embed)
        if diff_change_data:
            # print(diff_change_data)
            up_change = "```\n"
            down_change = "```\n"
            for player in diff_change_data:
                # print(player)
                # break
                # print(player['cost_change_event'])
                # print(player[0])
                # print(player[1])
                # print(player[2])
                # print(player[3])
                # break
                # if player['cost_change_event'] > 0:
                if player[3] > 0:
                    # up_change += "{} - £{}m\n".format(player['web_name'], player['now_cost'] / 10)
                    up_change += "{} - £{}m\n".format(player[35], player[18] / 10)
                # elif player['cost_change_event'] < 0:
                elif player[3] < 0:
                    # down_change += "{} - £{}m\n".format(player['web_name'], player['now_cost'] / 10)
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
                con = sqlite3.connect("fplbot.db")
                change_data_old_temp = pd.read_sql_query("SELECT * FROM changes", con)
                gw_name = "changesgw{:02d}".format(week['id'])
                change_data_old_temp.to_sql(gw_name, con, if_exists="replace")
                change_data_old = change_data_old_temp.values.tolist()
                con.close()


# @bot.command(name='tweet')
# async def tweet(ctx):
#     twitter_bot.start(ctx)
#     await ctx.send("tweeting")

@tasks.loop(seconds=10)
async def live_data(channel, guild):
# @bot.command(name='live')
# async def live(ctx):
    print("scanning")
    response = requests.get('https://fantasy.premierleague.com/api/fixtures/')
    con = sqlite3.connect("fplbot.db")
    fixture_data = pd.read_sql_query("SELECT * FROM fixtures", con)
    # player_data = pd.read_sql_query("SELECT * FROM players", con)
    # team_data = pd.read_sql_query("SELECT * FROM teams", con)
    con.close()
    # fixture_data = fixture_data_temp.values.tolist()
    # print(fixture_data)
    # print(fixture_data_temp)
    # print(fixture_data_temp.iloc[3])
    # for fixture in fixture_data:
    #     # con = sqlite3.connect("fplbot.db")
    #     print(fixture[0])
    fixture_data_new = []
    for index1, game in enumerate(response.json()):
        change_data = []
        new_change_data = []
        if not game['started']:
            # fixture_data_new.append(fixture_data.iloc[index])
            game['stats'] = json.dumps(game['stats'])
            fixture_data_new.append(game)
            continue
        # print(index)
        # print(game)
        # print(game['stats'])
        # print(json.dumps(game['stats']))
        # temp = fixture_data.iloc[index1]
        temp = fixture_data.iloc[index1]
        game_data = json.loads(temp['stats'])
        # print(game_data)
        # print(temp['stats'])
        # if json.dumps(game['stats']) == temp['stats']:
        #     print(game['code'])
        #     print("bloop")
        if game['stats'] != game_data:
            # print("werk")
            # continue
            for index2, stat in enumerate(game['stats']):
                # print(game_data[index2])
                # print(stat)
                # print(game_data[index])
                try:
                    # print(game_data[index2])
                    if stat != game_data[index2]:
                        if stat['a']:
                            for item in stat['a']:
                                if not game_data[index2]['a']:
                                    if item not in game_data[index2]['a']:
                                        new_change_data.append(['a', stat['identifier'], item])
                                else:
                                    new_change_data.append(['a', stat['identifier'], item])
                        if stat['h']:
                            for item in stat['h']:
                                if not game_data[index2]['h']:
                                    if item not in game_data[index2]['h']:
                                        new_change_data.append(['h', stat['identifier'], item])
                                else:
                                    new_change_data.append(['h', stat['identifier'], item])
                        # print(new_change_data)
                        change_data.append([stat['identifier'], stat['a'], stat['h'], index2])
                except IndexError:
                    change_data.append([stat['identifier'], stat['a'], stat['h'], index2])
                    # new_change_data.append([stat['identifier']])
                    if stat['a']:
                        for item in stat['a']:
                            new_change_data.append(['a', stat['identifier'], item])
                    if stat['h']:
                        for item in stat['h']:
                            new_change_data.append(['h', stat['identifier'], item])
                    # new_change_data.append([stat['identifier'], item])
                # print(new_change_data)
            # print(change_data)
            # print(new_change_data)
            if new_change_data:
                on = sqlite3.connect("fplbot.db")
                away = lookup_team(game['team_a'], ['name', 'short_name', 'code'])
                away_players = lookup_player_group(game['team_a'], ['web_name', 'event_points'])
                home = lookup_team(game['team_h'], ['name', 'short_name', 'code'])
                home_players = lookup_player_group(game['team_h'], ['web_name', 'event_points'])
                con.close()
                embed = discord.Embed()
                for value in new_change_data:
                    if value[1] != 'bps':
                        event_clock = lookup_event_clock(game['pulse_id'])
                        if value[0] == 'a':
                            image = "https://resources.premierleague.com/premierleague/badges/50/t{}.png".format(away['code'])
                            print("{} {}: {} - {} for player {}".format(value[0], away['name'], value[1], value[2]['value'], away_players[value[2]['element']]['web_name']))
                            # embed_desc = "{}\n{} ({})".format(format_identifier(value[1]), away_players[value[2]['element']]['web_name'], away['short_name'])
                            if value[1] == 'bonus':
                                player_team = "{} - {} ({})".format(value[2]['value'], away_players[value[2]['element']]['web_name'], away['short_name'])
                            else:
                                player_team = "{} ({})\n{}".format(away_players[value[2]['element']]['web_name'], away['short_name'], event_clock)
                        elif value[0] == 'h':
                            image = "https://resources.premierleague.com/premierleague/badges/50/t{}.png".format(home['code'])
                            print("{} {}: {} - {} for player {}".format(value[0], home['name'], value[1], value[2]['value'], home_players[value[2]['element']]['web_name']))
                            if value[1] == 'bonus':
                                player_team = "{} - {} ({})".format(value[2]['value'], home_players[value[2]['element']]['web_name'], home['short_name'])
                            else:
                                player_team = "{} ({})\n{}".format(home_players[value[2]['element']]['web_name'], home['short_name'], event_clock)
                            # embed_desc = "{}\n{} ({})".format(format_identifier(value[1]), home_players[value[2]['element']]['web_name'], home['short_name'])    
                        # embed = discord.Embed(description=embed_desc)
                        # embed = discord.Embed()
                        # event_info = ":t{}: {} {} - {} {} :t{}:".format(home['code'], home['short_name'], game['team_h_score'], game['team_a_score'], away['short_name'], away['code'])
                        event_info = "{} {} {} - {} {} {}".format(discord.utils.get(guild.emojis, name='t' + str(home['code'])), home['short_name'], game['team_h_score'], game['team_a_score'], away['short_name'], discord.utils.get(guild.emojis, name='t' + str(away['code'])))
                        embed.set_thumbnail(url=image)
                        embed.add_field(name=format_identifier(value[1]), value=player_team, inline=False)
                        embed.add_field(name='\u200b', value=event_info)
                await channel.send(embed=embed)
            # if change_data:
            #     con = sqlite3.connect("fplbot.db")
            #     away = lookup_team(game['team_a'], ['name', 'short_name'])
            #     away_players = lookup_player_group(game['team_a'], ['web_name', 'event_points'])
            #     home = lookup_team(game['team_h'], ['name', 'short_name'])
            #     home_players = lookup_player_group(game['team_h'], ['web_name', 'event_points'])
            #     con.close()
            #     # await channel.send(change_data)
            #     for category in change_data:
            #         if category[1]:
            #             for item in category[1]:
            #                 print(item)
            #                 # print("A {} - {} for player {}".format(category[0], item['value'], item['element']))
            #                 # print("A {}: {} - {} for player {}".format(away['name'], category[0], item['value'], item['element']))
            #                 print("A {}: {} - {} for player {}".format(away['name'], category[0], item['value'], away_players[item['element']]['web_name']))
            #                 try:
            #                     # for subitem in game_data[0][category[0]]
            #                     # print(game_data)
            #                     # print(category[3])
            #                     temp = category[3]
            #                     # print(game_data)
            #                     # if game_data[0][category[0]]:
            #                     #     print(game_data[0][category[0]])
            #                 except IndexError:
            #                     print("Error Index")
            #                 except KeyError:
            #                     print("Error Key")
            #                 except TypeError:
            #                     print("Type Error")
            #         if category[2]:
            #             for item in category[2]:
            #                 print(item)
            #                 # print("H {} - {} for player {}".format(category[0], item['value'], item['element']))
            #                 # print("H {}: {} - {} for player {}".format(home['name'], category[0], item['value'], item['element']))
            #                 print("H {}: {} - {} for player {}".format(home['name'], category[0], item['value'], home_players[item['element']]['web_name']))
            #                 try:
            #                     # print(game_data)
            #                     if game_data[0][category[0]]:
            #                         print(game_data[0][category[0]])
            #                 except IndexError:
            #                     print("Error Index")
            #                 except KeyError:
            #                     print("Error Key")
            #                 except TypeError:
            #                     print("Type Error")
            #     # for category in change_data:
                #     print(category)
                #     if category[0] == 'goals_scored':
                #         title = category[0]
                #         goals_scored_away = category[1]
                #         goals_scored_home = category[2]
                #         away = goals_scored_away
                #         home = goals_scored_home
                #         desc = goals_scored_away + goals_scored_home
                #     elif category[0] == 'assists':
                #         title = category[0]
                #         assists_away = category[1]
                #         assists_home = category[2]
                #         away = assists_away
                #         home = assists_home
                #         desc = assists_away + assists_home
                #     elif category[0] == 'own_goals':
                #         title = category[0]
                #         own_goals_away = category[1]
                #         own_goals_home = category[2]
                #         away = own_goals_away
                #         home = own_goals_home
                #         desc = own_goals_away + own_goals_home
                #     elif category[0] == 'penalties_saved':
                #         title = category[0]
                #         penalties_saved_away = category[1]
                #         penalties_saved_home = category[2]
                #         away = penalties_saved_away
                #         home = penalties_saved_home
                #         desc = penalties_saved_away + penalties_saved_home
                #     elif category[0] == 'penalties_missed':
                #         title = category[0]
                #         penalties_missed_away = category[1]
                #         penalties_missed_home = category[2]
                #         away = penalties_missed_away
                #         home = penalties_missed_home
                #         desc = penalties_missed_away + penalties_missed_home
                #     elif category[0] == 'yellow_cards':
                #         title = category[0]
                #         yellow_cards_away = category[1]
                #         yellow_cards_home = category[2]
                #         away = yellow_cards_away
                #         home = yellow_cards_home
                #         desc = yellow_cards_away + yellow_cards_home
                #     elif category[0] == 'red_cards':
                #         title = category[0]
                #         red_cards_away = category[1]
                #         red_cards_home = category[2]
                #         away = red_cards_away
                #         home = red_cards_home
                #         desc = red_cards_away + red_cards_home
                #     elif category[0] == 'saves':
                #         title = category[0]
                #         saves_away = category[1]
                #         saves_home = category[2]
                #         away = saves_away
                #         home = saves_home
                #         desc = saves_away + saves_home
                #     elif category[0] == 'bonus':
                #         title = category[0]
                #         bonus_away = category[1]
                #         bonus_home = category[2]
                #         away = bonus_away
                #         home = bonus_home
                #         desc = bonus_away + bonus_home
                #     elif category[0] == 'bps':
                #         title = category[0]
                #         bps_away = category[1]
                #         bps_home = category[2]
                #         away = bps_away
                #         home = bps_home
                #         desc = bps_away + bps_home
                #     embed = discord.Embed(title=title, description=desc)
                #     embed.add_field(name='Home', value=home)
                #     embed.add_field(name='Away', value=away)
                #     await channel.send(embed=embed)
            # if game['stats'][0] == game_data[0]:
            #     print("moar werk")
            # if game['stats']
            game['stats'] = json.dumps(game['stats'])
            fixture_data_new.append(game)
        else:
            # fixture_data_new.append(fixture_data.iloc[index])
            game['stats'] = json.dumps(game['stats'])
            fixture_data_new.append(game)
        # game['stats'] = json.dumps(game['stats'])
        # else:
        #     fixture_data_new.append()
    fixture_data_df = pd.DataFrame(fixture_data_new)
    # print(fixture_data_df)
    con = sqlite3.connect("fplbot.db")
    fixture_data_df.to_sql("fixtures", con, if_exists="replace")
    con.close()
    #     # if game['finished']:
    #     #     continue
    #     print(game['event'])
    #     if not game['started']:
    #         continue
    # print(game)
    # await channel.send("DONE")


@tasks.loop(seconds=10)
async def twitter_bot(ctx, channel):
    global tweet_id
    tweet_data = []
    headers = {
        'Authorization': 'Bearer ' + BEARER
    }
    if tweet_id:
        url = 'https://api.twitter.com/2/users/761568335138058240/tweets?max_results=5&since_id=' + tweet_id
    else:
        url = 'https://api.twitter.com/2/users/761568335138058240/tweets?max_results=5'
    try:
        response = requests.get(url, headers=headers)
        print("twitter working")
        print(response)
        if response.json()['meta']['result_count'] != 0:
            tweet_id = response.json()['data'][0]['id']
            for tweet in response.json()['data']:
                if 'Goal' in tweet['text'] and 'Assist' in tweet['text']:
                    embed = discord.Embed(description=tweet['text'])
                    await channel.send(embed=embed)
    except Exception as e:
        await ctx.send("Error connecting to twitter API: {}".format(e))


def team_fixtures_by_id(team_id):
    fixtures = []
    teams = {}
    con = sqlite3.connect("fplbot.db")
    team_data_temp = pd.read_sql_query("SELECT * FROM teams", con)
    fixture_data_temp = pd.read_sql_query("SELECT * FROM fixtures", con)
    print(fixture_data_temp)
    con.close()
    team_data = team_data_temp.values.tolist()
    fixture_data = fixture_data_temp.values.tolist()
    for team in team_data:
        teams[team[4]] = team[6]
    if team_id > 0 and team_id < 21:
        for fixture in fixture_data:
            if not fixture[3]:
                if team_id == fixture[10]:
                    fixtures.append([fixture[2], teams[fixture[12]], 'A'])
                elif team_id == fixture[12]:
                    fixtures.append([fixture[2], teams[fixture[10]], 'H'])
    return(fixtures)


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
            player_fixtures = team_fixtures_by_id(player[27])
            fixtures = "```\n"
            for x in range(0, 5):
                fixtures += "GW-{:02d}: {} ({})\n".format(player_fixtures[x][0], player_fixtures[x][1], player_fixtures[x][2])
            fixtures += "```"
            changes = "```\n" + lookup_price_changes(player[15], ctx.guild) + "\n```"
            embed = discord.Embed(title=title)
            embed.set_thumbnail(url=image)
            embed.add_field(name='Info', value=player_result)
            embed.add_field(name='Upcoming Fixtures', value=fixtures, inline=False)
            embed.add_field(name='Price Changes', value=changes, inline=False)
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
            if not fixture[3]:
                if team_search_id == fixture[10]:
                    # diff = fixture[15] - fixture[16] - 1
                    # if diff > 0:
                    #     diff_emoji = '\U0001F7E2'
                    # elif diff < 0:
                    #     diff_emoji = '\U0001F534'
                    # else:
                    #     diff_emoji = '\U000026AA'
                    fixtures += "GW-{:02d}: {} (A)\n".format(fixture[2], teams[fixture[12]] + ' ' * (14 - len(teams[fixture[12]])))
                elif team_search_id == fixture[12]:
                    # diff = fixture[16] - fixture[15]
                    # if diff > 0:
                    #     diff_emoji = '\U0001F7E2'
                    # elif diff < 0:
                    #     diff_emoji = '\U0001F534'
                    # else:
                    #     diff_emoji = '\U000026AA'
                    fixtures += "GW-{:02d}: {} (H)\n".format(fixture[2], teams[fixture[10]] + ' ' * (14 - len(teams[fixture[10]])))
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
                    fixtures += "GW-{:02d}: {} {} - {} {} {}\n".format(fixture[2], ' ' * (14 - len(teams[fixture[12]])) + teams[fixture[12]], int(fixture[13]), int(fixture[11]), teams[fixture[10]] + ' ' * (14 - len(teams[fixture[10]])), win_loss_emoji)
                # if team_search_id == fixture[10]:
                    # fixtures += "GW-{}: {} {} - {} {}\n".format(fixture[2], teams[fixture[12]], int(fixture[13]), teams[fixture[10]], int(fixture[11]))
                # elif team_search_id == fixture[12]:
                    # fixtures += "GW-{}: {} {} - {} {}\n".format(fixture[2], teams[fixture[12]], int(fixture[13]), teams[fixture[10]], int(fixture[11]))
        fixtures += "```"
        embed = discord.Embed(title='{} Fixtures'.format(teams[team_search_id]), description=fixtures)
        embed.set_thumbnail(url=image)
        # embed.add_field(name='{} Fixtures'.format(teams[team_search_id]), value=fixtures)
        print(len(fixtures))
        await ctx.send(embed=embed)
    else:
        await ctx.send("Team not found")


@bot.command(name='dump', help='Dumps all FPL API data into sqlite db')
async def dump_test(ctx):
    # player_data = []
    team_data = []
    fixture_data = []
    response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    fixture_response = requests.get('https://fantasy.premierleague.com/api/fixtures/')
    for team in response.json()['teams']:
        team_data.append(team)
    for fixture in fixture_response.json():
        fixture['stats'] = json.dumps(fixture['stats'])
        if fixture['code'] == 2210282:
            # fixture['stats'] = '[]'
            # fixture['stats'] = json.dumps(fixture['stats'][0])
            fixture['stats'] = '[{"identifier": "goals_scored", "a": [], "h": [{"value": 1, "element": 42}]}, {"identifier": "assists", "a": [], "h": [{"value": 1, "element": 38}]}]'
        fixture_data.append(fixture)
    con = sqlite3.connect("fplbot.db")
    team_data_df = pd.DataFrame(team_data)
    team_data_df.to_sql("teams", con, if_exists="replace")
    fixture_data_df_temp = pd.DataFrame(fixture_data)
    print(fixture_data_df_temp)
    # fixture_data_df = fixture_data_df_temp.drop(['stats'], axis=1)
    # fixture_data_df.to_sql("fixtures", con, if_exists="replace")
    fixture_data_df_temp.to_sql("fixtures", con, if_exists="replace")
    con.close()
    await ctx.send('all team and fixture data dumped into sqlite db')


# @bot.command(name='up', help='Show players likely to rise in price')
# async def find_up(ctx, val: int):
#     try:
#         last_scrape = datetime.datetime.fromtimestamp(os.path.getmtime('data.csv'), tz=pytz.timezone("Europe/London"))
#         pd_results = pd.read_csv('data.csv')
#         new_temp = pd_results.drop(['Fixtures', 'Name.1', 'Arrow.1', 'Target.1', '#', 'Price', 'Position', 'Arrow', 'Unlocks', 'Club', 'Status', 'Owned'], axis=1)
#         response = new_temp.values.tolist()
#         block_result = "```\n"
#         for i in response:
#             if i[4] >= val:
#                 block_result += "{} - {} ({})\n".format(i[0], i[1], i[4])
#         block_result += "```\nLast updated: {}".format(last_scrape.strftime("%H:%M %d-%m-%Y"))
#     except:
#         block_result = "```\nNo data availible\n```"
#     embed = discord.Embed()
#     embed.add_field(name='Potential Rises', value=block_result)
#     await ctx.send(embed=embed)


# @bot.command(name='down', help='Show players likely to fall in price')
# async def find_down(ctx, val: int):
#     try:
#         last_scrape = datetime.datetime.fromtimestamp(os.path.getmtime('data.csv'), tz=pytz.timezone("Europe/London"))
#         pd_results = pd.read_csv('data.csv')
#         new_temp = pd_results.drop(['Fixtures', 'Name.1', 'Arrow.1', 'Target.1', '#', 'Price', 'Position', 'Arrow', 'Unlocks', 'Club', 'Status', 'Owned'], axis=1)
#         response = new_temp.values.tolist()
#         block_result = "```\n"
#         for i in response:
#             if i[4] <= -val:
#                 block_result += "{} - {} ({})\n".format(i[0], i[1], i[4])
#         block_result += "```\nLast updated: {}".format(last_scrape.strftime("%H:%M %d-%m-%Y"))
#     except:
#         block_result = "```\nNo data availible\n```"
#     embed = discord.Embed()
#     embed.add_field(name='Potential Drops', value=block_result)
#     await ctx.send(embed=embed)


bot.run(TOKEN)
