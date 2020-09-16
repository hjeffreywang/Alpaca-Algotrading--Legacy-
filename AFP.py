#Version 3.0 EmaPulse 

#Dev time in Jupyter is over, this version of Alpaca Farm (paper) is meant
#to be ran on a remote Heroku server, and hence includes __main__ syntax
#and a function for determing the next market open date

###IMPORT BLOCK
import alpaca_trade_api as tradeapi
from config import *
#config contains API key variables KEY_ID and SECRET_KEY,
#as well as various URLS

import talib as ta
import talib.abstract as tab
#Library for easily calculating various stock indicators

import requests, time, os, copy, random, pickle
import datetime as dt
import pytz
import pandas as pd
import numpy as np



###GLOBAL VARIABLES
APIP = tradeapi.REST(KEY_ID,SECRET_KEY,PAPER_URL,api_version='v2')
DTzero = dt.datetime(1996,9,4)
TDPICKLE = 'APF3_Trader.pickle'
MARKETOPEN = dt.time(6,30)
BEFOREMARKETOPEN = dt.time(6,10)
ALMOSTMARKETOPEN = dt.time(6,50)
MARKETCLOSE = dt.time(13)
ALMOSTMARKETCLOSE = dt.time(12,50)
NYTZ = timezone = pytz.timezone("America/New_York")

###GLOBAL FUNCTIONS
def txt2List(txt):
    if txt.endswith('SYM.txt'):
        with open(txt) as f:
            return [l.strip("\n") for l in f.readlines()]
    else:
        print('txt is not a list of symbols!')
        
def LoadTD():
        with open(TDPICKLE,'rb') as f:
            return pickle.load(f)
def SaveTD(trader):
    with open(TDPICKLE,'wb') as f:
        pickle.dump(trader,f)

def getNextOpen():
    nextopen = APClock = APIP.get_clock().next_open
    return dt.datetime.combine(nextopen.date(),BEFOREMARKETOPEN)

###"DICTIONARY" CLASSES
class UAsset: #asset that the trader knows about, but isn't actively watching
    def __init__(self,sym,shortable):
        self.SYM = sym
        self.rank = -1
        self.score = 0
        self.ban = False
        self.lagban = False
        self.shortable = shortable
        self.tradable = True
        self.held = False
        self.current = 0
        

class PAsset: #asset that the trader knows about, and _is_ actively watching
    def __init__(self,sym):
        self.SYM = sym
        self.side = 'neutral'
        self.qty = 0
        self.entry = 0
        self.entryTime = dt.datetime.now() #works since PAsset is created when a position is opened
        self.uplpc = 0
        self.current = 0
        self.base = 0
        self.bardata5 = pd.DataFrame()
        self.bardata1 = pd.DataFrame()

class LogEvent: #assumes logevent is created as a position is closed
    def __init__(self,sym,qty,side,entry,entryTime,exit):
        self.SYM = sym
        self.qty = qty
        self.side = side
        self.entry = entry
        self.exit = exit
        self.entryTime = entryTime
        self.exitTime = dt.datetime.now()
        self.holdTime = self.exitTime-self.entryTime
        self.change = self.exit-self.entry
        self.plpc = self.change/self.entry


