import discord

from discord.ext import commands
from discord import Color

from discord.ext.commands.errors import MissingRequiredArgument, NoPrivateMessage, MissingRole, CommandNotFound


from dotenv import dotenv_values

from PIL import Image
import io

import argparse
import requests
import urllib.parse
import json
import time
import random

import logging
from  logging.handlers import TimedRotatingFileHandler
#https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler

version = 'v0.0.1-beta'

cliParser = argparse.ArgumentParser(prog='mtg_tournament_bot', description='MTG Tournament Helper Bot', epilog='', add_help=False)
cliParser.add_argument('-e', '--env', choices=['DEV', 'PROD'], default='DEV', action='store')
cliParser.add_argument('-d', '--debug', default=False, action='store_true')
cliArgs = cliParser.parse_args()

logging_handler = TimedRotatingFileHandler("./bot-log.log", when="midnight")
#logging.FileHandler("./bot-log.log")
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)-16s] [%(levelname)-8s] %(module)s.%(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.StreamHandler(), logging_handler])
logger = logging.getLogger()
dmlogger = logging.getLogger('DirectMessage')
gmlogger = logging.getLogger('GuildMessage')

if cliArgs.debug:
    logger.setLevel(Logging.DEBUG)
    dmlogger.setLevel(Logging.DEBUG)
    gmlogger.setLevel(Logging.DEBUG)
    logger.debug("DEBUG TURNED ON")
    
dev_env = dotenv_values(".devenv")
prod_env = dotenv_values(".prodenv")

bot_env = dev_env
if('PROD' == cliArgs.env.upper()):
    bot_env = prod_env
    logger.info(f'THIS IS RUNNING IN PRODUCTION MODE AND WILL CONNECT TO PRODUCTION BOT TO THE MAIN JUMPSTART DISCORD SERVER')
else:
    logger.info(f'This is running DEVELOPMENT MODE and the DEVELOPMENT bot will connect to your test server')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=['!m-', '!t-', '!l-'], intents=intents) #command_prefix can be one item - i.e. '!' or a list - i.e. ['!','#','$']

# listParser = argparse.ArgumentParser(prog='!list', description='Simple JumpStart List Query Command', epilog='Example(s):\n!list --set JMP TEFERI\n!list TEFERI', add_help=False, formatter_class=argparse.RawTextHelpFormatter)
# listParser.add_argument('list', action='store') #look into nargs so we don't have to "" the lists?  This would introduct string concatination on the list that's the result.
# listParser.add_argument('-s', '--set', choices=['ALL', 'JMP', 'J22', 'DMU', 'BRO', 'ONE', 'MOM', 'LTR'], default='ALL', action='store')
# listParser.add_argument('-n', '--number', choices=['1', '2', '3', '4'], default=1, action='store') #might not want to default to 1 here, but think of a better way to handle this

# pickParser = argparse.ArgumentParser(prog='!pick', description='Pick n Random JumpStart Packs Command', epilog='Example(s):\n!pick --set JMP \n!p3 --set J22\n!p3 --set J22 --type themes', add_help=False, formatter_class=argparse.RawTextHelpFormatter)
# pickParser.add_argument('-n', '--number', choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], default=3, action='store')
# pickParser.add_argument('-s', '--set', choices=['ALL', 'JMP', 'J22', 'DMU', 'BRO', 'ONE', 'MOM', 'LTR'], default='JMP', action='store')
# pickParser.add_argument('-t', '--type', choices=['themes', 'THEMES', 'Themes', 't', 'T', 'lists', 'LISTS', 'l', 'L', "Lists"], default='themes', action='store')
# pickParser.add_argument('--nodupes', action='store_true')
#MRCUS - rarity

@bot.event
async def on_ready():
    #print(f'{jsd.jumpstart}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="MTG Tournament Lo-Fi"))
    logger.info(f'We have logged in as {bot.user} with status {bot.status}')

