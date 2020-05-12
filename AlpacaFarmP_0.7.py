#AlpacaFarmP - Implementation of algorithmic trading strategy in the paper (P)
#trading API of alpaca.

#Todo:
#Implement the favorite SYM system, have a file somewhere recording the favor levels of different symbols
#Give each symbol a "stale" timer, indicating a maximum hold time

#Reformat the code to iterate through many (500+) stock instead of the same list of symbols limited by API calls. Keep
#stocks with a position in the portfolio, and exchange out the others




import alpaca_trade_api as tradeapi
from config import *
#contains API key variables KEY_ID and SECRET_KEY, as well as various URLS
from pandas import DataFrame
import talib as ta
import talib.abstract as tab

import requests, time, os, copy, random, json
import datetime as dt
import pandas as pd
import numpy as np


#GLOBAL VARIABLES:==============
APIP = tradeapi.REST(KEY_ID,SECRET_KEY,PAPER_URL,api_version='v2')
EAC = 0.2 #Expected fraction os assets in circulation at any given time, used to calculate shares to buy
EAC_SF = 0.01 #safety percent to always leave some leftovers of cash in the pot
HardSellFloor = 0.025 #unrealized percent loss that will trigger a hard sell condition and cooldown (don't divide by 100)

#TRADING STRATS:================
#accepts baradata with built-in indicators, returns boolean

#volumestrat41, theoretically the best of the volume-based scalping strategies 
def buystrat_vs41(bardata):
    if bardata['adx'][-1] > 23 and \
        bardata['mfi'][-1] < 21 and \
        bardata['ultosc'][-1] < 40 and \
        bardata['rsi'][-1] < 35 and \
        bardata['minusdi'][-1] > bardata['plusdi'][-1]:
        return True
    else:
        return False
def sellstrat_vs41(bardata):
    if bardata['adx'][-1] > 23 and bardata['rsi'][-1] > 75:
        return True
    else:
        return False

#Hey what if we just tried to ride rsi for all it's worth? This strat buys on a steep rsi "derivative"
#and sells near the peak (hopefully)
def buystrat_rsicaveman(bardata):
    if bardata['rsi'][-3] > 35 and bardata['rsi'][-1] > 45:
        return True
    else:
        return False
    
def sellstrat_rsicaveman(bardata):
    if bardata['rsi'][-1] > 60:
        return True
    else:
        return False


def liquidate(Log=''):
#liquidates account (closes all positions, sells all holdings) by sending DELETE to positions url
#Most important function
    positions = APIP.list_positions()
    Lnow = dt.datetime.now().isoformat() #note this timestamp timezone or whatever is different than alpaca's
    requests.delete(POSITIONS_URL,headers=HEADERS)
    if bool(Log):
        LogFile = open(Log,'a')
        for position in positions:
            uplpc = float(position.unrealized_plpc)
            LogFile.write("{},lsell,{},{:d},{:.2f},{:.2f}\n".format(Lnow,position.symbol,int(position.qty),
                                                                    float(position.current_price),float(position.unrealized_plpc)))
        LogFile.close()
    
def getSYMlist(SYMtxt): #return list of symbols from symtxt, 
    f = open(SYMtxt,'r')
    SYMlist = [sym.rstrip("\n") for sym in f.readlines()]
    random.shuffle(SYMlist) #get a random sample if using maxcount below
    f.close()
    return SYMlist
    
def makePF(SYMlist,maxcount=10000,banlist=[]):
#Makes initial portfolio (PF), list of asset dictionary (asd) objects, cutoff at length maxcount
#asd object includes:
#SYM: symbol
#Nshares: shares held, zero by default
#shprice: market share price when bought/sold. Different prices per share is too complex. 0 by default
#side: 'long', 'short' (not implemented) or False for no position in alpaca
#cooldown: timestamp float telling when asset should become active again, 0 otherwise. Use with sell floor condition
#ban: True if the asset is blacklisted (i.e. not valid, macro event) forbidding trading, False otherwise
#favor: Favorability factor, how much we "like" any asset, influences how much money we'll give it. Default 1    
    pf = []
    count = 0
    for j,SYM in enumerate(SYMlist):
        pf.append({'SYM':SYM,'Nshares':0,'shprice':0,'side':False,'cooldown':0,'ban':False,'favor':1})
        count += 1
        try:
            if SYM in banlist or not APIP.get_asset(SYM).tradable: #preemptive ban
                pf[j]['ban'] = True
        except: #Assuming bad symbol
            pf[j]['ban'] = True
        if count >= maxcount:
            return pf
    return pf