###TRADER CLASS (Master variable for the program)
class Trader:
    def __init__(self):
        self.universe = [] #list of "Uassets"
        self.portfolio = [] #list of "PAssets"
        self.log = [] #list of "LogEvents"
        self.ucounter = 0 #increments when a universe asset is sampled, used to cycle through UAssets
        #Account-related variables
        self.cash = 0
        self.ok = True
        self.today = DTzero
        self.backuprank = 0
    
    ###Universe functions
    def ban(self,SYMs,Ban=True,All = False): #can also be used to unban
        if All:
            for u in self.universe:  
                u.ban = Ban
        if isinstance(SYMs,str):
            for u in self.universe:
                if u.SYM == SYMs:
                    u.ban = Ban
        elif isinstance(SYMs,list):
            for SYM in SYMs:
                for u in self.universe:
                    if u.SYM == SYM:
                        u.ban = Ban
    def growUniverse(self,List): #transfer
        if isinstance(List,str) and List.endswith('SYM.txt'):
            ulist = txt2List(List)
        elif isinstance(List,str):
            ulist = [s.strip() for s in List.split(',')]
        elif isinstance(List,list):
            ulist = List
        c = 1; d = 0
        for SYM in [SYM.upper() for SYM in ulist]:
            if SYM in [u.SYM for u in self.universe]:
                print('{} already in universe'.format(SYM))
            else:
                try:
                    alas = APIP.get_asset(SYM)
                    c += 1
                    if not alas.tradable or not alas.status.lower() == 'active':
                        print('{} not tradable in Alpaca'.format(SYM))
                    else:
                        #Find if shortable
                        if not alas.shortable or not alas.easy_to_borrow:
                            shortable = False
                        else:
                            shortable = True
                        self.universe.append(UAsset(SYM,shortable))
                        d += 1
                    if c%89 == 0:
                        print('resting API')
                        time.sleep(55)
                except:
                    print("{} not found in Alpaca".format(SYM))
        print('Tried {:d} symbols, added {:d} to universe'.format(len(ulist),d))
            
             
    def destroyUniverse(self):
        self.universe = []
    def score(self,how='RSI'): #Uses alpaca barsets to apply a indicator-based score to each symbol
        if how == 'RSI': #13-day RSI
            c = 1
            for u in self.universe:
                barset = APIP.get_barset(u.SYM,'1D',limit=34).df[u.SYM]
                c += 1
                rsi = ta.RSI(barset['close'],timeperiod=13)
                u.score = rsi[-1]
                if c%89 == 0:
                    print('resting API')
                    time.sleep(55)
        else:
            print('method "{}" not available!'.format(how))
    def rank(self): #assumes scores exist, arrange UAssets based on score and assigns rank equal to index
        self.universe.sort(key=lambda x: x.score,reverse=True)
        for j,u in enumerate(self.universe):
            u.rank = j+1 #rank starts at 1
                
    def banFrac(self,ban=0.5,keep=0,keepN=0): 
        #eliminate portions of the universe by banning or keeping a certain fraction
        #assumes universe is ranked
        if keepN > 0:
            if keepN > len(self.universe):
                print('Trying to keep more assets than available in universe!')
                return
            else:
                for u in self.universe:
                    if u.rank > keepN:
                        u.ban = True
                    else:
                        u.ban = False
                        
        else:       
            if keep > ban:
                ban = 1-keep
            if ban >= 1:
                print('Error, fraction "{:.2f}" greater than 1'.format(ban))
                return
            thresh = len(self.universe)*(1-ban)
            for u in self.universe:
                if u.rank > thresh:
                    u.ban = True
                else:
                    u.ban = False
    def sample(self,how='EP_up'): 
        #Open positions and add assets from the universe to the portfolio if they meet indicator criteria
        #call repatedly to cycle through whole universe. 
        #Also syncs "current" field of UAsset
        while True: #find a nonbanned asset
            u = self.universe[self.ucounter]
            self.ucounter = (self.ucounter + 1)%len(self.universe)
            if not u.ban and not u.lagban and not u.held:
                break
        if how.startswith('EP'):
            barset = APIP.get_barset(u.SYM,'5Min',limit=21).df[u.SYM]
            offset = NYTZ.localize(dt.datetime.now()+dt.timedelta(hours=3))-barset.index[-1]
            if offset > dt.timedelta(minutes=20):
                u.lagban = True
                print('{} banned, lagging by {:.1f} minutes'.format(u.SYM,offset.seconds/60))
                nextrank = 1000
                #find highest-ranking banned symbol and unban it
                for v in self.universe:
                    if not v.lagban and v.ban and v.rank < nextrank:
                        nextrank = v.rank
                if nextrank < len(self.universe):
                    self.universe[nextrank-1].ban = False #-1 because rank starts at 1
            else:
                u.current = barset['close'][-1]
                ema = ta.EMA(barset['close'],timeperiod=8)
                merisa = ta.RSI(ema,timeperiod=2)
                bardata = barset.assign(ema=ema,merisa=merisa)
                ###print(u.SYM)
                ###print('close:',", ".join([str(round(x,2)) for x in bardata.iloc[-5:]['close'].tolist()]))
                ###print('merisa:',", ".join([str(round(x,2)) for x in bardata.iloc[-5:]['merisa'].tolist()]))

                #"Global" ema variables here because why not
                EPlen1 = 2 #How many time intervals to check for extreme emarsi
                EPlen2 = 5 #How far back to look for upwards price action
                EPsat = 1 #emarsi must be under/over this
                EPthresh = 0.2 #percent increase from start to end of emalength required for signal to trigger

                if how == 'EP_up' or how == 'EP_2x': #upwards emapulse
                    if (bardata.iloc[-EPlen1:]['merisa'] < EPsat).all() and \
                    ((bardata.iloc[-1]['close'] - 
                     min(bardata.iloc[-EPlen2:]['close']))/bardata.iloc[-1]['close'] > EPthresh/100):
                        self.Open(u,'buy')
                        self.portfolio.append(PAsset(u.SYM))
                        u.held = True
                        return
                if how == 'EP_down' or how == 'EP_2x' and u.shortable: #downwards emapulse
                    if (bardata.iloc[-EPlen1:]['merisa'] > 100-EPsat).all() and \
                    ((max(bardata.iloc[-EPlen2:]['close']) - 
                     bardata.iloc[-1]['close'])/max(bardata.iloc[-EPlen2:]['close']) > EPthresh/100):
                        self.Open(u,'sell')
                        self.portfolio.append(PAsset(u.SYM))
                        u.held = True
                        return
    def watch(self,how = 'Merisa_thresh',Ethresh=50):
        #close positions and remove them from the portfolio
        #unlike sample, looks at the entire portfolio at once
        deleteThis = []
        for i,p in enumerate(self.portfolio):
            if how.startswith('Merisa'): #gonna need emarsi bardata again
                barset = APIP.get_barset(p.SYM,'5Min',limit=21).df[p.SYM]
                ema = ta.EMA(barset['close'],timeperiod=8)
                merisa = ta.RSI(ema,timeperiod=2)
                bardata = barset.assign(ema=ema,merisa=merisa)
                #store bardata for more accuracy
                if p.bardata5.empty:
                    p.bardata5 = bardata
                else:
                    p.bardata5 = p.bardata5.combine_first(bardata)
            if how == 'Merisa_thresh':
                if p.side == 'long' and (p.bardata5.iloc[-5:]['merisa'] > Ethresh).any() or \
                p.side == 'short' and (p.bardata5.iloc[-5:]['merisa'] < 100-Ethresh).any():
                    self.Close(p,why='merisa threshold')
                    self.portfolio.remove(p)
                    #reactivate symbol in universe
                    for u in self.universe:
                        if u.SYM == p.SYM:
                            u.held = False
    
                    

    #Interacting with Alpaca
    def syncAccount(self):
        alac = APIP.get_account()
        self.cash = float(alac.cash)+float(alac.short_market_value)*2 
        #because short positions are negative and get added to cash for some reason
        self.equity = float(alac.equity)
        self.last_equity = float(alac.last_equity)
        if not alac.shorting_enabled or alac.status != 'ACTIVE' or alac.account_blocked or alac.trading_blocked:
            self.ok = False
    def syncPositions(self,useFloor=False,Floor=0.3,useTime=False,holdTime=30*60):
        alpos = APIP.list_positions()
        #Update everything from alpaca postions list
        for a in alpos:
            found = False
            for i,p in enumerate(self.portfolio):
                if a.symbol == p.SYM:
                    found = True
                    p.qty = int(a.qty)
                    p.side = a.side
                    p.entry = float(a.avg_entry_price)
                    p.current = float(a.current_price)
                    p.uplpc = float(a.unrealized_plpc)
            if not found:
                print('{} in Alpaca but not Portfolio. Sent Delete Request...'.format(a.symbol))
                requests.delete(POSITIONS_URL+"/"+a.symbol,headers=HEADERS)
                time.sleep(5)
        #find if anything is in the portfolio but not yet in Alpaca (should be impossible given good sleep times),
        #but if so, conform potfolio to Alpaca
        for i,p in enumerate(self.portfolio):
            found = False
            for a in alpos:
                if a.symbol == p.SYM:
                    found = True #already did these
            if not found:
                print('{} found in Portfolio but not Alpaca. Removing from portfolio...'.format(p.SYM))
                del self.portfolio[i]
                
        #Apply sell floor
        if useFloor:
            for i,p in enumerate(self.portfolio):
                if p.uplpc > p.base:
                    p.base = p.uplpc #not converted to %
                if p.uplpc < p.base - Floor/100:
                    self.Close(p,why='sell floor')
                    del self.portfolio[i]
                    for u in self.universe:
                        if u.SYM == p.SYM:
                            u.held = False
        #apply sell time
        if useTime and time.time() > p.entryTime + holdTime:
            self.Close(p,why='expired')
            del self.portfolio[i]
            for u in self.universe:
                if u.SYM == p.SYM:
                    u.held = False
        time.sleep(5)
        self.syncAccount()
            
                    
                
    def Open(self,u,Side,cashFrac=0.2,maxShares=250): #u is a UAsset
        #assumes asset is neutral, i.e. no prior position to close
        #check for existing position; internal consistency check
        for p in self.portfolio:
            if p.SYM == u.SYM:
                print('Asset already in portfolio')
                return
        if self.cash <= 1000: #don't open a position
            print('Would open {}, but running low on cash ({:.3f}$)'.format(u.SYM,u.current))
            return
        #calculate number of shares from TD.cash and u.current
        qty = min([int(self.cash*cashFrac/u.current),maxShares])
        if qty <= 0:
            print('Would open {} but {:.3f} is too expensive'.format(u.SYM,u.current)) #not likely
            return
        #Place order
        if not Side.lower() in ('buy','sell'):
            print('Invalid side (buy or sell!)')
            return
        order = APIP.submit_order(
                        symbol = u.SYM,
                        qty = qty,
                        side = Side.lower(),
                        type = 'market',
                        time_in_force='gtc')
        print('Opened {} on {} at {:.3f}'.format(Side,u.SYM,u.current))
        time.sleep(5)
        self.syncAccount()
    def Close(self,p,why=''):
        #With requests.delete, we don't need to assume position exists
        requests.delete(POSITIONS_URL+"/"+p.SYM,headers=HEADERS)
        print('Closed {} on {} for {:.3f}% ({})'.format(p.side,p.SYM,p.uplpc*100,why))
        self.log.append(LogEvent(p.SYM,p.qty,p.side,p.entry,p.entryTime,p.current))
        time.sleep(5)
        self.syncAccount()
    def liquidate(self):
        #Might as well put the most important function here
        requests.delete(POSITIONS_URL,headers=HEADERS)
        time.sleep(10) #double delete to be certain no positions remain
        requests.delete(POSITIONS_URL,headers=HEADERS)

    def startDay(self,banFrac=0.5,keepN=0,Recalculate=True):
        self.log = [] #clear log
        if Recalculate:
            #unban everything
            self.ban('????',All=True,Ban=False)
            for u in self.universe:
                u.lagban = False
            self.score()
            self.rank()
            self.banFrac(ban=banFrac,keepN=keepN)
            time.sleep(30) #extra sleep because
    def endDay(self): #reset EVERYTHING
        for p in self.portfolio:
            self.Close(p,why='Day End')
        self.portfolio = []
        for u in self.universe:
            u.held = False
    def listLog(self):
        totalgain = 0
        for l in self.log:
            if l.side == 'long':
                pm = 1
            elif l.side == 'short':
                pm = -1
            totalgain += l.change*l.qty*pm
            entryTime = str(l.entryTime.time()).split('.')[0]
            exitTime = str(l.exitTime.time()).split('.')[0]
            print("{} {:d} {}, entered {:.2f} at {}, exit {:.2f} at {}, {:.2f}$ ({:.3f}%)".format(l.side,l.qty,l.SYM,
                                                                                                  l.entry,
                                                                                              entryTime,l.exit,
                                                                                              exitTime,
                                                                                                  l.change*l.qty*pm,
                                                                                                l.plpc*100*pm))

        print('Total day gain: {:.2f}$ with {:d} trades'.format(totalgain,len(self.log)))
                                                                                                  
        
