#Systematic Backtester.py

#Beginnings of systematic iterative strategy testing. The backtrader cerebro run is contained within a function with
#strictly defined inputs and outputs. Outcomes of tests are written to a CSV file, which can be analyzed for trends

#TODO: 
#Make and test even larger data sets

#Write a function that plots Number of trades versus percent return for 1 strat, see if it looks like a bell curve

#Add min/max timestamp option to analyzer plotting functions

#import bt strats from a separate file

import backtrader as bt
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
# --------------------------------
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------
import talib.abstract as tab
from typing import Dict, List
from pandas import DataFrame, DatetimeIndex, merge
# --------------------------------
import talib as ta
import random, time, os
import datetime as dt
import numpy as np

###BT STRAT CLASSES (skip this part)
class Scalp(bt.Strategy):

    
    
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=10)
        self.emaclose=bt.indicators.EMA(self.data.close, period=10)
        self.emalow=bt.indicators.EMA(self.data.low, period=10)
        self.rsi=bt.talib.RSI(self.data.close, timeperiod=14 )
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        
        #macd indicators
        #self.macd_arr=bt.indicators.macd(self.data.close)
        
        #self.macd=self.macd_arr[0]
        #self.macdsignal=self.macd_arr[1]
        
        
        
        #creat stochastic momentum indicators 
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=14, slowk_period=4, slowd_period=4)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.adx > 30 and \
            self.fastd < 30 and \
            self.fastk < 30:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.fastd > 70  and \
            self.rsi > 87  and \
            self.fastk > 70:
                self.sell()
                
class Scalp4(bt.Strategy):  
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=5)
        self.emaclose=bt.indicators.EMA(self.data.close, period=5)
        self.emalow=bt.indicators.EMA(self.data.low, period=5)
        self.rsi=bt.talib.RSI(self.data.close, timeperiod=14 )
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        
        #macd indicators
        #self.macd_arr=bt.indicators.macd(self.data.close)
        
        #self.macd=self.macd_arr[0]
        #self.macdsignal=self.macd_arr[1]
        
        
        
        #creat stochastic momentum indicators 
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.adx > 30 and \
            self.rsi < 29  and \
            self.fastd < 30 and \
            self.fastk > self.fastd and \
            self.fastk < 30:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.fastd > 70  and \
            self.rsi > 80  and \
            self.fastk > 70:
                self.sell()

class Scalpy(bt.Strategy):
    """
        this strategy is based around the idea of generating a lot of potential buys and make tiny profits on each trade
        we recommend to have at least 60 parallel trades at any time to cover non avoidable losses.
        Recommended is to only sell based on ROI for this strategy
    """ 
#populate a dataframe with indicators
    
    
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=10)
        self.emaclose=bt.indicators.EMA(self.data.close, period=10)
        self.emalow=bt.indicators.EMA(self.data.low, period=10)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        self.mfi=bt.talib.MFI(self.data.high , self.data.low ,self.data.close ,self.data.volume, timeperiod=14 )
        self.rsi=bt.talib.RSI(self.data.close, timeperiod=14 )
        
        
        
        #macd indicators
        #self.macd_arr=bt.indicators.macd(self.data.close)
        
        #self.macd=self.macd_arr[0]
        #self.macdsignal=self.macd_arr[1]
        
        
        
        #creat stochastic momentum indicators 
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=14, slowk_period=4, slowd_period=4)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.adx > 30 and \
            self.fastk < 30 and \
            self.rsi < 25 and \
            self.cci <= -120.0:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.fastk > 70 and \
            self.fastd > 70  and \
            self.rsi > 83  and \
            self.cci >= 120.0 :
                self.sell()

class Scalpy3(bt.Strategy):
    
    
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=10)
        self.emaclose=bt.indicators.EMA(self.data.close, period=10)
        self.emalow=bt.indicators.EMA(self.data.low, period=10)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #macd indicators
        #self.macd_arr=bt.indicators.macd(self.data.close)
        
        #self.macd=self.macd_arr[0]
        #self.macdsignal=self.macd_arr[1]
        
        
        
        #creat stochastic momentum indicators 
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=14, slowk_period=4, slowd_period=4)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.adx > 20 and \
            self.fastk < 20 and \
            self.fastd < 20 and \
            self.cci <= -150.0:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.fastk > 95 and \
            self.fastd > 95  and \
            self.cci >= 150.0 :
                self.sell()

