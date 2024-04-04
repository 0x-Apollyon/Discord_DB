# -*- coding: UTF-8 -*-
import requests
import json

null = None
false = False
true = True

discord_api_version = 9
discord_api_base_url = f"https://discord.com/api/v{discord_api_version}"


class Table:
    def __init__(self, cluster , id , name):
        self.cluster = cluster
        self.id = id
        self.name = name


    def __str__(self):
        return f"Discord_DB Table: {self.name}"

    def delete(self):

        bot_token = self.cluster.database.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        r = requests.delete(f"{discord_api_base_url}/channels/{self.id}", headers=headers)

    def write(self , data):

        if len(data) > 2000 or len(data) < 1:
            raise Exception("Data length must be between 1 and 2000 characters") 
        bot_token = self.cluster.database.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}
        payload = {"mobile_network_type":"unknown","content":data,"tts":false,"flags":0}
        r = requests.post(f"{discord_api_base_url}/channels/{self.id}/messages" , headers = headers , json=payload)
        if r.status_code == 200:
            return "Data written"
        elif r.status_code == 404:
            raise Exception("Table not found") 
        elif r.status_code == 429:
            raise Exception("Controller/IP ratelimited") 
        elif r.status_code == 500:
            raise Exception("Discord server error") 

    def read(self , count):

        bot_token = self.cluster.database.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        reading_chunks = []
        hundred_chunks = count//100
        remaining_chunks = count%100
        
        for i in range(hundred_chunks):
            reading_chunks.append(100)
        reading_chunks.append(remaining_chunks)

        return_content = []
        for i , chunk in enumerate(reading_chunks):
            if i == 0:
                r = requests.get(f"{discord_api_base_url}/channels/{self.id}/messages?limit={chunk}" , headers=headers)
                tables_contents = eval(r.text)
                valuable_messages = []
                for msg in tables_contents:
                    if msg["author"]["id"] == self.cluster.database.controller.id:
                        valuable_messages.append(msg)

                last_id =  valuable_messages[-1]["id"]

                for msg in valuable_messages:
                    cnt = msg["content"]
                    return_content.append(cnt)
            else:
                r = requests.get(f"{discord_api_base_url}/channels/{self.id}/messages?limit={chunk}&before={last_id}" , headers=headers)
                tables_contents = eval(r.text)
                valuable_messages = []
                for msg in tables_contents:
                    if msg["author"]["id"] == self.cluster.database.controller.id:
                        valuable_messages.append(msg)

                last_id =  valuable_messages[-1]["id"]

                for msg in valuable_messages:
                    cnt = msg["content"]
                    return_content.append(cnt)

        return return_content





    


class Cluster:
    def __init__(self, database , id , name):
        self.database = database
        self.id = id
        self.name = name

    def __str__(self):
        return f"Discord_DB Cluster: {self.name}"

    def access_tables(self):

        bot_token = self.database.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        r = requests.get(f"{discord_api_base_url}/guilds/{self.database.id}/channels", headers=headers)
        guild_channels = eval(r.text)
        tables = []
        for channel in guild_channels:
            if channel["parent_id"] == self.id:
                tbl = Table(self , channel["id"] , channel["name"])
                tables.append(tbl)

        return tables

    def delete(self):

        bot_token = self.database.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        r = requests.get(f"{discord_api_base_url}/guilds/{self.database.id}/channels", headers=headers)
        guild_channels = eval(r.text)
        for channel in guild_channels:
            if channel["parent_id"] == self.id:
                channel_id = channel["id"]
                r = requests.delete(f"{discord_api_base_url}/channels/{channel_id}", headers=headers)
        r = requests.delete(f"{discord_api_base_url}/channels/{self.id}", headers=headers)

    def purge(self):

        bot_token = self.database.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        r = requests.get(f"{discord_api_base_url}/guilds/{self.database.id}/channels", headers=headers)
        guild_channels = eval(r.text)
        for channel in guild_channels:
            if channel["parent_id"] == self.id:
                channel_id = channel["id"]
                r = requests.delete(f"{discord_api_base_url}/channels/{channel_id}", headers=headers)

    

