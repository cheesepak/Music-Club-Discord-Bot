# ================================================================================================ #
# --- Music Club Discord Bot - bot.py ------------------------------------------------------------ #
# ================================================================================================ #

import sys
import subprocess
import discord 
import platform
import gspread
import asyncio
import requests
import json
import random
from datetime import datetime, timedelta, date
from discord.ext import commands, tasks
from settings import * 

VERSION = "0.5.5"

# Album Days
TODAY = 0       
PREVIOUS = -1
UPCOMING = 1    
UPUPCOMING = 2  
ERROR = "Unable to find the album 🎶"
LIMIT = 95 # Character Limit for thread titles

gc = gspread.service_account_from_dict(CREDENTIALS)

intents = discord.Intents().all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)
bot.remove_command('help') 

# The /mu/core Google spreadsheet
mu = gc.open("mu core")
musheet =  mu.sheet1

# --- Functions ---------------------------------------------------------------------------------- #

# Handles the date format #/#/#### based on OS
def get_formatted_date():
    now = datetime.now()
    if platform.system() == 'Windows': 
        return now.strftime("%#m/%#d/%Y")
    else:
        return now.strftime("%-m/%-d/%Y")

# Check's date stored in data.txt; called when today's date is not on the spreadsheet
def check_date():
    file = open('date.txt', 'r') 
    saved_date = file.read()
    file.close()
    return saved_date

# Update date.txt to today's date
def update_date_today():
    date_str = get_formatted_date()
    file = open('date.txt', 'w') 
    file.write(date_str)
    print(f"Updated date.txt: ({file.read()})")
    file.close()

# Fetch album information from the Google spreadsheet
def find_album(date_str_in, adjacent_in):
    date_cell = musheet.find(date_str_in) #find matching cell in spreadsheet, substringed to match
    # A = Date, B = Username, C = Artist, D = Album, E = Genre, F = Track Highlight, G = Notes
    mu_album = [musheet.get(('A%s') % (date_cell.row + adjacent_in)), musheet.get(('B%s') % (date_cell.row + adjacent_in)), musheet.get(('C%s') % (date_cell.row + adjacent_in)), musheet.get(('D%s') % (date_cell.row + adjacent_in)), musheet.get(('E%s') % (date_cell.row + adjacent_in)), musheet.get(('F%s') % (date_cell.row + adjacent_in)),musheet.get(('G%s') % (date_cell.row + adjacent_in))]
    mu_album_str = (mu_album[0][0][0], mu_album[1][0][0], mu_album[2][0][0], mu_album[3][0][0], mu_album[4][0][0])
    return mu_album_str 

# TENOR gif search
def get_gif(search_term):
    # get the top 8 GIFs for the search term
    r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, TENOR_APIKEY, ckey,  lmt))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_8gifs = json.loads(r.content)
    else:
        top_8gifs = None

    return top_8gifs

# --- Midnight Tasks ----------------------------------------------------------------------------- #

def seconds_until_midnight():
    now = datetime.now()
    target = (now + timedelta(days=1)).replace(hour=0, minute=2, second=0, microsecond=0)
    # --- Tester ---
    #target = (now + timedelta(days=0)).replace(hour=10, minute=22, second=0, microsecond=0) 
    diff = (target - now).total_seconds()
    print(f"Seconds Until Midnight: {target} - {now} = {diff}")
    return diff

def seconds_until_10am():
    now = datetime.now()
    target = (now + timedelta(days=1)).replace(hour=10, minute=1, second=0, microsecond=0)
    diff = (target - now).total_seconds()
    print(f"Seconds Until 10AM: {target} - {now} = {diff}")
    return diff