class Scalpy2(bt.Strategy):
    
    
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=10)
        self.emaclose=bt.indicators.EMA(self.data.close, period=10)
        self.emalow=bt.indicators.EMA(self.data.low, period=10)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        self.mfi=bt.talib.MFI(self.data.high , self.data.low ,self.data.close ,self.data.volume, timeperiod=14 )
        self.rsi=bt.talib.RSI(self.data.close, timeperiod=14 )
        
        
        
        #macd indicators
        #self.macd_arr=bt.indicators.macd(self.data.close)
        
        #self.macd=self.macd_arr[0]
        #self.macdsignal=self.macd_arr[1]
        
        
        
        #creat stochastic momentum indicators 
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=14, slowk_period=4, slowd_period=4)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.adx > 30 and \
            self.fastk < 30 and \
            self.fastd < 30 and \
            self.cci <= -130.0:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.fastk > 75 and \
            self.fastd > 75  and \
            self.rsi > 85  and \
            self.cci >= 100.0 :
                self.sell()

class Scalp2(bt.Strategy):
    
    
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=10)
        self.emaclose=bt.indicators.EMA(self.data.close, period=10)
        self.emalow=bt.indicators.EMA(self.data.low, period=10)
        self.rsi=bt.talib.RSI(self.data.close, timeperiod=14 )
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        
        #macd indicators
        #self.macd_arr=bt.indicators.macd(self.data.close)
        
        #self.macd=self.macd_arr[0]
        #self.macdsignal=self.macd_arr[1]
        
        
        
        #creat stochastic momentum indicators 
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=14, slowk_period=4, slowd_period=4)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.adx > 30 and \
            self.fastd < 30 and \
            self.fastk < 30:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.fastd > 70  and \
            self.rsi > 90  and \
            self.fastk > 70:
                self.sell()

###FUNCTIONS==========================================================

def writeInputOutput(Strategy,Input,Output,CSVfilename):
#The column order in the CSV is currently: 
#Timestamp; Strategy; Symbol; StartDate; EndDate; Interval; BarLength; Set; PercentIncrease; Ntrades
#Strategy is the strategy name string, input/output are dicts, CSVfilename= BTArchive1.csv
#Assumes a such a file already exists, copypaste the above line into a txt, call it XXXX.csv

    if not CSVfilename in os.listdir(): #don't write a new file. 
        print(CSVfilename+' not found.')
        return
    with open(CSVfilename,'a') as CSV: #append mode
        Timestamp = str(int(time.time())) #"ID number"
        time.sleep(1)
        PercentIncreaseStr = '{:.2f}'.format(Output['PercentIncrease'])
        
        CSV.write(Timestamp+','+Strategy+','+Input['SYM']+','+Input['StartDate']+','+Input['EndDate']+','+
                 Input['Interval']+','+str(Input['YDF'].shape[0])+','+
                 Input['Set']+','+PercentIncreaseStr+','+str(Output['Ntrades'])+"\n")
        CSV.close()
        
def getInputs_SYMS(N,SymListTxt,StartDate,EndDate,Interval):
    #Get many inputs of random symbols
    #N=number of symbols to pull, SymListText = "data set" to pull them from (must end with SYM.txt, 
        #i.e. BigCapSYM.txt) 
    #Interval = bar interval (same as yf, '1m', 30m, 1d, 1mo, et),
    #Dates as a string ('2020-04-06')
    
    
    SYMS = [False]*N
    Inputs = []
    for i in range(N):
        while True: #Keep going until you get a valid YDF
            #choose a symbol, no repeats
            f = open(SymListTxt)
            flines=f.readlines()
            while True:
                SYM = random.choice(flines).rstrip("\n")
                if not SYM in SYMS:
                    break
            f.close()
            #download
            YDF = yf.download([SYM],start=StartDate,end=EndDate,interval=Interval)
                               
            if not YDF.shape[0]==0: #No data was downloaded, yf will describe what went wrong
                SYMS[i]=SYM
                break
        
        YDF = YDF.dropna() #Remove NaN rows, if any
        Inputs.append({'YDF':YDF,'SYM':SYM,'StartDate':StartDate,
                       'EndDate':EndDate,'Interval':Interval,
                      'Set':SymListTxt.rstrip("SYM.txt")})
        #dt.datetime.strptime(StartDate,'%Y-%m-%d')
    return Inputs #returns list of dicts, dicts containing the YDF and its important qualifiers

