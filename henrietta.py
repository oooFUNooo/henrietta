import re
import io
import json
import zipfile
import discord
import requests
import argparse
import urllib.parse
from threading import Thread


PROJECT_EU4     = '76'
PROJECT_CK2     = '91'
PROJECT_PREFIX  = 'https://paratranz.cn/projects/'
PROJECT_POSTFIX = '/strings?mode=4&key='
ZIPFILE_PREFIX  = 'https://paratranz.cn/api/projects/'
ZIPFILE_POSTFIX = '/artifacts/download'
PARATRANZ_EU4   = PROJECT_PREFIX + PROJECT_EU4 + PROJECT_POSTFIX
PARATRANZ_CK2   = PROJECT_PREFIX + PROJECT_CK2 + PROJECT_POSTFIX

DEFAULT_SEARCH_NUM = 1

client = discord.Client()
eu4dic = {}
ck2dic = {}


# Startup
@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + '\n')


# Response
@client.event
async def on_message(message):

    messages = message.content.split('\n')

    if client.user != message.author:
        for mes in messages:

            # Search for EU4 Key
            command = re.match(r'^(!eu4k(ey)?\s+)[^\s]', mes)
            if command:
                key = re.sub(command.group(1), '', mes)
                print('Search for key ' + key)
                result = eu4dic.get(key)
                if not result:
                    found = False
                    for index in range(10):
                        newkey = key  + ':' + str(index)
                        print('Search again for ' + newkey)
                        newresult = eu4dic.get(newkey)
                        if newresult:
                            found = True
                            out = PARATRANZ_EU4 + urllib.parse.quote(newkey) + '\n'
                            out = out + '```' + newresult[0] + '```'
                            out = out + '```' + newresult[1] + '```'
                            break
                    if found:
                        await message.channel.send(out)
                    else:
                        await message.channel.send('そのキーは存在しません')
                else:
                    out = PARATRANZ_EU4 + urllib.parse.quote(key) + '\n'
                    out = out + '```' + result[0] + '```'
                    out = out + '```' + result[1] + '```'
                    await message.channel.send(out)

            # Search for EU4 Text
            else:
                command = re.match(r'^(!eu4t(ext)?\s+)[^\s]', mes)
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
                    for key in eu4dic:
                        entry = eu4dic.get(key)
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
                            out = PARATRANZ_EU4 + urllib.parse.quote(entry[1]) + '\n'
                            out = out + '```' + entry[2] + '```'
                            out = out + '```' + entry[3] + '```'
                            await message.channel.send(out)
                            if count >= num:
                                break

            # Search for CK2 Key
            command = re.match(r'^(!ck2k(ey)?\s+)[^\s]', mes)
            if command:
                key = re.sub(command.group(1), '', mes)
                print('Search for key ' + key)
                result = ck2dic.get(key)
                if not result:
                    found = False
                    for index in range(10):
                        newkey = key  + ':' + str(index)
                        print('Search again for ' + newkey)
                        newresult = ck2dic.get(newkey)
                        if newresult:
                            found = True
                            out = PARATRANZ_CK2 + urllib.parse.quote(newkey) + '\n'
                            out = out + '```' + newresult[0] + '```'
                            out = out + '```' + newresult[1] + '```'
                            break
                    if found:
                        await message.channel.send(out)
                    else:
                        await message.channel.send('そのキーは存在しません')
                else:
                    out = PARATRANZ_CK2 + urllib.parse.quote(key) + '\n'
                    out = out + '```' + result[0] + '```'
                    out = out + '```' + result[1] + '```'
                    await message.channel.send(out)

            # Search for CK2 Text
            else:
                command = re.match(r'^(!ck2t(ext)?\s+)[^\s]', mes)
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
                    for key in ck2dic:
                        entry = ck2dic.get(key)
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
                            out = PARATRANZ_CK2 + urllib.parse.quote(entry[1]) + '\n'
                            out = out + '```' + entry[2] + '```'
                            out = out + '```' + entry[3] + '```'
                            await message.channel.send(out)
                            if count >= num:
                                break


def eu4init():

    # Create Dictionary
    headers = {
    	'Authorization': PARATRANZ_TOKEN,
    }
    r = requests.get(ZIPFILE_PREFIX + PROJECT_EU4 + ZIPFILE_POSTFIX, headers=headers)
    zf = zipfile.ZipFile(io.BytesIO(r.content), 'r')
    for fileinfo in zf.infolist():
        if re.search(r'\.json', fileinfo.filename):
            jsonstr  = zf.read(fileinfo).decode('UTF-8')
            jsondata = json.loads(jsonstr)
            for entry in jsondata:
                original    = entry.get('original')
                translation = entry.get('translation')
                if original == '':
                    original = '[EMPTY]'
                if translation == '':
                    translation = '[EMPTY]'
                eu4dic[entry.get('key')] = [original, translation]


def ck2init():

    # Create Dictionary
    headers = {
    	'Authorization': PARATRANZ_TOKEN,
    }
    r = requests.get(ZIPFILE_PREFIX + PROJECT_CK2 + ZIPFILE_POSTFIX, headers=headers)
    zf = zipfile.ZipFile(io.BytesIO(r.content), 'r')
    for fileinfo in zf.infolist():
        if re.search(r'\.json', fileinfo.filename):
            jsonstr  = zf.read(fileinfo).decode('UTF-8')
            jsondata = json.loads(jsonstr)
            for entry in jsondata:
                original    = entry.get('original')
                translation = entry.get('translation')
                if original == '':
                    original = '[EMPTY]'
                if translation == '':
                    translation = '[EMPTY]'
                ck2dic[entry.get('key')] = [original, translation]


if __name__ == "__main__":

    # Parse Command Line Options
    parser = argparse.ArgumentParser()
    parser.add_argument('discord_token'  , help='Discord Token')
    parser.add_argument('paratranz_token', help='ParaTranz Token')
    args = parser.parse_args()

    DISCORD_TOKEN   = args.discord_token
    PARATRANZ_TOKEN = args.paratranz_token

    thread1 = Thread(target=eu4init)
    thread2 = Thread(target=ck2init)

    thread1.start()
    thread2.start()

    # Run Bot
    client.run(DISCORD_TOKEN)
