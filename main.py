import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import bleach
import re
import discord
from discord.ext import commands
import vars
from table2ascii import table2ascii as t2a, PresetStyle

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='*', intents=intents)

def main():
    getReport()

def getReport():
    # Get the total list of reports for guild
    url = "https://www.warcraftlogs.com/guild/reports-list/641248"
    page = requests.get(url)

    reports = BeautifulSoup(page.content, "html.parser")

    #Get the top most report for the guild
    for tr in reports.find_all('tr'):
        td = tr.find('td')
        if td:
            a = td.find('a')
            break

    # Do some gamer splitting to get full report url
    baseLink = str(a).split("=\"")
    splitLink = baseLink[1].split("\">")


    # The reports page has some whack JS that generates the parse listings so fake a browser and wait
    newUrl = "https://www.warcraftlogs.com" + str(splitLink[0] + "#view=rankings&boss=-2&difficulty=0&wipes=2&playermetric=dps&playermetriccompare=rankings")
    browser = webdriver.ChromiumEdge()
    browser.get(newUrl)
    time.sleep(2)
    html = browser.page_source
    thisLog = BeautifulSoup(html, "html.parser")

    # Get the bit of the page that has the dps, tanks and healer parses
    logTable = thisLog.find("div", {"class": "report-rankings-tab-content"})
    #print(logTable)

    #dpsTable = BeautifulSoup(logTable, "html.parser")

    # spilt out the dps table
    dpsLog = logTable.find("table")
    rows=list()
    for row in dpsLog.find_all("tr"):
        rows.append(row)

    # Bosses are included in the dps table as the first element so split it out
    bosses = rows[0]
    # Bleach that nasty HTML out of there
    cleanBosses = bleach.clean(str(bosses),strip=True)
    filteredBosses = cleanBosses.split("\n")
    bossList = []
    for boss in filteredBosses:
        if boss != '':
            bossList.append(boss)
    bossNames = []
    for boss in bossList:
        boss = re.sub(r'[^a-zA-Z]',"", boss)
        bossNames.append(boss)

    players=list()
    for r in rows[1:]:
        cleanPlayer = bleach.clean(str(r),strip=True)
        cleanPlayer = cleanPlayer.split("\n")
        for c in cleanPlayer:
            if c == '':
                cleanPlayer.remove(c)
        players.append(cleanPlayer)
    
    for pl in players:
        pl.pop()
    
    return bossNames, players

@bot.command()
async def on_ready():
    print('Running...')

@bot.command()
async def runReport(ctx):
    test = getReport()
    output = t2a(
        header = test[0],
        body = test[1],
        style = PresetStyle.thin_compact
    )
    print(f"```\n{output}\n```")
    await ctx.send("done")

bot.run(vars.TOKEN)