def getInput(SYM,StartDate,EndDate,Interval,Set='All'):
    #simpler version of getInputs for one symbol.
    #reguires set text string for category, use ALL for now
    
       
    YDF = yf.download([SYM],start=StartDate,end=EndDate,interval=Interval)
                       
    if YDF.shape[0]==0: #No data was downloaded, yf will describe what went wrong
        return False
    YDF = YDF.dropna() #Remove NaN rows, if any
        
    Input = {'YDF':YDF,'SYM':SYM,'StartDate':StartDate,
                   'EndDate':EndDate,'Interval':Interval,
                  'Set':Set}
    #dt.datetime.strptime(StartDate,'%Y-%m-%d')
    return Input #returns list of dicts, dicts containing the YDF and its important qualifiers

def getInputs_DATES(N,SYM,StartRange,EndRange,DaySpan,Interval,Set='All'):
    #N = number of random dates to get
    #DateSpan = integer indicating how many days each input set should span
    #StartRange, Endrange = sample period, formatted with %Y-%m-%d
    StartDates = [False]*N
    EndDates = [False]*N
    Inputs = []
    for i in range(N):
        while True: #Keep going until you get a valid YDF
            #choose a date, no repeats
            sord = dt.datetime.strptime(StartRange,'%Y-%m-%d').date().toordinal()
            eord = dt.datetime.strptime(EndRange,'%Y-%m-%d').date().toordinal()
            tord = dt.datetime.now().date().toordinal()
            while True:
                StartDateD = dt.date.fromordinal(random.randint(sord, eord)) #date object
                EndDateD = StartDateD + dt.timedelta(days=DaySpan)
                if not StartDateD.strftime('%Y-%m-%d') in StartDates \
                and tord-EndDateD.toordinal() >= 0: 
                #Dates lists contain strs. Also, no end dates in the future
                    break
            
            
            #download
            StartDate = StartDateD.strftime('%Y-%m-%d')
            EndDate = EndDateD.strftime('%Y-%m-%d')
            #print(StartDate+'__'+EndDate)
            YDF = yf.download([SYM],start=StartDate,end=EndDate,interval=Interval)
            
            if not YDF.shape[0]==0: #No data was downloaded, yf will describe what went wrong
                StartDates[i] = StartDate
                EndDates[i] = EndDate
                break
            
        YDF = YDF.dropna() #Remove NaN rows, if any        
        Inputs.append({'YDF':YDF,'SYM':SYM,'StartDate':StartDate,
                       'EndDate':EndDate,'Interval':Interval,
                      'Set':Set})
        #dt.datetime.strptime(StartDate,'%Y-%m-%d') .strftime('%Y-%m-%d')
    return Inputs #returns list of dicts, dicts containing the YDF and its important qualifiers

def getInputs_DATESYMS(N,SymListTxt,StartRange,EndRange,DaySpan,Interval,Set='All'):
    #ok cool, now let's randomize dates and SYMS at the same time
    StartDates = [False]*N
    EndDates = [False]*N
    SYMS = [False]*N
    Inputs = []
    for i in range(N):
        while True:
            #choose a date, no repeats
            sord = dt.datetime.strptime(StartRange,'%Y-%m-%d').date().toordinal()
            eord = dt.datetime.strptime(EndRange,'%Y-%m-%d').date().toordinal()
            tord = dt.datetime.now().date().toordinal()
            while True:
                StartDateD = dt.date.fromordinal(random.randint(sord, eord)) #date object
                EndDateD = StartDateD + dt.timedelta(days=DaySpan)
                if not StartDateD.strftime('%Y-%m-%d') in StartDates \
                and tord-EndDateD.toordinal() >= 0: 
                #Dates lists contain strs. Also, no end dates in the future
                    break    
            #choose a symbol, no repeats
            f = open(SymListTxt)
            flines=f.readlines()
            while True:
                SYM = random.choice(flines).rstrip("\n")
                if not SYM in SYMS:
                    break
            f.close()
            
            #download
            StartDate = StartDateD.strftime('%Y-%m-%d')
            EndDate = EndDateD.strftime('%Y-%m-%d')
            YDF = yf.download([SYM],start=StartDate,end=EndDate,interval=Interval)
            
            if not YDF.shape[0]==0: #No data was downloaded, yf will describe what went wrong
                StartDates[i] = StartDate
                EndDates[i] = EndDate
                SYMS[i] = SYM
                break
                
        YDF = YDF.dropna() #Remove NaN rows, if any    
        Inputs.append({'YDF':YDF,'SYM':SYM,'StartDate':StartDate,
                       'EndDate':EndDate,'Interval':Interval,
                      'Set':Set})
    return Inputs #returns list of dicts, dicts containing the YDF and its important qualifiers
            
        
    

