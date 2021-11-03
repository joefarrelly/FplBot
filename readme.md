# Discord bot for FPL

## Overview

FplBot is a discord bot that provides updates on player price changes as they happen, as well as live match updates and bonus points awarded after each game. You can also lookup players by name to see some information like upcoming fixtures and previous price changes and more. You can lookup teams by name to see a complete list of all of their fixtures and results, and you can see the current league standings.

## Technologies

- Python 3.8.10
- Pandas 1.3.2
- SQLite 3.31.1
- Discord py 1.7.3

## Command List

Prefix for all commands is set in the env file, **!fpl** is recommended.

- **changes** : Displays all price changes from the current gameweek.
- **table** : Displays the current league standings in a table.
- **search** or **s** : Lookup a player by name.
- **team** : Search a team by name and show the fixtures/results for the season.
- **sync** : Run this command once to make the bot work.
- **help** : List all commands available.

## Discord API Setup
First step is to get a **Discord Token** for your bot. Go [here](https://discord.com/developers/applications) and create a new application as follows:
- Create a new application:
    - Click the **"New Application"** button in the top right of the Applications screen.
    - Enter the project name (try to choose a unique name as this is used automatically when creating the bot) and click the **"Create"** button.
    - The application name and bot name can be changed after creation so don't worry too much about the name, just try to make it unique so you get no errors when creating the bot.
- Add bot to the application:
    - In the Settings Menu on the left-hand side click **"Bot"**.
    - Click **"Add Bot"** button in the top right of the Bot screen.
    - Confirm creation of the bot by clicking the **"Yes, do it!"** button.
    - If you get an error here, go back to the General Information screen and rename your app to something more unique, then repeat the steps to add the bot to the application.
- On the Bot screen you should now see Build-A-Bot, which allows you to change the icon and name of the bot that will show in your discord.
- Additionally there will be a small TOKEN section below the name with **"Copy"** and **"Regenerate"** buttons, this is the token you will need for the Backend Setup below.
- The rest of the options on the Bot screen can all be left as they are, the only one I would recommend changing is the top option **"Public Bot"** so that the bot can only be added to servers by you.
- Add newly created bot to your discord server:
    - In the Settings Menu on the left-hand side click **"OAuth2"**.
    - In the SCOPES section at the bottom of the page tick the box **"bot"**.
    - Ignore the BOT PERMISSIONS section as the bot will be given the necessary permissions by default.
    - Click the **"Copy"** button in the bottom right of the SCOPES section.
    - Open a new tab in your browser and paste the link you just copied.
    - From the dropdown select the name of the server you want to add the bot to.
    - Click the **"Authorize"** button in the bottom right and you should now see the bot in your server! Note it will be in the offline section of your user list as the backend of the bot is not running yet.

## Backend Setup
Clone the repo:
```bash
git clone https://github.com/joefarrelly/FplBot.git 
```
Update repo:
* Using `.env.sample` as a template, create `.env` in `~/FplBot/.env`, where the values are:
    * DISCORD_TOKEN: Your bot token from the Discord API Setup.
    * COMMAND_PREFIX: The prefix you want all of your bot commands to start with.
    * DEBUG_OPTION: Leave this blank, I changed this to 1 for testing.
    * CHANNEL: The name of the channel in your server that you would like live match updates and price changes to be posted to.

Install the packages needed:
```bash
pip install -r requirements.txt
```

## Running the Tool

Make sure you are inside the FplBot directory and start the bot using:
```bash
python main.py
```

In any channel run the command **!fpl sync**, replacing !fpl with whatever value you set for COMMAND_PREFIX in the .env file.

## Images

![demo_live](https://i.imgur.com/FdFGU2n.png)

![demo_price_changes](https://i.imgur.com/eOrLS3z.png)

![demo_player_search](https://i.imgur.com/tYXl1S4.png)

![demo_table](https://i.imgur.com/FVoTzMV.png)

![demo_team_search](https://i.imgur.com/ui8EQTJ.png)