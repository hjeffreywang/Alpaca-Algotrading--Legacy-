#Systematic Backtester.py

#Beginnings of systematic iterative strategy testing. The backtrader cerebro run is contained within a function with
#strictly defined inputs and outputs. Outcomes of tests are written to a CSV file, which can be analyzed for trends

#TODO:


#asset optimizer that has one strategy choose stock symbols that it's more successful
#with to trade with more often. May require a much longer data set though.



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

from BTStrats import *

MASTERDIR = '/Users/Blight/Pygrams/ALPACA'
os.chdir(MASTERDIR)

###BT STRAT CLASSES (skip this part)
        



###FUNCTIONS==========================================================

def writeInputOutput(Strategy,Input,Output,CSVfilename):
#The column order in the CSV is currently: 
#Timestamp; Strategy; Symbol; StartDate; EndDate; DataSize; Set; PercentIncrease; Ntrades; WinRate;
#SQN, AvgHold, AvgHoldW, AvgHoldL
#Strategy is the strategy name string, input/output are dicts, CSVfilename= BTArchive2.csv
#Assumes a such a file already exists, copypaste the above line into a txt, call it XXXX.csv

    if not CSVfilename in os.listdir(): #don't write a new file. 
        print(CSVfilename+' not found, creating new')
        CSV = open(CSVfilename,'w')
        CSV.write('Timestamp,Strategy,Symbol,StartDate,EndDate,DataSize,Set,PercentIncrease,Ntrades,'+
                  'WinRate,SQN,AvgHold,AvgHoldW,AvgHoldL,InMarketPer\n')
        CSV.close()
    with open(CSVfilename,'a') as CSV: #append mode
        Timestamp = str(int(time.time())) #"ID number"
        time.sleep(1)
        PercentIncreasestr = '{:.2f}'.format(Output['PercentIncrease'])
        WinRatestr = '{:.2f}'.format(Output['WinRate'])
        SQNstr = '{:.2f}'.format(Output['SQN'])
        AvgHoldstr = '{:.2f}'.format(Output['AvgHold'])
        AvgHoldWstr = '{:.2f}'.format(Output['AvgHoldW'])
        AvgHoldLstr = '{:.2f}'.format(Output['AvgHoldL'])
        InMarketPerstr = '{:.2f}'.format(Output['InMarketPer'])
        
        CSV.write(Timestamp+','+Strategy+','+Input['SYM']+','+Input['StartDate']+','+Input['EndDate']
                  +','+str(Input['YDF'].shape[0])+','+
                 Input['Set']+','+PercentIncreasestr+','+str(Output['Ntrades'])+','+WinRatestr+','+
                  SQNstr+','+AvgHoldstr+','+AvgHoldWstr+','+AvgHoldLstr+','+InMarketPerstr+"\n")
        CSV.close()

pickledir = "SYMpickles/"
def getInput_pickle(SYM,StartDate,EndDate):
    #Assumes folder SYMpickles exists and all files have format SYM.pickle
    try:
        PDF = pd.read_pickle(pickledir+SYM+'.pickle')
    except FileNotFoundError:
        print(SYM+' not found')
        return
    startD = dt.datetime.strptime(StartDate,'%Y-%m-%d').date()
    endD = dt.datetime.strptime(EndDate,'%Y-%m-%d').date()
    MaxDate = PDF.iloc[0,-1] #should be 2020-04-24
    MinDate = PDF.iloc[-1,-1] #should be 2008-01-02
    if startD < MinDate:
        print('Start Date out of range')
        return
    elif endD > MaxDate:
        print('End Date out of range')
        return
    elif endD < startD:
        print('Your dates are backwards')
        return
    #Filter by ask date
    DF = PDF.loc[((PDF['date'] >= startD) & (PDF['date'] <= endD))]
    #Clean out impossible non-market trading times too
    DF = DF.tz_convert('US/Eastern')
    Marketopen = dt.time(9,30)
    Marketclose = dt.time(12+4,0)
    DF = DF.loc[((DF.index.time >= Marketopen) & (DF.index.time <= Marketclose))]
    #And sort the darn thing since the times are ascending but not the dates!
    DF = DF.sort_index(ascending=True)

    #Pickle dataframe: timestamp open, high, low, close, volume, date
    #Yahoo dataframe: open, high, low, close, volume
    return {'YDF':DF,'SYM':SYM,'StartDate':StartDate,
                       'EndDate':EndDate,
                      'Set':''}
    #assumes pickle has 1m bar granularity 
        
    