def testInput(Input,StratName,WriteFile='BTArchive1.csv'):
    #feed dataframe to cerbro
    datacere = bt.feeds.PandasData(dataname=Input['YDF'])
    
    #create backtrader
    cerebro = bt.Cerebro()
    #Find strategy. I could do this with eval(StartName), but that's not safe
    if StratName in StratList:
        cerebro.addstrategy(eval(StratName)) #this eval isn't too much of a security risk, is it?
    else:
        print('StratName not Found')
        return

    #set up cerebro
    StartCash = 100000 #I would like this number for later
    cerebro.broker.setcash(StartCash)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.addsizer(bt.sizers.AllInSizer)
    #All In Sizer always uses maximum cash possible, meaning we can divide the profit by the starting cash later to
    #get a normalized percent increase
    cerebro.adddata(datacere)
    #Analyzers. I am not sure how many of these lines are necessary
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="ret")
    cerebro.addanalyzer(bt.analyzers.PeriodStats, _name="pstat")
    cerebro.addanalyzer(bt.analyzers.Transactions, _name="trans")
    
    #Run
    try:
        result = cerebro.run()
        analysis = result[0].analyzers.ta.get_analysis()
    except IndexError:
        print('Error in Cerebro')
        return False
    #Get the output
    Gross = cerebro.broker.getvalue()
    PercentIncrease= (Gross-StartCash)/StartCash*100
    Ntrades = analysis['total']['total']
    Output = {'PercentIncrease':PercentIncrease,'Ntrades':Ntrades}
    
    if bool(WriteFile):
        writeInputOutput(StratName,Input,Output,WriteFile)
    print('Used {} on {} from {} to {}'.format(StratName,Input['SYM'],Input['StartDate'],Input['EndDate']))                                                       
    print('Returned {:.2f}% with {:d} trades'.format(Output['PercentIncrease'],Output['Ntrades']))
    print('<==========*==========>')
    return Output

###ANALYSIS FUNCTIONS==========================================================

def BarAverage1(Strats,Interval,Yaxis='PercentIncrease',Weighting='DataSize',CSV='BTArchive1.csv'):
    #Runs through lines in the CSV archive, averaging together all lines of the same strat name tested 
    #over the specified interval. The average can be weighted by the total length of the input data used or the 
    #number of trades made
    
    #get the Y data
    DF = pd.read_csv(CSV)
    RealData = DF.loc[((DF['Interval']==Interval) & (DF['Ntrades'] > 0))]
    SMeans = np.zeros(len(Strats))
    for i in range(len(Strats)):
        StratData = RealData.loc[(RealData['Strategy']==Strats[i])]
        print('{:d} test results found for {}'.format(StratData.shape[0],Strats[i]))
        if Yaxis == 'PercentIncrease':
            if Weighting == 'DataSize':
                SMeans[i] = sum(StratData.loc[:,'PercentIncrease']*StratData.loc[:,'BarLength'])/\
                sum(StratData.loc[:,'BarLength'])
            elif Weighting == 'Ntrades':
                SMeans[i] = sum(StratData.loc[:,'PercentIncrease']*StratData.loc[:,'Ntrades'])/\
                sum(StratData.loc[:,'Ntrades'])
    #Get bar positions and labels
    barwidth = 0.75
    barx = np.arange(len(Strats))
    plt.xticks(barx,Strats)
    #Plot
    plt.bar(barx,SMeans,width=barwidth,color='blue')
    plt.axhline(color='Black')
    plt.xlabel('Strategy')
    plt.ylabel('Mean Percent Return',size=16)
    plt.title('Interval = {}, Weighting = {}'.format(Interval,Weighting))
    plt.show()

