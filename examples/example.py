# -*- coding: UTF-8 -*-
from discord_db.discord_db import *
import os

null = None
false = False
true = True

cwd = os.getcwd()

token = os.path.join(cwd, "token.txt")
tokens_file = open(token, "r")
token = tokens_file.read().strip()
tokens_file.close()

cntrl = login(token)
database = cntrl.access_databases()[0]
for cluster in database.access_clusters():
    for tbl in cluster.access_tables():
            print(tbl.read(5))