#using @bot.listen() will listen for messages, but will continue processing commands, so having the await bot.process_commands(message) when this is set with @bot.listen() decorator it will fire the command twice.
@bot.event  
async def on_message(message):
    if message.author == bot.user: #avoid infinite loops
        return
    if not isinstance(message.channel, discord.DMChannel) and message.channel.name != 'bot-testing' and message.channel.name != 'pauper-league-bot-testing' : #only allow processing of messages in the bot-testing channel and DMs
        return

    #Fix "auto-completed" en and em dashes
    message.content = message.content.replace('\u2013', '--')
    message.content = message.content.replace('\u2014', '--')
    #Fix fancy single quotes
    message.content = message.content.replace('\u2018', '\'')
    message.content = message.content.replace('\u2019', '\'')
    #Fix fancy double quotes
    message.content = message.content.replace('\u201C', '"')
    message.content = message.content.replace('\u201D', '"')

    logger.debug(f"{bot}")
    #print(f"{bot.get_guild(message.guild.id)}")

    if isinstance(message.channel, discord.DMChannel):
        dmlogger.info(f'{message.created_at}, DIRECT_MESSAGE, Channel: {message.channel}({message.channel.id}), Author: {message.author}({message.author.id}), Message: {message.content}')
    else:
        gmlogger.info(f'{message.created_at}, Guild: {message.guild}({message.guild.id}), Channel: {message.channel}({message.channel.id}), Author: {message.author}({message.author.id}), Author Roles: {message.author.roles}, Message: {message.content}')

    await bot.process_commands(message) #this will continue processing to allow commands to fire.

@bot.event
async def on_command_error(ctx, error):
    if isinstance(ctx.message.channel, discord.DMChannel):
        logger.error(f'{ctx.message.created_at}, DIRECT_MESSAGE, Channel: {ctx.channel}({ctx.channel.id}), Author: {ctx.author}({ctx.author.id}), Message: {ctx.message.content}')
    else:
        logger.error(f'{ctx.message.created_at}, Guild: {ctx.guild}({ctx.guild.id}), Channel: {ctx.channel}({ctx.channel.id}), Author: {ctx.author}({ctx.author.id}), Author Roles: {ctx.author.roles}, Message: {ctx.message.content}')

    if isinstance(error, MissingRequiredArgument):
        # await ctx.send("There was an issue processing your command.  Please try again.")
        return
    if isinstance(error, NoPrivateMessage):
        logger.error(error)
        return
    if isinstance(error, MissingRole):
        logger.error(error)
        return
    if isinstance(error, CommandNotFound):
        logger.error(error)
        return
    raise error

@bot.command()
async def context(ctx):

    guild_information = f'GUILD: {ctx.guild}'
    channel_information = f'CHANNEL: {ctx.channel}\n    CHANNEL-ID: {ctx.channel.id}\n    CHANNEL-ID_TYPE: {type(ctx.channel.id)}'
    if ctx.guild != None:
        guild_information = f'{guild_information}\n    GUILD-ID: {ctx.guild.id}\n    GUILD-ID_TYPE: {type(ctx.guild.id)}'
    else:
        channel_information = f'{channel_information}\n    CHANNEL-RECIPIENT: {ctx.channel.recipient}'

    logger.info(f"""
    ARGS: {ctx.args}
    AUTHOR: {ctx.author}
    AUTHOR-ID: {ctx.author.id}
    AUTHOR-ID_TYPE: {type(ctx.author.id)}
    BOT: {ctx.bot}
    BOT_PERMISSIONS: {ctx.bot_permissions}
    {channel_information}
    CLEAN_PREFIX: {ctx.clean_prefix}
    COG: {ctx.cog}
    COMMAND: {ctx.command}
    COMMAND_FAILED: {ctx.command_failed}
    CURRENT_ARGUMENT: {ctx.current_argument}
    CURRENT_PARAMETER: {ctx.current_parameter}
    FILESIZE_LIMIT: {ctx.filesize_limit}
    {guild_information}
    INTERACTION: {ctx.interaction}
    INVOKED_PARENTS: {ctx.invoked_parents}
    INVOKED_SUBCOMMAND: {ctx.invoked_subcommand}
    INVOKED_WITH: {ctx.invoked_with}
    KWARGS: {ctx.kwargs}
    ME: {ctx.me}
    MESSAGE: {ctx.message}
    MESSAGE_CONTENT: {ctx.message.content}
    PERMISSIONS: {ctx.permissions}
    PREFIX: {ctx.prefix}
    SUBCOMMAND_PASSED: {ctx.subcommand_passed}
    VALID: {ctx.valid}
    VOICE_CLIENT: {ctx.voice_client}'""")
    



