from datetime import datetime, timedelta
import numpy as np
import pyexchanges
import pytime
import pyapi
import re
import os

import random
import discord
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

class Stonks:
    def __init__(self):
        self.requestInfo = dict()
        self.Exchanges = pyexchanges.Exchanges()
        self.Time = pytime.Time()
        self.API = pyapi.API()

    def parse(self, sentence):
        self.reset()
        words = [z.lower() for z in re.split('[^a-zA-Z0-9-]', sentence) if len(z) > 0]
        # print(words)
        for c,w in enumerate(words):
            # Checking Realtime general price
            if w in ['price']:
                self.requestInfo['price'] = True
            
            # obtain ticker(s)
            if w.upper() in self.Exchanges.getSupportedTickers():
                self.requestInfo['tickList'].append(w.upper())

            # Historical price
            if '-' in w and "price" in words and ''.join(w.split('-')).isdigit():
                self.requestInfo['date'] = w.strip(' -') + " 00:00:00"

            # Profile
            if w in ['profile']:
                self.requestInfo['profile'] = True

            # Gainer
            if w in ['gainers','gainer', 'gain', 'gains']:
                if c < len(words)-1 and words[c+1].isdigit():
                    self.requestInfo['priceLimit'] = words[c+1]
                self.requestInfo['gainer'] = True

            # Active
            if w in ['popular', 'active', 'hot', 'actives']:
                if c < len(words)-1 and words[c+1].isdigit():
                    self.requestInfo['priceLimit'] = words[c+1]
                self.requestInfo['active'] = True

            # Loser
            if w in ['losers','loser', 'lose']:
                if c < len(words)-1 and words[c+1].isdigit():
                    self.requestInfo['priceLimit'] = words[c+1]
                self.requestInfo['loser'] = True

            # Sector
            if w in ['sectors','sector']:
                self.requestInfo['sector'] = True

            # Market Hours, Holidays
            mkthrs = False
            for first,second in zip(words,words[1:]):
                if first == 'market' and second in ['hour', 'hours', 'close', 'open']:
                    mkthrs = True
            if mkthrs or w in ['holiday', 'holidays','market-hours', 'market-hour', 'times', 'time', 'market-open', 'market-close']:
                self.requestInfo['mrkthours'] = True

            # News
            if w in ['news']:
                self.requestInfo['news'] = True

            # Rating
            if w in ['rating', 'rate']:
                self.requestInfo['rating'] = True

            # Screener
            if w in ['screener', 'screen']:
                self.requestInfo['screener'] = True
            
        if self.requestInfo['screener']:
            for c,w in enumerate(words):
                if c < len(words)-1:
                    if w == 'marketcapmorethan':
                        self.requestInfo['screenerVar']['marketCapMoreThan'] = words[c+1]
                    elif w == 'marketcaplessthan':
                        self.requestInfo['screenerVar']['marketCapLessThan'] = words[c+1]
                    elif w == 'betamorethan':
                        self.requestInfo['screenerVar']['betaMoreThan'] = words[c+1]
                    elif w == 'betalessthan':
                        self.requestInfo['screenerVar']['betaLessThan'] = words[c+1]
                    elif w == 'volumemorethan':
                        self.requestInfo['screenerVar']['volumeMoreThan'] = words[c+1]
                    elif w == 'volumelessthan':
                        self.requestInfo['screenerVar']['volumeLessThan'] = words[c+1]
                    elif w == 'dividendmorethan':
                        self.requestInfo['screenerVar']['dividendMoreThan'] = words[c+1]
                    elif w == 'dividendlessthan':
                        self.requestInfo['screenerVar']['dividendLessThan'] = words[c+1]
                    elif w == 'sector':
                        self.requestInfo['screenerVar']['sector'] = words[c+1]
                    elif w == 'limit':
                        self.requestInfo['screenerVar']['limit'] = words[c+1]
                    elif w == 'price':
                        self.requestInfo['screenerVar']['price'] = words[c+1]

    def reply(self):
        results = []
        # Historical vs Realtime
        if self.requestInfo['price'] and self.requestInfo['date']:
            for tick in self.requestInfo['tickList']:
                curInfo = self.API.getHistorical(tick, 'close', self.requestInfo['date'])
                results.append((tick,)+curInfo)
        elif self.requestInfo['price']:
            for tick in self.requestInfo['tickList']:
                curInfo = self.API.getRealtime(tick)
                results.append(curInfo)
        # Profile
        if self.requestInfo['profile']:
            for tick in self.requestInfo['tickList']:
                curInfo = self.API.getProfile(tick)
                results.append(curInfo)
        # Gainer
        if self.requestInfo['gainer']:
            curInfo = self.API.mostGainer()
            results.append(curInfo)
        # Active
        if self.requestInfo['active']:
            curInfo = self.API.mostActive()
            results.append(curInfo)
        # Loser
        if self.requestInfo['loser']:
            curInfo = self.API.mostLoser()
            results.append(curInfo)
        # Sector
        if self.requestInfo['sector']:
            curInfo = self.API.getSector()
            results.append(curInfo)
        # MarketHours
        if self.requestInfo['mrkthours']:
            curInfo = self.API.getMarketHours()
            results.append(curInfo)
        # News
        if self.requestInfo['news']:
            curInfo = self.API.getNews(','.join(self.requestInfo['tickList']))
            results.append(curInfo)
        # Rating
        if self.requestInfo['rating']:
            for tick in self.requestInfo['tickList']:
                curInfo = self.API.getRating(tick)
                results.append(curInfo)
        # Screener
        if self.requestInfo['screener']:
            curInfo = self.API.getScreener(self.requestInfo['screenerVar'])
            results.append(curInfo)
        return results

    def reset(self):
        self.requestInfo.clear()
        self.requestInfo['date'] = None
        self.requestInfo['price'] = None
        self.requestInfo['profile'] = None
        self.requestInfo['gainer'] = None
        self.requestInfo['active'] = None
        self.requestInfo['loser'] = None
        self.requestInfo['sector'] = None
        self.requestInfo['priceLimit'] = None
        self.requestInfo['mrkthours'] = None
        self.requestInfo['news'] = None
        self.requestInfo['rating'] = None
        self.requestInfo['screener'] = None
        self.requestInfo['screenerVar'] = dict()
        self.requestInfo['tickList'] = []
    
    def getRequest(self):
        return self.requestInfo

    def getSupportedNames(self):
        return self.Exchanges.getSupportedNames()
    
    def getTime(self):
        return self.Time