# Edit thread to today's album on one server and post an embed message in a music channel on another
@tasks.loop(hours=24)
async def called_once_a_day_at_midnight():
    await asyncio.sleep(seconds_until_midnight())
    
    print(f"Midnight tasks begin ({datetime.now()})")
    date_str = get_formatted_date()
    weekday = datetime.now().weekday()
    print(f"- {date_str}, {weekday}")

    if weekday in {0, 2, 4}:
        file = open('date.txt', 'w+') 
        file.write(date_str)
        print(f"- Updated date.txt") # ({file.read()})
        file.close()

    latest_date = check_date()
    mu_album = find_album(latest_date, TODAY)
    mu_album_w = find_album(latest_date, UPCOMING)
    mu_album_f = find_album(latest_date, UPUPCOMING)

    message_channel = bot.get_channel(CLUB_ID)  

    if date_str == latest_date: 
        limit = 95
        activity_str = f"{mu_album[1]} - {mu_album[2]}"

        # Checks string length and truncates to fit character limit if necessary
        activity_str_truc = activity_str[:limit] + '..' * (len(activity_str) > limit)

        # Set and change client's activity
        client_activity = (activity_str_truc)
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(client_activity))

        title_str = f"/{mu_album[0]}/core presents: {mu_album[1]} - {mu_album[2]}"
        title_str_truc = title_str[:limit] + '..' * (len(title_str) > limit)

        # Edit thread name to today's album
        thread = bot.get_channel(CLUB_ID)
        await thread.edit(name=title_str_truc)
        print("- Updated thread name and client activity")
    else:  
        print("- No album found for today")

    # if Monday, post the week's albums, if Wed or Fri, just post that day's album
    if weekday == 0: 
        try:
            # The big weekly music post
            embed = discord.Embed(title="🎵 This Week's Oubliette Essential Albums 🎵", 
            description=f"""
📣 Good morning, /Oubliette/core listeners 📣 
And if yoooooou can believe it, it's a **Monday** *once* ***again*** ✨

**MON**: {mu_album[1]} - {mu_album[2]} | {mu_album[4]}
**WED**: {mu_album_w[1]} - {mu_album_w[2]} | {mu_album_w[4]}
**FRI**: {mu_album_f[1]} - {mu_album_f[2]} | {mu_album_f[4]}
""", 
            color=discord.Color.teal())
            embed.set_thumbnail(url="https://i.imgur.com/bJVDPc0.png")
            await message_channel.send(embed=embed) 

            # Monday's music post
            embed2 = discord.Embed(title="🎵 Today's Oubliette Essentials Album 🎵", 
            description=f"Today's /{mu_album[0]}/core album is {mu_album[1]} - {mu_album[2]}. It's a {mu_album[4]} kind of day.", 
            color=discord.Color.teal())
            await message_channel.send(embed=embed2)
            print("- Posted this week's album in the thread")
            print("- Posted today's album in the thread")

            # Posts random gif of band
            gif_url = random.choice(get_gif(f"{mu_album[1]} band")['results'])['url']
            await message_channel.send(gif_url) 
            await message_channel.send(f"gif of {mu_album[1]} 😩 via Tenor")  
            print("- Posted gif of band")

        except (IndexError, AttributeError) as e:
            await message_channel.send("Unable to find this week's album 🎶")
            print("Error: ", e)
    elif weekday in {2, 4}:
        try:
            embed = discord.Embed(title="🎵 Today's Oubliette Essentials Album 🎵", 
            description=f"Today's /{mu_album[0]}/core album is {mu_album[1]} - {mu_album[2]}. It's a {mu_album[4]} kind of day.", 
            color=discord.Color.teal())
            await message_channel.send(embed=embed)
            print("- Posted today's album in the thread")

            # Posts random gif of band
            gif_url = random.choice(get_gif(f"{mu_album[1]} band")['results'])['url']
            await message_channel.send(gif_url) 
            await message_channel.send(f"gif of {mu_album[1]} 😩 via Tenor")  
            print("- Posted gif of band")
        except (IndexError, AttributeError) as e:
                await message_channel.send(ERROR)
                print("Error: ", e)

    print(f"Midnight tasks completed")

# --- On Ready ----------------------------------------------------------------------------------- #

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    latest_date = check_date()
    mu_album = find_album(latest_date, TODAY)
    client_activity = (f"{mu_album[1]} - {mu_album[2]}")
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(client_activity))
    if not called_once_a_day_at_midnight.is_running():
        called_once_a_day_at_midnight.start()
        print(f"Starting Midnight Task")

# --- Commands ----------------------------------------------------------------------------------- #     
# --- Album Commands - Set albums based on the trigger and bot responds it in the designated channel

# --- Today's/Latest album ---
@bot.command(aliases=['album', 'latest', 'current'])
async def today(ctx):
    latest_date = check_date()
    try:
        mu_album = find_album(latest_date, TODAY)
        date_str = get_formatted_date()
        if date_str == mu_album[3]:
            embed = discord.Embed(title="🎵 Today's Oubliette Essentials Album 🎵", 
            description=f"Today's /{mu_album[0]}/core album is {mu_album[1]} - {mu_album[2]}. It's a {mu_album[4]} kind of day.", 
            color=discord.Color.teal())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="🎵 Current Oubliette Essentials Album 🎵", 
            description=f"The current /{mu_album[0]}/core album is {mu_album[1]} - {mu_album[2]}. It's a {mu_album[4]} kind of day.", 
            color=discord.Color.teal())
            await ctx.send(embed=embed)
    except (IndexError, AttributeError) as e:
            await ctx.send(ERROR)
            print("Error: ", e)
    print(f'{ctx.message.author} triggered !today')