@bot.command()
async def ping(ctx, hidden=True):
    await ctx.send("pong")
    await ctx.author.send("Really?!?  OK, PONG!")
    logger.info(f'User Roles for ping: {ctx.author.roles}')

@bot.command()
@commands.has_any_role("TournamentOrganizer", "League Organizer")
#has_role requires all the roles listed
async def test(ctx):
    await ctx.author.send(f'You have the right role!')
    await ctx.send(f"Well isn't this interesting?")

@bot.command()
@commands.is_owner()
async def test2(ctx):
    await ctx.author.send(f'Send to owner?')
    await ctx.send(f"You are my owner!") #if this was in a DM, will be sent back to the DM.

#Participant Commands (Anyone Commands) - I wonder if thses should send direct to the user

@bot.command(name='displayActiveTournaments', aliases=['active', 'a'])
async def display_active_tournaments(ctx, tournament_format: str = commands.parameter(displayed_name="Tournament Format", default="All", description="[All, Pauper, Modern, Pre-Modern, Standard]")):
    await ctx.send(f"Active Tournament listing for format '{tournament_format}'")

@bot.command(name='registerForTournament', aliases=['register', 'r'])
async def register_for_tournament(ctx, tournament_id: int = commands.parameter(displayed_name="The ID of the Tournament to Register for", description="The Tournament ID of the Tournament to Register for.")):
    await ctx.send(f"Registering for tournament ID {tournament_format}")
    #need to pull in ctx.author and ctx.author.id for DMing later

@bot.command(name='unRegisterFromTournament', aliases=['unregister', 'u'])
async def unregister_from_tournament(ctx, tournament_id: int = commands.parameter(displayed_name="The ID of the Tournament to Un-Register for", description="The Tournament ID of the Tournament to Un-Register for.")):
    await ctx.send(f"Removing Registering from {tournament_format}")

@bot.command(name='submitDeckList', aliases=['submit', 'deck', 'decklist'])
async def register_for_tournament(ctx, tournament_format: str = commands.parameter(displayed_name="Tournament to Register For", default="All", description="Either the Tournament ID, or if there's only one 'registration active' tournament for a given format, the format can be used to shortcut it.")):
    await ctx.send(f"Submitting DeckList for {tournament_format} as 'decklist'")

#The tournaments the user has registered for
@bot.command(name='getRegistrationInformation', aliases=['get', 'g', 'registrations'])
async def get_registrations(ctx):
    await ctx.send(f"Getting Tournament Registration Information for user for active tournaments")
    #This should return the registation ID along with the information


# @bot.command(name='registerForTournament', aliases=['register', 'r'])
# async def register_for_tournament(ctx, tournament_format: str = commands.parameter(displayed_name="Tournament to Register For", default="All", description="Either the Tournament ID, or if there's only one 'registration active' tournament for a given format, the format can be used to shortcut it.")):
#     await ctx.send(f"Registering for {tournament_format}")

# @bot.command(name='unRegisterFromTournament', aliases=['unregister', 'u'])
# async def unregister_from_tournament(ctx, tournament_format: str = commands.parameter(displayed_name="Tournament to Register For", default="All", description="Either the Tournament ID, or if there's only one 'registration active' tournament for a given format, the format can be used to shortcut it.")):
#     await ctx.send(f"Removing Registering from {tournament_format}")

# @bot.command(name='submitDeckList', aliases=['submit', 'deck', 'decklist'])
# async def register_for_tournament(ctx, tournament_format: str = commands.parameter(displayed_name="Tournament to Register For", default="All", description="Either the Tournament ID, or if there's only one 'registration active' tournament for a given format, the format can be used to shortcut it.")):
#     await ctx.send(f"Submitting DeckList for {tournament_format} as 'decklist'")


######################################################################################################
##### League Organizer Only Commands
######################################################################################################