def BarAverage2(Strats,Interval,StartDate,EndDate,BaselineSYM='SPY',
                Yaxis='PercentIncrease',Weighting='DataSize',CSV='BTArchive1.csv'):
    #Like BarAverage 1, but only take tests of a certain StartDate-EndDate interval, for comparison against a
    #Index-like baseline
    
    #get the Y data
    DF = pd.read_csv(CSV)
    RealData = DF.loc[((DF['Interval']==Interval) & (DF['Ntrades'] > 0) 
                       & (DF['StartDate'] == StartDate) & (DF['EndDate'] == EndDate))]
    SMeans = np.zeros(len(Strats))
    for i in range(len(Strats)):
        StratData = RealData.loc[(RealData['Strategy']==Strats[i])]
        print('{:d} test results found for {}'.format(StratData.shape[0],Strats[i]))
        if Yaxis == 'PercentIncrease':
            if Weighting == 'DataSize':
                SMeans[i] = sum(StratData.loc[:,'PercentIncrease']*StratData.loc[:,'BarLength'])/\
                sum(StratData.loc[:,'BarLength'])
            elif Weighting == 'Ntrades':
                SMeans[i] = sum(StratData.loc[:,'PercentIncrease']*StratData.loc[:,'Ntrades'])/\
                sum(StratData.loc[:,'Ntrades'])
    #Get the baseline
    base = pd.DataFrame() #empty
    if BaselineSYM == 'SPY':
        base = yf.download('SPY',start=StartDate,end=EndDate,interval=Interval)
        if Yaxis == 'PercentIncrease':
            baseline = (base.iloc[-1,3]-base.iloc[0,3])/base.iloc[0,3] #percent return from 1 share, iloc[3] = close

    #Get bar positions and labels
    barwidth = 0.75
    barx = np.arange(len(Strats))
    plt.xticks(barx,Strats)
    #Plot
    plt.bar(barx,SMeans,width=barwidth,color='blue')
    plt.axhline(color='Black')
    if bool(BaselineSYM) and not base.shape[0] == 0: #There is a baseline and it was downloaded successfully
        plt.axhline(y=baseline,color='red')    
    plt.xlabel('Strategy')
    plt.ylabel('Mean Percent Return',size=16)
    plt.title('Interval = {}, Weighting = {}, {} to {}, Baseline = {}'.format(Interval,Weighting,StartDate,EndDate,
                                                                             BaselineSYM))
    plt.show()

def StratDist(Strat,Interval,Xaxis='PercentIncrease',Yaxis='Ntrades',CSV='BTArchive1.csv'):
    #Somewhat modular function for looking at the performance of one strategy
    #basic use is plotting the number of trades / data length of a test result versus performance to see if
    #success is random, or if the degree of success is statistically "normal" (bell curve shaped)
    
    #Get the data
    DF = pd.read_csv(CSV)
    RealData = DF.loc[((DF['Interval']==Interval) & (DF['Ntrades'] > 0) 
                       & (DF['Strategy'] == Strat))]
    print('{:d} test results found for {}'.format(RealData.shape[0],Strat))
    if Xaxis == 'PercentIncrease' and Yaxis == 'Ntrades': #because I want pretty red and green colors
        Xpos = RealData.loc[(RealData['PercentIncrease'] > 0),'PercentIncrease']
        Xneg = RealData.loc[(RealData['PercentIncrease'] <= 0),'PercentIncrease']
        Ypos = RealData.loc[(RealData['PercentIncrease'] > 0),'Ntrades']
        Yneg = RealData.loc[(RealData['PercentIncrease'] <= 0),'Ntrades']
        Y = RealData.loc[:,'Ntrades']
    #if Yaxis == 'Ntrades':
        #Y = RealData.loc[:,'Ntrades']
    elif Xaxis == 'PercentIncrease' and Yaxis == 'DataSize': 
        Xpos = RealData.loc[(RealData['PercentIncrease'] > 0),'PercentIncrease']
        Xneg = RealData.loc[(RealData['PercentIncrease'] <= 0),'PercentIncrease']
        Ypos = RealData.loc[(RealData['PercentIncrease'] > 0),'BarLength']
        Yneg = RealData.loc[(RealData['PercentIncrease'] <= 0),'BarLength']
        Y = RealData.loc[:,'BarLength']
    
    #Plot and label
    #plt.plot(X,Y,color='blue',linestyle='',marker='D')
    if Xaxis == 'PercentIncrease':
        plt.plot(Xpos,Ypos,color='green',linestyle='',marker='D')
        plt.plot(Xneg,Yneg,color='red',linestyle='',marker='D')
    plt.axvline(x=0,color='black',linestyle='solid')
    #plt.gca().set_ylim(bottom=0) #locks bottom y limit at 0
    plt.ylim(0,max(Y)*1.1)
    plt.xlabel(Xaxis,size=16)
    plt.ylabel(Yaxis,size=16)
    plt.title('Strategy = {}, Interval = {}'.format(Strat,Interval))
    plt.show()

#Do Stuff!
StratList = ['Scalp','Scalp4','Scalpy','Scalpy3','Scalpy2','Scalp2']
#this variable must be present!
    
SYMtxt = "S&P500SYM.txt"
Day2 = '2020-04-15'
Day1 = (dt.datetime.strptime(Day2,'%Y-%m-%d')-dt.timedelta(days=50)).strftime('%Y-%m-%d')


for Strat in StratList:
    Inputs = getInputs_SYMS(50,'S&P500SYM.txt',Day1,Day2,'2m')
    for I in Inputs:
        testInput(I,Strat)

BarAverage2(StratList,'2m',Day1,Day2,Weighting='DataSize')

    

    


    
            
            