###RUN FUNCTION (outside Trader because it needs to save)
def run(TD,debug=True,debug0=False):
    if TD.today != dt.datetime.now().date():
        TD.startDay(keepN=34)
        TD.today = dt.datetime.now().date()
    while True:
        APClock = APIP.get_clock()
        if APClock.is_open and dt.datetime.now().time() < ALMOSTMARKETCLOSE and dt.datetime.now().time() > ALMOSTMARKETOPEN:
            SaveTD(TD)
            nextminute5 = time.time() + 5*60
            TD.syncAccount()
            TD.watch()
            currentuc = TD.ucounter; loop = False
            
            if debug:
                for p in TD.portfolio:
                    try:
                        print("{} {}, current {:.2f}, merisa {:.3f}, uplpc {:.3f}".format(p.SYM,p.side,p.current,
                                                                                   p.bardata5['merisa'][-1],
                                                                                  p.uplpc*100))
                    except KeyError:
                        pass
            if debug0:
                print('5min loop')
                    
            while time.time() < nextminute5:
                nextminute1 = time.time() + 60
                TD.syncPositions(useFloor=False,useTime=False)
                time.sleep(5)
                    
                while time.time() < nextminute1:
                    if debug0:
                        print("ucounter: {:d}, Number positions: {:d}, cash: {:.2f}".format(TD.ucounter,
                                                                                           len(TD.portfolio),
                                                                                          TD.cash))
                    if TD.ucounter == currentuc and loop:
                        pass
                    else:
                        TD.sample(how='EP_up')
                        loop = True
                    time.sleep(3)
        elif not APClock.is_open and dt.datetime.now().time() < MARKETOPEN:
            print('Waiting for market to open')
            time.sleep(10)
        elif dt.datetime.now().time() > ALMOSTMARKETCLOSE:
            print('End of trading day')
            TD.endDay()
            time.sleep(30)
            TD.syncAccount()
            print('Day gain: {:.2f} ({:3f})'.format(TD.equity-TD.last_equity,
                                                    (TD.equity-TD.last_equity)/TD.last_equity*100))
            return
        else: #should only happen in the morning before the market opens
            time.sleep(60)
        