@bot.command(aliases=['genre'])
async def mood(ctx):
    latest_date = check_date()
    try:
        mu_album = find_album(latest_date, TODAY)
        await ctx.send(f"It's a {mu_album[4]} kind of day.")
    except (IndexError, AttributeError) as e:
            await ctx.send(ERROR)
            print("Error: ", e)
    print(f'{ctx.message.author} triggered !mood')

# --- Previous album ---
@bot.command(aliases=['prev'])
async def previous(ctx):
    latest_date = check_date()
    try:
        mu_album = find_album(latest_date, PREVIOUS)
        embed = discord.Embed(title="Previous Oubliette Essentials Album", 
        description=f"Previous /{mu_album[0]}/core album is {mu_album[1]} - {mu_album[2]}. It was a {mu_album[4]} kind of day.", 
        color=discord.Color.dark_teal())
        await ctx.send(embed=embed)
    except (IndexError, AttributeError) as e:
            await ctx.send(ERROR)
            print("Error: ", e)
    print(f'{ctx.message.author} triggered !previous')  

# --- Upcoming album ---
@bot.command(aliases=['next'])
async def upcoming(ctx):
    latest_date = check_date()
    try:
        mu_album = find_album(latest_date, UPCOMING)
        embed = discord.Embed(title="Upcoming Oubliette Essentials Album", 
        description=f"Next /{mu_album[0]}/core album is {mu_album[1]} - {mu_album[2]}. It will be a {mu_album[4]} kind of day.", 
        color=discord.Color.dark_teal())
        await ctx.send(embed=embed)
    except (IndexError, AttributeError) as e:
        await ctx.send(ERROR)
        print("Error: ", e)    
    print(f'{ctx.message.author} triggered !upcoming')  

# --- Upupcoming album (album after next) ---
@bot.command()
async def upupcoming(ctx):
    latest_date = check_date()
    try:
        mu_album = find_album(latest_date, UPUPCOMING)
        embed = discord.Embed(title="Upupcoming Oubliette Essentials Album", 
        description=f"The *next* next /{mu_album[0]}/core album is {mu_album[1]} - {mu_album[2]}. It will be a {mu_album[4]} kind of day.", 
        color=discord.Color.dark_teal())
        await ctx.send(embed=embed)
    except (IndexError, AttributeError) as e:
        await ctx.send(ERROR)
        print("Error: ", e)
    print(f'{ctx.message.author} triggered !upupcoming')

# --- gifposting ---
# Coming: posts a random gif of dreamybull using Tenor API OR random gif of whatever user input is, joke derived from upcoming
@bot.command(aliases=['cum', 'gif'])
@commands.cooldown(1, 5, commands.BucketType.guild)
async def coming(ctx,*,search_term:str=None):
    if not search_term:
        search_term = "dreamybull"
    gif_url = random.choice(get_gif(search_term)['results'])['url']
    await ctx.send(gif_url) 
    await ctx.send(f"gif of {search_term} 😩 via Tenor")  
    print(f'{ctx.message.author} triggered !coming @ {datetime.now()} | {gif_url}')  

# Posts a gif of the band
@bot.command(aliases=['vibe'])
@commands.cooldown(1, 5, commands.BucketType.guild)
async def vibes(ctx):
    latest_date = check_date()
    try:
        mu_album = find_album(latest_date, TODAY)
        gif_url = random.choice(get_gif(f"{mu_album[1]} band")['results'])['url']
        await ctx.send(gif_url) 
        await ctx.send(f"gif of {mu_album[1]} 😩 via Tenor")  
        print(f'{ctx.message.author} triggered !vibes @ {datetime.now()} | {gif_url}')  
    except (IndexError, AttributeError) as e:
        await ctx.send(ERROR)
        print("Error: ", e)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Sorry, that command wasn't found... 😩")

