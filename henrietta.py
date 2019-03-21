import os
import re
import json
import discord
import argparse
import urllib.parse


DISCORD_TOKEN = "SECRET"

PROJECT_URL_EU4 = 'https://paratranz.cn/projects/76/strings?mode=4&key='
PROJECT_URL_CK2 = 'https://paratranz.cn/projects/91/strings?mode=4&key='

DEFAULT_SEARCH_NUM = 1

paradic = {}
client  = discord.Client()


# Startup
@client.event
async def on_ready():
    print('Logged in as ' + client.user.name)
    print('')


# Response
@client.event
async def on_message(message):

    messages = message.content.split('\n')

    if client.user != message.author:
        for mes in messages:

            # Search for Key
            command = re.match(regex_key, mes)
            if command:
                key = re.sub(command.group(1), '', mes)
                print('Search for key ' + key)
                result = paradic.get(key)
                if not result:
                    found = False
                    for index in range(10):
                        newkey = key  + ':' + str(index)
                        print('Search again for ' + newkey)
                        newresult = paradic.get(newkey)
                        if newresult:
                            found = True
                            out = urlbase + urllib.parse.quote(newkey) + '\n'
                            out = out + '```' + newresult[0] + '```'
                            out = out + '```' + newresult[1] + '```'
                            break
                    if found:
                        await message.channel.send(out)
                    else:
                        await message.channel.send('そのキーは存在しません')
                else:
                    out = urlbase + urllib.parse.quote(key) + '\n'
                    out = out + '```' + result[0] + '```'
                    out = out + '```' + result[1] + '```'
                    await message.channel.send(out)

            # Search for Text
            else:
                command = re.match(regex_text, mes)
                if command:
                    text = re.sub(command.group(1), '', mes)
                    result = re.match(r'^(([0-9]+)\s+)[^\s]', text)
                    if result:
                        num = int(result.group(2))
                        text = re.sub(result.group(1), '', text)
                    else:
                        num = DEFAULT_SEARCH_NUM
                    print('Search for text ' + text)
                    results = []
                    for key in paradic:
                        entry = paradic.get(key)
                        hit = re.search(text, entry[0])
                        if hit:
                            results.append([len(entry[0]), key, entry[0], entry[1]])
                        else:
                            hit = re.search(text, entry[1])
                            if hit:
                                results.append([len(entry[1]), key, entry[0], entry[1]])
                    if len(results) == 0:
                        await message.channel.send('該当するエントリは存在しません')
                    else:
                        results.sort()
                        count = 0
                        for entry in results:
                            count = count + 1
                            out = urlbase + urllib.parse.quote(entry[1]) + '\n'
                            out = out + '```' + entry[2] + '```'
                            out = out + '```' + entry[3] + '```'
                            await message.channel.send(out)
                            if count >= num:
                                break


# Parse Command Line Options
parser = argparse.ArgumentParser()
parser.add_argument('input', help = 'input folder')
parser.add_argument('game' , help = 'eu4 or ck2')
args = parser.parse_args()

# Set Game Specific Values
if args.game == 'eu4':
    regex_key  = r'^(!eu4k(ey)?\s+)[^\s]'
    regex_text = r'^(!eu4t(ext)?\s+)[^\s]'
    urlbase    = PROJECT_URL_EU4
if args.game == 'ck2':
    regex_key  = r'^(!ck2k(ey)?\s+)[^\s]'
    regex_text = r'^(!ck2t(ext)?\s+)[^\s]'
    urlbase    = PROJECT_URL_CK2

# Create Dictionary
found = []
for root, dirs, files in os.walk(args.input):
    for filename in files:
        found.append(os.path.join(root, filename))
for path in found:
    file   = os.path.basename(path)
    folder = os.path.dirname (path)
    name, ext = os.path.splitext(file)
    if ext == '.json':
        jsonfile = open(path, 'r', encoding = 'UTF-8')
        print('Processing ' + file + '...')
        jsonstr  = jsonfile.read()
        jsondata = json.loads(jsonstr)
        for entry in jsondata:
            paradic[entry.get('key')] = [entry.get('original'), entry.get('translation')]
        jsonfile.close()

# Run Bot
client.run(DISCORD_TOKEN)