#What's going on here: Every 5 minutes, applies watch rule. Then every minute after within those 5 minutes, syncs 
#account, positions. Samples from the universe while waiting for that minute to pass. Will not loop over the 
#universe within 5 minutes

###ENTRY POINT FUNCTION
def main():
##    #Make or load a trader
##    try:
##        TD = LoadTD()
##    except:
##        TD = Trader()
##        TD.growUniverse('ETFSYM.txt')
##        
##    #Run the trader continuously, run>break ends when market close
##    while True:
##        try:
##            run(TD,debug=True,debug0=False)
##            break
##        except Exception as e:
##            print(e)
##            time.sleep(60*2)
##            
##    #Sleep until right before the market opens, run will do the necessary preparations and wait to trade
##    nextopen = getNextOpen()
##    time.sleep((nextopen-dt.datetime.now()).total_seconds())
##    #Recursion because more while True is ugly
##    main()

    #PLACEHOLDER TEST ROUTINE
    c = 0
    while True:
        time.sleep(60*5)
        if c%2 == 0:
            side = 'buy'
        elif c%2 == 1:
            side = 'sell'
        print(side+'!')
        order = APIP.submit_order(
                        symbol = 'TSLA',
                        qty = 5,
                        side = side,
                        type = 'market',
                        time_in_force='gtc')
        c+=1
        
    
    

if __name__ == "__main__":
    main()
    
    
    


    