def testInput(Input,StratName,WriteFile='BTArchive2.csv'):
    #feed dataframe to cerbro
    if Input == None:
        print('Empty Input')
        return
    datacere = bt.feeds.PandasData(dataname=Input['YDF'])
    
    #create backtrader
    cerebro = bt.Cerebro()
    #Find strategy. I could do this with eval(StartName), but that's not safe
    if StratName in AllStrats:
        cerebro.addstrategy(eval(StratName)) #this eval isn't too much of a security risk, is it?
    else:
        print('StratName not Found')
        return

    #set up cerebro
    StartCash = 100000 #I would like this number for later
    cerebro.broker.setcash(StartCash)
    cerebro.broker.setcommission(commission=0.0)
    cerebro.addsizer(bt.sizers.AllInSizerInt)
    #All In Sizer always uses maximum cash possible, meaning we can divide the profit by the starting cash later to
    #get a normalized percent increase
    cerebro.adddata(datacere)
    #Analyzers. I am not sure how many of these lines are necessary
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    #cerebro.addanalyzer(bt.analyzers.Returns, _name="ret")
    #cerebro.addanalyzer(bt.analyzers.PeriodStats, _name="pstat")
    cerebro.addanalyzer(bt.analyzers.Transactions, _name="trans")
    
    #Run
    try:
        result = cerebro.run()
        analysis_ta = result[0].analyzers.ta.get_analysis()
        #analysis_trans = pd.DataFrame(result[0].analyzers.trans.get_analysis())
        analysis_sqn = result[0].analyzers.sqn.get_analysis()
    except:
        print('Error in Cerebro')
        return False
    #Get the output
    Ntrades = analysis_ta['total']['closed']
    if analysis_ta['total']['closed'] - analysis_ta['total']['total'] < -1:
        print('WARNING: open trades exceed closed trades')
    WinRate = analysis_ta['won']['total']/Ntrades
    PercentIncrease = analysis_ta['pnl']['gross']['total']/StartCash*100
    AvgHold = analysis_ta['len']['average']/60 #hours, assumes 1m barwidth
    InMarketPer = analysis_ta['len']['total']/len(Input['YDF']) #How often in the market
    AvgHoldW = analysis_ta['len']['won']['average']/60
    AvgHoldL = analysis_ta['len']['lost']['average']/60
    SQN = analysis_sqn['sqn']
    Output = {'PercentIncrease':PercentIncrease,'Ntrades':Ntrades,'WinRate':WinRate,'AvgHold':AvgHold,
              'AvgHoldW':AvgHoldW,'AvgHoldL':AvgHoldL,'SQN':SQN,'InMarketPer':InMarketPer}
    
    if bool(WriteFile):
        writeInputOutput(StratName,Input,Output,WriteFile)
    print('Used {} on {} from {} to {}'.format(StratName,Input['SYM'],Input['StartDate'],Input['EndDate']))                                                       
    print('Returned {:.2f}% with {:d} trades'.format(Output['PercentIncrease'],Output['Ntrades']))
    print('WinRate = {:.2f}, SQN = {:.2f}, '.format(WinRate,SQN))
    print('Average Hold = {:.2f} Hours, {:.2f} for wins, {:.2f} for losses'.format(AvgHold,AvgHoldW,AvgHoldL))
    print('In market {:.2f}% of the time'.format(InMarketPer*100))
    print('<==========*==========>')
    return Output