###Create a new tournament
@bot.command(name='newTournament', aliases=['nt'], description="Creates a new MTG tournament", brief="New Tournament", hidden=False)
@commands.has_any_role("Admin", "League Organizer")
async def new_tournament(ctx, tournament_start_date: str = commands.parameter(displayed_name="Tournament Start Date", description="YYYYMMDD"),
                              tournament_format: str = commands.parameter(displayed_name="Tournament Format", default="Pauper", description="[Pauper, Modern, Pre-Modern, Standard]"), 
                              tournament_style: str  = commands.parameter(displayed_name="Tournament Style", default="Swiss", description="[Swiss, Bracket, Pool]"), 
                              tournament_type: str = commands.parameter(displayed_name="Tournament Type", default="Monthly", description="[Monthly, League, Tournament]"),
                              tournament_name: str = commands.parameter(displayed_name="Tournament Name", default="PlayAway", description="The Name of the Tournament")):
    """
    Could add more detailed information here about usage?

    Combination of Tournament Start Date and Tournament Name should be unique
    """
    await ctx.send(f"Creating a new tournament {tournament_format} {tournament_style} {tournament_type} to start on {tournament_start_date} with name of '{tournament_name}' and created by '{ctx.author} ({ctx.author.id})'")
    #Message Author will be the creator of the tournament
    tournament_id = 1
    await ctx.send(f"Tournament created with ID {tournament_id} - you should save this and use this to be able to manage the tournament.")

###Display or List tournaments
@bot.command(name='listTournaments', aliases=['ls', 'lt'], description="Lists MTG tournaments based on filters", brief="List Tournaments", hidden=False)
@commands.has_any_role("Admin", "League Organizer")
async def new_tournament(ctx, tournament_format: str = commands.parameter(displayed_name="Tournament Format", default="All", description="[All, Pauper, Modern, Pre-Modern, Standard]"), 
                              tournament_style: str  = commands.parameter(displayed_name="Tournament Style", default="All", description="[All, Swiss, Bracket, Pool]"), 
                              tournament_type: str = commands.parameter(displayed_name="Tournament Type", default="All", description="[All, Monthly, League, Tournament]"),
                              tournament_start_date_after: str = commands.parameter(displayed_name="Tournament Start Date After", default="19700101", description="YYYYMMDD")):
    """
    Could add more detailed information here about usage?

    Combination of Tournament Start Date and Tournament Name should be unique
    """
    await ctx.send(f"Listing tournamnets based on the following filter {tournament_format} {tournament_style} {tournament_type} to start on or after {tournament_start_date}.")

###Open a tournament for registration
@bot.command(name='openTournament', aliases=['ot'], description="Opens a MTG tournament for registration by passing in the ID of the tournament", brief="Open Tournament", hidden=False)
@commands.has_any_role("Admin", "League Organizer")
async def open_tournament_id(ctx, tournament_id: int = commands.parameter(displayed_name="Tournament ID", default="0", description="The ID of the tournament you want to open for registration")):
    """
    Could add more detailed information here about usage?

    Combination of Tournament Start Date and Tournament Name should be unique
    """
    await ctx.send(f"Locating tournament with ID of {tournament_id} to open it for registration")

# @bot.command(name='openTournamentLong', aliases=['otl'], description="Opens a MTG tournament for registration by passing in the start date of the tournament along with the tournament name.", brief="Open Tournament", hidden=False)
# @commands.has_any_role("Admin", "League Organizer")
# async def new_tournament(ctx, tournament_start_date: str = commands.parameter(displayed_name="Tournament Start Date", description="YYYYMMDD"),
#                               tournament_name: str = commands.parameter(displayed_name="Tournament Name", description="The Name of the Tournament")):
#     """
#     Could add more detailed information here about usage?

#     Combination of Tournament Start Date and Tournament Name should be unique
#     """
#     await ctx.send(f"Locating tournament with start date of {tournament_start_date} and name of {tournament_name} to open it for registration")


###Close a tournament from new registrations
@bot.command(name='closeTournament', aliases=['ct'], description="Closes a MTG tournament for any new registrations by passing in the ID of the tournament", brief="Close Tournament", hidden=False)
@commands.has_any_role("Admin", "League Organizer")
async def open_tournament_id(ctx, tournament_id: int = commands.parameter(displayed_name="Tournament ID", default="0", description="The ID of the tournament you want to close from registration")):
    """
    Could add more detailed information here about usage?

    Combination of Tournament Start Date and Tournament Name should be unique
    """
    await ctx.send(f"Locating tournament with ID of {tournament_id} to close registrations")

