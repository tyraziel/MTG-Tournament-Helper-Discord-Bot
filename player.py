import requests
import urllib.parse
import json
import time

class Player:
    player_data = {}
    discord_id = 0
    discord_name = ""
    dm_channel_id = 0
    dm_preference = False
    need_to_write_to_file = True

    def __init__(self):
        discord_id = 0
        discord_name = ""
        dm_channel_id = 0
        dm_preference = False
        need_to_write_to_file = True

    def writeToFile(self):
        the_json = self.toJSON()
        # with open("tournament.json") as outfile:
        #     outfile.write(the_json)

    def toJSON(self):
        return json.dumps({"discord_id": self.discord_id, "discord_name": self.discord_name, "dm_channel_id": self.dm_channel_id, "dm_preference": self.dm_preference})

    def __str__(self):
        return f"""Player Data - 
Player Discord Name:  {discord_name}
Player Discord ID:    {discord_id}
Player DM Channel ID: {dm_channel_id}
Player DM Preference: {dm_preference}
Need to Write to File: {need_to_write_to_file}"""

    # @static
    # def loadFromFile(filename : str):
    #     with open(filename, 'r') as the_file:
    #         the_object = json.load(the_file)
    #     return Tournament()