def BHList(SYMtxt,StartDate,EndDate,Base='SPY'):
    #Simple fuctions that compares the individual returns of each asset in the SYMtxt to SPY over the start-end interval
    #Aggregate mean return appears as a line, individual assets as points
    #Meant to check the efficacy of stock pick lists over various timeframes
    Ndays = dt.datetime.strptime(EndDate,'%Y-%m-%d').date().toordinal()-\
            dt.datetime.strptime(StartDate,'%Y-%m-%d').date().toordinal()
    
    #Open SYMtxt and get Data
    Smean = 0
    Returns = []
    f = open(SYMtxt)
    flines=f.readlines()
    f.close()
    for l in flines:
        SYM = l.rstrip("\n")
        YDF = yf.download(SYM,start=StartDate,end=EndDate,interval='1d')
        if not YDF.shape[0] == 0:
            Returns.append((YDF.iloc[-1,3]-YDF.iloc[0,3])/YDF.iloc[0,3])
            Smean += Returns[-1]
    Smean = Smean/len(Returns)
    #Baseline
    if Base == 'SPY':
        BSYM = 'SPY'    
    BYDF = yf.download(BSYM,start=StartDate,end=EndDate,interval='1d')
    if not BYDF.shape[0] == 0:
        Baseline = (BYDF.iloc[-1,3]-BYDF.iloc[0,3])/BYDF.iloc[0,3]*100
    else:
        return
    #Plot
    plt.plot(Returns,linestyle='',marker='d',color='blue')
    plt.axhline(y=Smean,color='black',label='average')
    plt.axhline(y=Baseline,color='red',label=Base)
    plt.ylabel('Return')
    plt.title(SYMtxt.rstrip("SYM.txt")+' '+str(Ndays)+' days')
    plt.legend(loc='best')
    plt.show()
    
    
            
    
###ANALYSIS FUNCTIONS==========================================================

def BarAverage1(Strats,Yaxis,Weighting='DataSize',CSV='BTArchive2.csv',
                Set = False):
    #Runs through lines in the CSV archive, averaging together all lines of the same strat name tested 
    #over the specified interval. The average can be weighted by the total length of the input data used or the 
    #number of trades made
    
    #get the Y data
    DF = pd.read_csv(CSV)
    if bool(Set):
        RealData = DF.loc[((DF['Ntrades'] > 0) & (DF['Set'] == Set))]
    else:
        RealData = DF.loc[((DF['Ntrades'] > 0))]
    SMeans = np.zeros(len(Strats))
    WSD = np.zeros(len(Strats)) #weighted standard deviation
    for i in range(len(Strats)):
        StratData = RealData.loc[(RealData['Strategy']==Strats[i])]
        print('{:d} test results found for {}'.format(StratData.shape[0],Strats[i])) 
        SMeans[i] = sum(StratData.loc[:,Yaxis]*StratData.loc[:,Weighting])/sum(StratData.loc[:,'DataSize'])
        WSD[i] = (sum(StratData.loc[:,Weighting]*(StratData.loc[:,Yaxis]-SMeans[i])**2)/
                  sum(StratData.loc[:,Weighting]))**0.5
            
    #Get bar positions and labels
    barwidth = 0.75
    barx = np.arange(len(Strats))
    plt.xticks(barx,Strats)
    #Plot
    plt.bar(barx,SMeans,width=barwidth,color='darkviolet',yerr=WSD)
    plt.axhline(color='Black')
    plt.xlabel('Strategy')
    plt.ylabel('Mean '+Yaxis,size=16)
    plt.title('Weighting = {}'.format(Weighting))
    plt.show()