def makePF_A():
#make portfolio dictionary object from read on current alpaca positions. Enables use of the run script between multiple runs
    pf = []
    print('<=====Portfolio Positions=====>')
    for position in APIP.list_positions():
        SYM = position.symbol
        Nshares = int(position.qty)
        shprice = float(position.current_price)
        side = position.side
        pf.append({'SYM':SYM,'Nshares':Nshares,'shprice':shprice,'side':side,'cooldown':0,'ban':False,'favor':1})
        print('{} on {}, {:d} shares at {:.2f}'.format(side,SYM,Nshares,shprice))
    return pf
        
        



#Add or subtract more indicators for any other strategy you want to use
def populateindicators(dataframe):
    bardata = dataframe.assign(mfi=ta.MFI(dataframe['high'],dataframe['low'],dataframe['close'],
                                np.asarray(dataframe['volume'], dtype='float'), timeperiod=14),
                     ultosc = ta.ULTOSC(dataframe['high'],dataframe['low'],dataframe['close']),
                     minusdi = tab.MINUS_DI(dataframe, timeperiod=14),
                     plusdi = tab.PLUS_DI(dataframe, timeperiod=14),
                     rsi = tab.RSI(dataframe, timeperiod=14, price='close'),
                     adx = tab.ADX(dataframe)
                     )
    return bardata