def discordInit(stonks, token):
    DISCORD_TOKEN = token
    client = discord.Client()
    time = stonks.getTime()
    tickerNames = stonks.getSupportedNames()

    @client.event
    async def on_ready():
        print(f'{client.user.name} has connected to Discord!')
        # # Setting `Playing ` status
        # await client.change_presence(activity=discord.Game(name="testing"))

        # # Setting `Streaming ` status
        # await client.change_presence(activity=discord.Streaming(name="My Stream", url=my_twitch_url))

        # # Setting `Listening ` status
        # await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="a song"))

        # Setting `Watching ` status
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="'-help'"))

    @client.event
    async def on_member_join(member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member.name}, welcome to the jungle ;)'
        )

    @client.event
    async def on_message(message):
        if message.author == client.user or not message.content:
            return

        command = message.content[0]
        request = message.content[1:]

        if command != '-':
            return

        embedVar = discord.Embed(color=0x00ff00)

        if 'help' in request:
            rep = helpTemplate(request)
            for k,v in rep.items():
                embedVar.add_field(name=k, value=v, inline=True)
            await message.channel.send(embed=embedVar)
            return
        
        stonks.parse(request)
        requestInfo = stonks.getRequest()        
        replies = stonks.reply()

        # Historical
        if requestInfo['price'] and requestInfo['date'] and not requestInfo['screener']:
            ret = priceTemplate(replies, requestInfo)
            requestType = "Historical"
        # Realtime
        elif requestInfo['price'] and not requestInfo['screener']:
            ret = priceTemplate(replies, requestInfo)
            requestType = "Realtime"
        # Profile
        elif requestInfo['profile']:
            ret = profileTemplate(replies, requestInfo)
            requestType = "Profile"
        # Gainer #top 15
        elif requestInfo['gainer']:
            ret = mostTemplate(replies, requestInfo)
            requestType = "Gainer"
        # Active #top 15
        elif requestInfo['active']:
            ret = mostTemplate(replies, requestInfo)
            requestType = "Active"
        # Loser #top 15
        elif requestInfo['loser']:
            ret = mostTemplate(replies, requestInfo)
            requestType = "Loser"
        # Hot Sectors
        elif requestInfo['sector'] and not requestInfo['screener']:
            ret = sectorTemplate(replies)
            requestType = "Sector"
        # MarketHours
        elif requestInfo['mrkthours']:
            ret = mrkthrsTemplate(replies)
            requestType = "Market Hours"
        # News
        elif requestInfo['news']:
            ret = newsTemplate(replies)
            requestType = "News"
        # Rating
        elif requestInfo['rating']:
            ret = ratingTemplate(replies)
            requestType = "Rating"
        # Screener
        elif requestInfo['screener']:
            ret = screenerTemplate(replies)
            

        if any([True for i in requestInfo.values() if isinstance(i, (int, float)) and i == True]):
            if type(ret) == str:
                print(requestType)
                await message.channel.send(ret)
            else:
                embedVar.add_field(name=requestType, value=''.join(ret), inline=False)
                await message.channel.send(embed=embedVar)

        if request != 'help' and len(replies) == 0:
            await message.channel.send('Unsupported command')

    def helpTemplate(request):
        rep = dict()
        req = request.split()
        if len(req) > 1:
            if req[1] == 'price':
                rep['Price'] = '-price <ticker(s)>\n-price <ticker(s)> <date YYYY-MM-DD>\ne.g. -price amc tsla 2020-01-01'
            elif req[1] == 'profile':
                rep['Profile'] = '-profile <ticker(s)>\ne.g. -profile amc tsla'
            elif req[1] == 'gainer':
                rep['Top Gainer'] = '-gainer <price limit>\ne.g. -gainer 100'
            elif req[1] == 'active':
                rep['Most Active'] = '-active <price limit>\ne.g. -active 100'
            elif req[1] == 'loser':
                rep['Top Loser'] = '-loser <price limit>\ne.g. -loser 100'
            elif req[1] == 'sector':
                rep['Hot Sector'] = '-sector\ne.g. -sector'
            elif req[1] == 'market-hours' or req[1] == 'holiday':
                rep['Market hours'] = '-market hours\ne.g. -market hours'
            elif req[1] == 'news':
                rep['News'] = '-news <ticker(s)>\ne.g. -news amc tsla'
            elif req[1] == 'rating':
                rep['Rating'] = '-rating <ticker(s)>\ne.g. -rating amc tsla'
            elif req[1] == 'screener':
                parameters= ['marketCapMoreThan','marketCapLessThan','betaMoreThan','betaLessThan','volumeMoreThan','volumeLessThan','dividendMoreThan','dividendLessThan','sector','price','limit']
                rep['Screener'] = '-screener <parameters>\ne.g. -screener price 100, volumeMoreThan 50000'
                rep['Parameters'] = '\n'.join(parameters)
        else:
            rep['Supported Commands'] = '-help <command>\nprice\nprofile\ngainer\nactive\nloser\nsector\nmarket-hours\nnews\nrating\nscreener'
        return rep

    def mostTemplate(replies, requestInfo):
        try:
            rep = ['```{: <12} {: <12} {: <12}\n```'.format('Ticker', 'Price', 'Change %')]
            for reply in replies:
                if type(reply) != list:
                    return 'Unsupported command'
                for c,tick in enumerate(reply):
                    if type(tick) != dict or not all(option in tick for option in ['ticker','price','changesPercentage']):
                        return 'Unsupported command'
                    if requestInfo['priceLimit'] and float(requestInfo['priceLimit']) < float(tick['price']):
                        continue
                    r = '```{}: {: <12} {:<12} {: <12}\n```'.format(c+1, tick['ticker'],"{:.2f}".format(float(tick['price'])), tick['changesPercentage'].strip('()'))
                    curLen = sum([len(i) for i in rep])
                    if curLen > 1023 or curLen + len(r) > 1023:
                        break
                    rep.append(r)
            if len(rep) == 1:
                return 'No results found'
            return rep
        except:
            return 'Unsupported command'

    def priceTemplate(replies, requestInfo):
        try:
            rep = []
            for c,reply in enumerate(replies):
                if (type(reply) not in [tuple, dict] or (type(reply) == tuple and len(reply) != 3)  or (type(reply) == dict and not all(option in reply for option in ['symbol','price','volume','date'])) ):
                    return 'Unsupported command'
                if type(reply) == dict:
                    rep.append("{}\nPrice:\t{}\nVolume:\t{}\nDate: {}\n".format(reply['symbol'], reply['price'],reply['volume'],reply['date']))
                else:
                    rep.append("{}\nPrice:\t{}\nDate:\t{}\n".format(reply[0],reply[1], reply[2]))
            if len(rep) == 0:
                return 'No results found'
            return rep
        except: 
            return 'Unsupported command'

    def profileTemplate(replies, requestInfo):
        try:
            rep = []
            for c,reply in enumerate(replies):
                if type(reply) != dict or 'description' not in reply.keys():
                    return 'Unsupported command'
                des = reply['description'][:1020]
                if len(reply['description']) > 1020:
                    des += '...'
                rep.append(des)
            if len(rep) == 0:
                return 'No results found'
            return rep
        except:
            return 'Unsupported command'

    def newsTemplate(replies):
        try:
            rep = []
            for reply in replies:
                for c,article in enumerate(reply):
                    r = '''**{}**\n**Published**: {}\n**Title**: {}\n**Text**: {}\n**URL**: {}\n\n'''.format(article['site'],article['publishedDate'][:16],article['title'][:35] + '...',article['text'][:200]+'...',article['url'])
                    curLen = sum([len(i) for i in rep])
                    if curLen >1023 or curLen + len(r) > 1023:
                        break
                    rep.append(r)
            if len(rep) == 0:
                return 'No results found'
            return rep
        except:
            return 'Unsupported command'

    def sectorTemplate(replies):
        try:
            rep = ['```Parameters\n{: <35} {: <35}\n```'.format('Sector', 'Change %')]
            for reply in replies:
                if type(reply[0]) != dict or not all(option in reply[0] for option in ['changesPercentage','sector']):
                    return 'Unsupported command'

                reply = sorted(reply, key = lambda i: float(i['changesPercentage'].strip('%')),reverse = True)
                rep.append('```**UP SECTORS**\n```'.format())
                for sec in reply[:5]:
                    rep.append('```{: <35} {: <35}\n```'.format(sec['sector'], sec['changesPercentage']))

                rep.append('```**DOWN SECTORS**\n```'.format())
                for c,sec in enumerate(reply[len(reply)-5 :][::-1]):
                    rep.append('```{: <35} {: <35}\n```'.format(sec['sector'], sec['changesPercentage']))
            if len(rep) == 1:
                return 'No Results found'
            return rep
        except:
            return 'Unsupported command'
    
    def ratingTemplate(replies):
        try:
            rep = []
            for reply in replies:
                for rate in reply:
                    if type(rate) != dict or not all(option in rate for option in ['symbol','date','rating']):
                        return 'Unsupported command'
                    scores = [i for i in rate.values() if str(i).isdigit()]
                    avg = round(sum(scores)/len(scores),2)
                    rep.append('{}\nRating: {}\nAvg. Score: {}/5\nDate: {}\n'.format(rate['symbol'],rate['rating'],avg, rate['date']))
            if len(rep) == 0:
                return 'No results found'
            return rep
        except:
            return 'Unsupported command'

    def screenerTemplate(replies):
        rep = ['```Parameters\n{: <12} {: <12} {: <12} {: <12}\n```'.format("Symbol","MarketCap","Price","Volume")]
        for reply in replies:
            for c,ticker in enumerate(reply[:15]):
                rep.append('```{}: {: <12} {: <12} {: <12} {: <12}\n```'.format(c+1,ticker['symbol'],num2Word(ticker['marketCap']),ticker['price'],num2Word(ticker['volume'])))
        if len(rep) == 1:
            return 'No results found'
        return rep

    def mrkthrsTemplate(replies):
        try:
            today = time.getCurrentDate()
            y,m,d = (today.split(" ")[0]).split("-")

            completed = time.busDays(y+ '-01-01 00:00:00', today)
            left = time.busDays(y+ '-01-01 00:00:00', y + '-12-31 00:00:00') - completed
            
            rep = []
            for reply in replies:
                if type(reply) != dict or not all(option in reply for option in ['stockExchangeName','stockMarketHours','stockMarketHolidays']):
                    return 'Unsupported command'
                rep.append('Year:{}\n{}\nOpens: {}\nCloses: {}\n'.format(y,reply['stockExchangeName'], reply['stockMarketHours']['openingHour'], reply['stockMarketHours']['closingHour']))
                for year in reply['stockMarketHolidays']:
                    if str(year['year']) != str(y):
                        continue
                    for k,v in year.items():
                        if k != 'year':
                            rep += '```{:<12}\n{:<12}\n```'.format(k , v)
                            vy, _, _ = v.split("-")
                            if str(vy) == str(y):
                                if time.timeDiff(v + " 00:00:00",today).days < 0:
                                    left -=1
            rep.append('Trading Days Left: {}'.format(left))
            if len(rep) == 0:
                return 'No results found'
            return rep
        except:
            return 'Unsupported command'

    def num2Word(num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:.2f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
    
    client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    stonks = Stonks()
    discordInit(stonks,DISCORD_TOKEN)


    