def BarAverage2(Strats,Yaxis,StartDate,EndDate,BaselineSYM='SPY',
                Weighting='DataSize',CSV='BTArchive2.csv',Set=False):
    #Like BarAverage 1, but can get SPY as a baseline is using Yaxis = PercentReturn beccause date-restricted
    
    #get the Y data
    DF = pd.read_csv(CSV)
    if bool(Set):
        RealData = DF.loc[((DF['Ntrades'] > 0) 
                           & (DF['StartDate'] == StartDate) & (DF['EndDate'] == EndDate)
                           & (DF['Set']==Set))]
    else:
        RealData = DF.loc[((DF['Ntrades'] > 0) 
                           & (DF['StartDate'] == StartDate) & (DF['EndDate'] == EndDate))]
    SMeans = np.zeros(len(Strats))
    WSD = np.zeros(len(Strats))
    for i in range(len(Strats)):
        StratData = RealData.loc[(RealData['Strategy']==Strats[i])]
        print('{:d} test results found for {}'.format(StratData.shape[0],Strats[i]))
        StratData = RealData.loc[(RealData['Strategy']==Strats[i])]
        print('{:d} test results found for {}'.format(StratData.shape[0],Strats[i])) 
        SMeans[i] = sum(StratData.loc[:,Yaxis]*StratData.loc[:,Weighting])/sum(StratData.loc[:,'DataSize'])
        WSD[i] = (sum(StratData.loc[:,Weighting]*(StratData.loc[:,Yaxis]-SMeans[i])**2)/
                  sum(StratData.loc[:,Weighting]))**0.5
        
    #Get the baseline
    base = pd.DataFrame() #empty
    if Yaxis == 'PercentIncrease' and BaselineSYM == 'SPY':
        base = yf.download('SPY',start=StartDate,end=EndDate,interval='1d')
        baseline = (base.iloc[-1,3]-base.iloc[0,3])/base.iloc[0,3]*100 #percent return from 1 share, iloc[3] = close

    #Get bar positions and labels
    barwidth = 0.75
    barx = np.arange(len(Strats))
    plt.xticks(barx,Strats)
    #Plot
    plt.bar(barx,SMeans,width=barwidth,color='darkviolet',yerr=WSD)
    plt.axhline(color='Black')
    if Yaxis == 'PercentIncrease' and not base.shape[0] == 0: #There is a baseline and it was downloaded successfully
        plt.axhline(y=baseline,color='red')    
    plt.xlabel('Strategy')
    plt.ylabel('Mean '+Yaxis,size=16)
    if Yaxis == 'PercentIncrease' and not base.shape[0] == 0:
        plt.title('Weighting = {}, {} to {}, Baseline = {}'.format(Weighting,StartDate,EndDate,BaselineSYM))
    else:
        plt.title('Weighting = {}, {} to {}'.format(Weighting,StartDate,EndDate))
    plt.show()

