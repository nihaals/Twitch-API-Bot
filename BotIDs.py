import json

with open("settings.json") as fp:
    settings = json.load(fp)

try:
    clientID = settings["clientID"]
    token = settings["token"]
    ownerID = int(settings["ownerID"])
    prefixes = settings["prefix"]
except:
    print("Check your settings.json")
    exit()

dev_id = 150750980097441792
dev_name = "Orangutan#9393"

permissionsURL = "2146958847"  # https://finitereality.github.io/permissions/
OAuth2 = "https://discordapp.com/oauth2/authorize?permissions={}&scope=bot&client_id={}".format(permissionsURL,
                                                                                                clientID)
URL = OAuth2