# @bot.command(name='closeTournamentLong', aliases=['ctl'], description="Closes a MTG tournament for any new registrations by passing in the start date of the tournament along with the tournament name.", brief="Close Tournament", hidden=False)
# @commands.has_any_role("Admin", "League Organizer")
# async def new_tournament(ctx, tournament_start_date: str = commands.parameter(displayed_name="Tournament Start Date", description="YYYYMMDD"),
#                               tournament_name: str = commands.parameter(displayed_name="Tournament Name", description="The Name of the Tournament")):
#     """
#     Could add more detailed information here about usage?

#     Combination of Tournament Start Date and Tournament Name should be unique
#     """
#     await ctx.send(f"Locating tournament with start date of {tournament_start_date} and name of {tournament_name} to close registrations")



###Start a tournament
@bot.command(name='startTournament', aliases=['st'], description="Starts a MTG tournament and progresses to round 1", brief="Start Tournament", hidden=False)
@commands.has_any_role("Admin", "League Organizer")
async def open_tournament_id(ctx, tournament_id: int = commands.parameter(displayed_name="Tournament ID", default="0", description="The ID of the tournament you want to open for registration")):
    """
    Could add more detailed information here about usage?

    Combination of Tournament Start Date and Tournament Name should be unique
    """
    await ctx.send(f"Starting the tournament with ID of {tournament_id}!!")
    await ctx.send(f"Pairing for Round 1 Generated")
    await ctx.send(f"Posting in Tournament Channel")
    await ctx.send(f"Sending DMs to all users")
    await ctx.send(f"Sending DM to Tournament Organizer")
    

###Update a tournament



##########################################
# Menu Option with responses
# https://gist.github.com/lykn/a2b68cb790d6dad8ecff75b2aa450f23
#
##########################################


###Drop a player

###Add a player?

###Fix a result
# The result update should be sent to each player (somehow?)

###Progress to new round
# Information should be sent to each player in a DM, like their pairing, links to stuff, etc
# Post should also be made in the proper channel for the round progression

###Display current round

###Display Current Standings

@bot.command(aliases=['information', 'fancontent', 'fancontentpolicy', 'license'])
async def info(ctx):
    await ctx.send(content=f"MTG Tournament Helper Bot {version}\n\nBot to help with the management of swiss style tournaments.\nThis bot monitors the Channels and Direct Messages that it is a part of, and will log and store messages in those Channels and Direct Messages for diagnostic, analysis and usage purposes.\nThis bot also stores various information about the users that send messages in such Channels or Direct Messages.  This information is (non-exhaustive list) Discord User Name, Discord User ID, Discord Guild Roles, Deck Lists User has submitted, Tournaments and Tournament Data for tournaments that the User has particiapted in.\n\nDeck list submissions will eventually be validated against (for legality at submission time) and posted to Moxfield.\n\nThis bot has been programmed to hit the Moxfield.com API at various commands or interactions.  The Moxfield API is not a publicly facing API and permission is required to make use of it https://www.moxfield.com/help/faq#moxfield-api.  This specific program will be (has been) coded to be rate-limited against Moxfield's API such that there is no more than approximetly one (1) request from it per second.\n\nUse of this code that hits the Moxfield API or knowledge of the Moxfield API from viewing this code and executing against Moxfield's API is AT YOUR OWN RISK.\n\nThis MTG Tournament Helper Bot is not affiliated with, endorsed, or sponsored by Moxfield LLC\n\nThis MTG Tournament Helper Bot is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.  https://company.wizards.com/en/legal/fancontentpolicy\n\nSource Code is released under the MIT License https://github.com/tyraziel/MTG-Tournament-Helper-Discord-Bot/ -- 2024", suppress_embeds=True)
    #Maybe add something about the data that's being stored, Discord User Name, Discord ID, Messages sent, Tournaments parcicipated in.

bot.run(bot_env['BOT_TOKEN'])