def StratDist(Strat,Xaxis='PercentIncrease',Yaxis='Ntrades',CSV='BTArchive2.csv',Set=False):
    #Somewhat modular function for looking at the performance of one strategy
    #basic use is plotting the number of trades / data length of a test result versus performance to see if
    #success is random, or if the degree of success is statistically "normal" (bell curve shaped)
    
    #Get the data
    DF = pd.read_csv(CSV)
    if bool(Set):
        RealData = DF.loc[((DF['Ntrades'] > 0) 
                           & (DF['Strategy'] == Strat) & (DF['Set'] == Set))]
    else:
        RealData = DF.loc[((DF['Ntrades'] > 0) 
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
        Ypos = RealData.loc[(RealData['PercentIncrease'] > 0),'DataSize']
        Yneg = RealData.loc[(RealData['PercentIncrease'] <= 0),'DataSize']
        Y = RealData.loc[:,'DataSize']
    
    #Plot and label
    #plt.plot(X,Y,color='blue',linestyle='',marker='D')
    if Xaxis == 'PercentIncrease':
        plt.plot(Xpos,Ypos,color='green',linestyle='',marker='d')
        plt.plot(Xneg,Yneg,color='red',linestyle='',marker='d')
        print('{} recorded {:d} positive runs and {:d} negative runs'.format(Strat,len(Xpos),len(Xneg)))
    plt.axvline(x=0,color='black',linestyle='solid')
    #plt.gca().set_ylim(bottom=0) #locks bottom y limit at 0
    plt.ylim(0,max(Y)*1.1)
    plt.xlabel(Xaxis,size=16)
    plt.ylabel(Yaxis,size=16)
    plt.title('Strategy = {}'.format(Strat))
    plt.show()

###META FUNCTIONS============================================================
def testPickles(Strat,StartDate,EndDate,Nsym):
    #one strat at a time because could take a long time. now with Nsym because we have a lot of pickles
    dirlist = os.listdir(pickledir)
    for i,di in enumerate(dirlist):
        if not di.endswith('.pickle'):
            dirlist.remove(di)
    picklist = random.sample(dirlist,Nsym)
    for pickle in picklist:
        Input = getInput_pickle(pickle.rstrip('.pickle'),StartDate,EndDate)
        testInput(Input,Strat)
    

    
    
            
    

#Do Stuff!
ScalpStrats = ['Scalp','Scalp4','Scalpy','Scalpy3','Scalpy2','Scalp2','Scalp5']
VolumeStrats = ['volumestrat','volumestrat2','volumestrat3','volumestrat4','volumestrat5',
                'volumestrat33','volumestrat34','volumestrat35','volumestrat41']
VS41_variants = ['volumestrat41_Q','volumestrat41_L','volumestrat41_E','volumestrat41_QL','volumestrat41_QE']
AllStrats = ScalpStrats+VolumeStrats+VS41_variants #this variable must be present!
TestStrats = ['Scalpy3','Scalp5','volumestrat33','volumestrat41']
    
SYMtxt = "S&P500_2020Q2SYM.txt"
day2 = '2019-05-13'
day1 = (dt.datetime.strptime(day2,'%Y-%m-%d')-dt.timedelta(days=13)).strftime('%Y-%m-%d')

day4 = '2019-05-13'
day3 = (dt.datetime.strptime(day4,'%Y-%m-%d')-dt.timedelta(days=365)).strftime('%Y-%m-%d')

day5 = '2017-07-10'
day6 = (dt.datetime.strptime(day5,'%Y-%m-%d')+dt.timedelta(days=4)).strftime('%Y-%m-%d')

PickleStart = '2008-01-02'
PickleEnd = '2020-04-24'
FinCrisStart = '2008-09-15' #collapse of Lehman brothers
FinCrisEnd = '2009-03-09' #Dow Jones hits a low, marking uptrend
CovidStart = '2020-02-03' #approximate start of coronavirus market meltdown


##I = getInput_pickle('BA',day3,day4)
##O = testInput(I,'volumestrat41')

for strat in TestStrats:
    testPickles(strat,day3,day4,20)
BarAverage2(TestStrats,'PercentIncrease',day3,day4,Weighting='DataSize',Set=False)



#testAllinList("S&P500_2020Q2SYM.txt",AllStrats,day1,day2,'2m')

##for Strat in TestStrats:
##    Inputs = getInputs_SYMS(52,'S&P500_2020Q2SYM.txt',day1,day2,'2m')
##    for I in Inputs:
##        testInput(I,Strat)
##        
##for Strat in StratList:
##    Inputs = getInputs_SYMS(50,'AllAlpacaSYM.txt',Day1,Day2,'2m')
##    for I in Inputs:
##        testInput(I,Strat)

#BarAverage2(TestStrats,'2m',day1,day2,Weighting='DataSize',Set=False)

#StratDist('Scalp','2m',Set=False)

#testList("IBD50_2020-04-13SYM.txt",day3,day4)
#testList("IBD100_2007-07-09SYM.txt",day5,day6)

    

    


    
            
            