def RUN(PF,LogFilecsv='AlpacaLog1.csv',stopwhen=False,LogTrue=True):
    #Loop over the portfolio and trade assets
    #Logs every trade, buy or sell, on the logfile, from which activity may one day be reconstructed
    #Logs consists of the following fields:
    #timestamp: last time recorded in the barset dataframe, a printed datetime object
    #buysell: 'buy' or 'sell' 'fsell' if sold by hard sell floor condition,lsell if by liquidate
    #SYM: SYM
    #Nshares: number of shares transacted
    #shprice: instantaneous market price of 1 share
    #percentreturn: blank string if 'buy', percent return on the trade if 'sell'
        #could reconstruct this, but should be handier to record it outright
    
    #stopwhen is a datetime object that determines when the loop will stop

    #SETUP=================
    STOP = False
    today = dt.datetime.today().date()
    MarketOpen = dt.datetime(year=today.year, month=today.month, day=today.day,
                             hour=6, minute=30, second=0)
    MarketClose = dt.datetime(year=today.year, month=today.month, day=today.day,
                             hour=13, minute=0, second=0)
    daystart=pd.Timestamp(year=today.year, month=today.month, day=today.day,
                          hour=0,tz='America/New_York').isoformat()
    nextminute = time.time()+60

    AACC = APIP.get_account() #Account object. Does not update on its own, must be refreshed with every usage
    APClock = APIP.get_clock()
    StartingCash = float(AACC.cash) #Starting cash amount, used in asset allocation calc.
    
    if not LogFilecsv in os.listdir(): #Make LogFile if it does not exist
        LogFile = open(LogFilecsv,'w')
        LogFile.write('timestamp,buysell,SYM,Nshares,shprice,preturn\n')
        LogFile.close()
    LogFile = open(LogFilecsv,'a')

    buyorderids = []

    


    #LOOP====================    
    while True:
        APClock = APIP.get_clock() #refresh this here, account is refreshed in the for ASD loop
        #Stop contions
        if dt.datetime.now() > MarketClose-dt.timedelta(minutes=20):
            print("Near market close, liquidating and closing shop")
            LogFile.close()
            liquidate(Log=LogFilecsv)
            return PF
        if bool(stopwhen) and dt.datetime.now() > stopwhen:
            print('Time stop condition met')
            LogFile.close()
            return PF
        if float(AACC.cash) < 0: #somehow we spent all our money
            print('Cash in account < 0, stopping trades and liquidating positions')
            liquidate()
            LogFile.close()
            return PF
        if AACC.trading_blocked or AACC.account_blocked:
            print('Something is wrong with Alpaca account status')
            LogFile.close()
            return PF

        caveSYM = random.choice(PF)['SYM']
        for ASD in PF:
            AACC = APIP.get_account() #refresh account object
            if time.time() >= ASD['cooldown']: #reactivate nullified stocks
                ASD['cooldown'] = 0

            try:    
                if not ASD['ban'] and ASD['cooldown'] <=0 :
                    #get barset data and process
                    barset = APIP.get_barset(ASD['SYM'],'1Min',limit=150).df #,start=daystart
                    #print(ASD['SYM']+' '+str(barset.index[-1]))
                    #panda with columns open, high, low, close, volume
                    bardata=populateindicators(barset[ASD['SYM']])
                    if ASD['SYM'] == caveSYM:
                        print(ASD['SYM']+'=======================>')
                        print(bardata.index[-1])
                    #Buy condition
                    if not bool(ASD['side']) and buystrat_vs41(bardata):
                        #Calculate Number of shares to buy
                        cash=min([float(AACC.cash)*0.5,StartingCash/((EAC+EAC_SF)*len(PF))*ASD['favor']])
                        #allocates the fraction of starting cash predicted by the EAC (fraction os assets in circulation)
                        #Or, defaults to half the cash currently in the bank if supplies running lower than that
                        shprice = barset.iloc[-1,-2] #most recent close
                        Nshares = int(cash/shprice) #check the indexing here. c for close. Must be at least 1 share
                        
                        #buy
                        if Nshares > 0: #API throws error on trying to buy 0 shares
                            order = APIP.submit_order(
                                symbol = ASD['SYM'],
                                qty = Nshares,
                                side = 'buy',
                                type = 'market',
                                time_in_force='gtc')
                            print('Bought {:d} shares of {}'.format(Nshares,ASD['SYM']))
                            buyorderids.append(order.id)
                            ASD['side'] = 'long'
                            ASD['Nshares'] = Nshares
                            ASD['shprice'] = shprice
                        else:
                            print('Would buy {}, but out of money'.format(ASD['SYM']))
                        
                    #sell condition
                    elif ASD['side'] == 'long' and sellstrat_vs41(bardata): 
                        order = APIP.submit_order(
                            symbol = ASD['SYM'],
                            qty = ASD['Nshares'],
                            side = 'sell',
                            type = 'market',
                            time_in_force='gtc')
                        position = APIP.get_position(ASD['SYM'])
                        sshprice = float(position.current_price)
                        percentreturn = float(position.unrealized_plpc)*100
                        #alternatively, find the position and ask for pnl from the api
                        
                        #Print and record what happened, if it happened
                        print('Sold {:d} shares of {} at {:.2f} for {:.2f}% return'.format(ASD['Nshares'],
                                                                                           ASD['SYM'],sshprice,percentreturn))
                        if LogTrue:
                            LogFile.write('{},sell,{},{:d},{:.2f},{:.2f}\n'.format(
                                                str(order.submitted_at),ASD['SYM'],Nshares,shprice,percentreturn))
                        ASD['side'] = False
                        ASD['Nshares'] = 0
                        ASD['shprice'] = 0
            except:
                print(ASD['SYM']+': error.')
                #ASD['ban'] = True

        #hard sell floor condition (outside of buy/sell loop)
        for position in APIP.list_positions():
            uplpc = float(position.unrealized_plpc)
            if uplpc <= -HardSellFloor and APClock.is_open:
                shprice = float(position.current_price)
                ASD = next((asd for asd in PF if asd['SYM'] == position.symbol), None)
                order = APIP.submit_order(
                    symbol = ASD['SYM'],
                    qty = ASD['Nshares'],
                    side = 'sell',
                    type = 'market',
                    time_in_force='gtc')
                print('Sold {:d} shares of {} at {:.2f} ({}% sell floor triggered)'.format(
                    ASD['Nshares'],ASD['SYM'],shprice,HardSellFloor*100))
                if LogTrue:
                    LogFile.write('{},fsell,{},{:d},{:.2f},{:.2f}\n'.format(
                                            str(order.submitted_at),ASD['SYM'],Nshares,shprice,uplpc))
                ASD['side'] = False
                ASD['Nshares'] = 0
                ASD['shprice'] = 0
                ASD['cooldown'] = time.time()+60*30

        #Record buy orders
        if LogTrue:
            for buyid in buyorderids:
                #print(buyid)
                request = requests.get(ORDERS_URL+"/{"+buyid+"}",headers=HEADERS)
                order=json.loads(request.content.decode('utf-8'))
                LogFile.write('{},buy,{},{:d},{}\n'.format(
                                            str(order['submitted_at']),order['symbol'],
                                            int(order['qty']),order['filled_avg_price']))
            buyorderids = [] #clear the cache
                        

        while dt.datetime.now() < MarketOpen:
            time.sleep(1)
        while nextminute-time.time()>0: #don't update until at least a minute has passed
            time.sleep(1)
        nextminute = time.time()+60
        LogFile.close() #save your work
        LogFile = open(LogFilecsv,'a')
        #print('A minute passed!') #Delete this later


###DOING THE THING==========
#Create SYMlist
SYMlist = getSYMlist('S&P500_2020Q2SYM.txt')
#Create portfolio
PFA = makePF_A() #Get any positions we're currently holding
PFB = makePF(SYMlist,maxcount=(180-len(PFA))) #Fill in the rest
PF = PFA+PFB #Can add together because they're lists
#Press start to RICH
PF = RUN(PF) #stopwhen = dt.datetime.now()+dt.timedelta(minutes=60*3)
                
        
            

           
                
            
                      
            
        
    