# --- Utility Commands --- 
# Manual Thread Title Edit: in case the midnight task did not complete for some reason 
# or a title change is necessary
@bot.command(aliases=['manual'])
async def fixtitle(ctx):
    latest_date = check_date()
    try:
        mu_album = find_album(latest_date, TODAY)
        thread = bot.get_channel(CLUB_ID)

        activity_str = f"{mu_album[1]} - {mu_album[2]}"
        
        # Checks string length and truncates to fit character limit if necessary
        activity_str_truc = activity_str[:LIMIT] + ('...' if len(activity_str) > LIMIT else '')

        # Set and change client's activity
        client_activity = (activity_str_truc)
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(client_activity))

        title_str = f"/{mu_album[0]}/core presents: {mu_album[1]} - {mu_album[2]}"
        title_str_truc = title_str[:LIMIT] + ('...' if len(title_str) > LIMIT else '')

        # Edit thread name to today's album
        await thread.edit(name=title_str_truc)

        await ctx.send("Set the thread title 🎶")
    except (IndexError, AttributeError) as e:
        await ctx.send("Unable to set the thread title 🎶")
        print("Error: ", e)
    print(f'{ctx.message.author} triggered !fixtitle') 

# Sets the data.txt to today | Todo: allow for date to be written in by a user if a date is given
@bot.command()
# @commands.is_owner() 
async def fixdate(ctx):
    datetime_str = get_formatted_date()
    try:
        file = open('date.txt', 'w') 
        file.write(datetime_str)
        await ctx.send(f"Fixed the date: now {file.read()} 📆") 
        file.close()
    except (IndexError, AttributeError) as e:
        await ctx.send("Error: ", e)
    print(f'{ctx.message.author} triggered !fixdate')

@bot.command()
async def checkdate(ctx):
    datetime_str = get_formatted_date()
    file = open('date.txt', 'r') 
    await ctx.send(f"Date on file is {file.read()} 📆")
    file.close()
    print(f'{ctx.message.author} triggered !checkdate')

# --- Help ---
@bot.command(aliases=['h'])
async def help(ctx):
    embed = discord.Embed(title="Music Club Bot Commands", 
    description=f"""
**!today**: today's album
**!prev**: previous album
**!next**: upcoming album (also !upcoming)
**!mood**: genre
**!vibes**: random gif of today's band
**!gif [whatever]**: random gif of your keyword
**!fixtitle**: In case something goes wrong(typo, null, etc), use this to manually set thread title after correct cell in spreadsheet has been modified
""", 
    color=discord.Color.dark_purple())
    embed.set_author(name="Sir Cheese", url="https://linktr.ee/sircheese", icon_url="https://d1fdloi71mui9q.cloudfront.net/mpdu5KysQIyH6FQbqWHX_40d0QF5e727bz4Hu")
    embed.set_thumbnail(url="https://i.imgur.com/mLZdGql.png")
    embed.set_footer(text=f"Let me know if you have any feature requests.\nMusic Club Bot {VERSION}")
    await ctx.channel.send(embed=embed)
    print(f'{ctx.message.author} triggered !help')

# --- Debugging / Testing ------------------------------------------------------------------------ #
    
# --- Ping ---
@bot.command()
async def ping(ctx):
    await ctx.reply(f"Pong! 🏓")
    await ctx.send(f'>>> {round(bot.latency * 1000)} ms')
    print(f'{ctx.message.author} pinged client')

# --- Restarts bot ---
@bot.command(name= 'restart')
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Restarting bot...")
    
    # Re-run the script using subprocess
    python = sys.executable
    script = sys.argv[0]
    
    # Restart the bot using subprocess
    subprocess.Popen([python, script])
    
    # Optionally exit the current process
    await bot.close()
    sys.exit()

# --- Generic test command ---
# Throw whatever in here for testing
@bot.command()
@commands.is_owner()
async def test(ctx):  
    latest_date = check_date()
    mu_album = find_album(latest_date, TODAY)
    mu_album_m = find_album(latest_date, TODAY)   
    mu_album_w = find_album(latest_date, UPCOMING)
    mu_album_f = find_album(latest_date, UPUPCOMING)

    embed = discord.Embed(title="🎵 This Week's Oubliette Essentials Album 🎵", 
    description=f"""
💿 **Album**: {mu_album[2]}
🎤 **Artist**: {mu_album[1]}
📻 **Genre**: {mu_album[4]}

📝 **Suggested by {mu_album[0]}**

**MON**: {mu_album_m[1]} - {mu_album_m[2]} | {mu_album_m[4]}
**WED**: {mu_album_w[1]} - {mu_album_w[2]} | {mu_album_w[4]}
**FRI**: {mu_album_f[1]} - {mu_album_f[2]} | {mu_album_f[4]}
""", 
    color=discord.Color.teal())
    embed.set_thumbnail(url="https://i.imgur.com/bJVDPc0.png")
    await ctx.send(embed=embed)

    print(f'{ctx.message.author} triggered !test')

# --- Run ---------------------------------------------------------------------------------------- #
    
bot.run(TOKEN)