class Database:
    def __init__(self, controller , id , name):
        self.controller = controller
        self.id = id
        self.name = name

    def __str__(self):
        return f"Discord_DB Database: {self.name}"

    def access_clusters(self):

        bot_token = self.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}
        r = requests.get(f"{discord_api_base_url}/guilds/{self.id}/channels", headers=headers)
        guild_channels = eval(r.text)
        clusters = []
        if r.status_code == 200:
            for channel in guild_channels:
                if channel["parent_id"] == None:
                    clstr = Cluster(self , channel["id"] , channel["name"])
                    clusters.append(clstr)

            return clusters
        elif r.status_code == 401:
            raise Exception("Database access error") 
        elif r.status_code == 429:
            raise Exception("Controller or IP ratelimited") 

    def purge(self):

        bot_token = self.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        r = requests.get(f"{discord_api_base_url}/guilds/{self.id}/channels", headers=headers)
        guild_channels = eval(r.text)

        for channel in guild_channels:
            channel_id = channel["id"]
            r = requests.delete(f"{discord_api_base_url}/channels/{channel_id}", headers=headers)

    def rename_db(self , new_name):

        if len(new_name) < 3 or len(new_name) > 100:
            raise Exception("The length of DB name must be between 3 and 100 characters") 
        
        bot_token = self.controller.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        data = {"name":new_name ,
                "description":null,
                "icon":null,
                "splash":null,
                "banner":null,
                "home_header":null,
                "afk_channel_id":null,
                "afk_timeout":300,
                "system_channel_id":null,
                "verification_level":0,
                "default_message_notifications":0,
                "explicit_content_filter":0,
                "system_channel_flags":0,
                "public_updates_channel_id":null,
                "safety_alerts_channel_id":null,
                "premium_progress_bar_enabled":false}

        r = requests.patch(f"https://discord.com/api/v9/guilds/{self.id}" ,headers = headers , json = data)

    
class Controller:
    def __init__(self, token , id , name):
        self.token = token
        self.id = id
        self.name = name

    def __str__(self):
        return f"Discord_DB Controller: {self.name}"

    def access_databases(self):

        bot_token = self.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        r = requests.get(f"{discord_api_base_url}/users/@me/guilds", headers=headers)
        guilds_array = eval(r.text)
        databases = []
        for guild in guilds_array:
            if guild["permissions"] == "562949953421311":
                guild_id = guild["id"]

                r = requests.get(f"{discord_api_base_url}/guilds/{guild_id}", headers=headers)
                guild_info = eval(r.text)
                db_obj = Database(self , guild_info["id"] , guild_info["name"])
                databases.append(db_obj)

        return databases

    def purge(self):

        bot_token = self.token
        headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

        r = requests.get(f"{discord_api_base_url}/users/@me/guilds", headers=headers)
        return_arr = []
        guilds_array = eval(r.text)
        for guild in guilds_array:
            if guild["permissions"] == "562949953421311":
                guild_id = guild["id"]

            r = requests.get(f"{discord_api_base_url}/guilds/{guild_id}/channels", headers=headers)
            guild_channels = eval(r.text)

            for channel in guild_channels:
                channel_id = channel["id"]
                r = requests.delete(f"{discord_api_base_url}/channels/{channel_id}", headers=headers)



def login(token):

    bot_token = "Bot " + token
    headers = {"Authorization": bot_token , 'Content-type': 'application/json'}

    r = requests.get(f"{discord_api_base_url}/users/@me", headers=headers)
    if r.status_code != 200:
        raise Exception("Invalid bot token provided. Please check") 
    else:
        
        bot_info_json = eval(r.text)
        controller = Controller(bot_token , bot_info_json["id"] , bot_info_json["username"])

        return controller






    




