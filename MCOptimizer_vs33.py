#MCOptimizer_vs33.py

#Monte Carlo optimization for backtrader strategies
#Given a list of params, the strategy class is created and tested against
#random sequences of data sets, producing a mean return
#The mean return is compared against a "highscore" list and placed appropriately
#result is a "highscore" list of the best parameters

#Each strategy gets its own optimizer. why bother changing the script for each new strategy?

import backtrader as bt
import pandas as pd
import yfinance as yf
import talib.abstract as tab
import numpy as np
import datetime as dt
import random, copy

StratName = 'volumestrat33'

HSlen = 16;
ParamDict_Init = {'adx_buy':22,'mfi_buy':25,'ultosc_buy':25,'rsi_buy':32,'minusdi_buy':25,'mfi_sell':63,'adx_sell':22,
                  'plusdi_sell':25,'rsi_sell':73}


class volumestrat33(bt.Strategy):
    #volumestrat33!

#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=4)
        self.emaclose=bt.indicators.EMA(self.data.close, period=4)
        self.emalow=bt.indicators.EMA(self.data.low, period=4)
        
        self.rsi=bt.talib.RSI(self.data.close, timeperiod=14 )
        self.mfi=bt.talib.MFI(self.data.high,self.data.low,self.data.close,self.data.volume, timeperiod=14 )
        self.ultosc=bt.talib.ULTOSC(self.data.high,self.data.low,self.data.close)
        
        self.minusdi=bt.talib.MINUS_DI(self.data.high,self.data.low,self.data.close)
        self.plusdi=bt.talib.PLUS_DI(self.data.high,self.data.low,self.data.close)
     
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)

        #Parameter dictionary for optimization
        #self.pad = pad
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.adx > pad['adx_buy'] and \
            self.mfi < pad['mfi_buy'] and \
            self.ultosc < pad['ultosc_buy'] and \
            self.rsi < pad['rsi_buy']  and \
            self.minusdi > self.plusdi and \
            self.minusdi > pad['minusdi_buy']: \
                self.buy()
                
                
        else:
            if self.mfi > pad['mfi_sell']  and \
            self.adx > pad['adx_sell'] and \
            self.plusdi > pad['plusdi_sell'] and \
            self.minusdi < self.plusdi and \
            self.rsi > pad['rsi_sell']:
                self.sell()
                        
def getpad_Wiggle(pad0,wiggle):
    pad = copy.copy(pad0)
    for k in pad.keys():
        pad[k] += pad[k] * (random.random()-0.5)*2*wiggle
    return pad
    

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

def testInput(Input,StratName,WriteFile=False):
    
    #feed dataframe to cerbro
    datacere = bt.feeds.PandasData(dataname=Input['YDF'])
    
    #create backtrader
    cerebro = bt.Cerebro()
    cerebro.addstrategy(eval(StratName))

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
    
##    print('Used {} on {} from {} to {}'.format(StratName,Input['SYM'],Input['StartDate'],Input['EndDate']))                                                       
##    print('Returned {:.2f}% with {:d} trades'.format(Output['PercentIncrease'],Output['Ntrades']))
##    print('<==========*==========>')
    return Output

def printpad():
    for k in pad.keys():
        print('{}:{:.2f}'.format(k,pad[k]))
        
def testInputs(Inputs,Strat,record='PercentIncrease'): #wrapper for testInput, averages percent return
    average = 0
    for I in Inputs:
        Output = testInput(I,Strat)
        average += Output[record]
    average = average/len(Inputs)
    return average

def plotHS(Highscores):
    fig, axs = plt.subplots(len(pad.keys(), 1))
    for i,k in enumerate(pad.keys()):
        X = []; Y = []
        for score in Highscores:
            X.append(score['pad'][k])
            Y.append(score['ret'])
        axs[i].plot(X,Y)
        axs[i].ylabel(k)
    axs[-1].xlabel('Percent Return')
    plt.show()
                     



EndDate = '2020-04-24'
StartDate = (dt.datetime.strptime(EndDate,'%Y-%m-%d')-dt.timedelta(days=58)).strftime('%Y-%m-%d')
SetUp = True
Highscores = []
pad = ParamDict_Init
while True:
    Inputs = getInputs_SYMS(52,'S&P500_2020Q2SYM.txt',StartDate,EndDate,'2m')
    if SetUp: #Set up Highscores list
        ret0 = testInputs(Inputs,StratName)
        printpad()
        print('Initial Return {:.2f}%'.format(ret0))
        print('<==========*==========>')
        Highscores.append({'pad':copy.copy(pad),'ret':ret0})
                              
    for i in range(HSlen): #Try HSlen number of param sets before getting new Inputs
        pad = getpad_Wiggle(ParamDict_Init,0.2)
        ret = testInputs(Inputs,StratName)
        for j,score in enumerate(Highscores):
            if ret > score['ret']:
                Highscores.insert(j,{'pad':copy.copy(pad),'ret':ret})
                #del Highscores[-1] #Just save every score
                printpad()
                print('Replaced position {:d} with return {:.2f}%'.format(j,ret))
                break
            elif j+1 == len(Highscores): #at the end, having not been any scores on top
                Highscores.append({'pad':copy.copy(pad),'ret':ret})
                #del Highscores[-1] #Just save every score
                printpad()
                print('Replaced position {:d} with return {:.2f}%'.format(j+1,ret))
                print('<==========*==========>')
                break
                
                
                            
                              
    



