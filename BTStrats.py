#BTStrats.py
#repository of backtrader strategy classes because I got tired of them cluttering up the main script
#Gotta love import *

import backtrader as bt
import talib.abstract as tab
import talib as ta
from typing import Dict, List
from pandas import DataFrame, DatetimeIndex, merge
import datetime as dt

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
class Scalp5(bt.Strategy):
 
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
        
        self.mfi=bt.talib.MFI(self.data.high,self.data.low,self.data.close,self.data.volume, timeperiod=14 )
        
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
            if self.mfi < 25  and \
            self.adx > 30 and \
            self.rsi < 29  and \
            self.fastd < 30 and \
            self.fastk > self.fastd and \
            self.fastk < 30:
                self.buy()
                
        else:
            if self.mfi > 75 and \
            self.fastd > 70  and \
            self.rsi > 80  and \
            self.fastk > 70:
                self.sell()

class volumestrat(bt.Strategy):
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=4)
        self.emaclose=bt.indicators.EMA(self.data.close, period=4)
        self.emalow=bt.indicators.EMA(self.data.low, period=4)
        
        
        self.mfi=bt.talib.MFI(self.data.high,self.data.low,self.data.close,self.data.volume, timeperiod=14 )
        self.ultosc=bt.talib.ULTOSC(self.data.high,self.data.low,self.data.close)
        
        self.minusdi=bt.talib.MINUS_DI(self.data.high,self.data.low,self.data.close)
        self.plusdi=bt.talib.PLUS_DI(self.data.high,self.data.low,self.data.close)
     
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.mfi < 85 and \
            self.ultosc < 85 and \
            self.minusdi > 25: \
            #self.minusdi > self.plusdi:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.mfi > 85  and \
            self.ultosc > 85  and \
            self.plusdi > 25:
                self.sell()

class volumestrat2(bt.Strategy):
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=4)
        self.emaclose=bt.indicators.EMA(self.data.close, period=4)
        self.emalow=bt.indicators.EMA(self.data.low, period=4)
        
        
        self.mfi=bt.talib.MFI(self.data.high,self.data.low,self.data.close,self.data.volume, timeperiod=14 )
        self.ultosc=bt.talib.ULTOSC(self.data.high,self.data.low,self.data.close)
        
        self.minusdi=bt.talib.MINUS_DI(self.data.high,self.data.low,self.data.close)
        self.plusdi=bt.talib.PLUS_DI(self.data.high,self.data.low,self.data.close)
     
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.mfi < 20 and \
            self.ultosc < 20 and \
            self.minusdi > 25 and \
            self.minusdi > self.plusdi:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.mfi > 80  and \
            self.ultosc > 80  and \
            self.minusdi > 25 and \
            self.minusdi < self.plusdi:
                self.sell()

class volumestrat3(bt.Strategy):
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=4)
        self.emaclose=bt.indicators.EMA(self.data.close, period=4)
        self.emalow=bt.indicators.EMA(self.data.low, period=4)
        
        
        self.mfi=bt.talib.MFI(self.data.high,self.data.low,self.data.close,self.data.volume, timeperiod=14 )
        self.ultosc=bt.talib.ULTOSC(self.data.high,self.data.low,self.data.close)
        
        self.minusdi=bt.talib.MINUS_DI(self.data.high,self.data.low,self.data.close)
        self.plusdi=bt.talib.PLUS_DI(self.data.high,self.data.low,self.data.close)
     
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.mfi < 20 and \
            self.ultosc < 30 and \
            self.minusdi > 25: \
            #self.minusdi > self.plusdi:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.mfi > 80  and \
            self.ultosc > 70  and \
            self.plusdi > 25:
                self.sell()

class volumestrat4(bt.Strategy):
 
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=4)
        self.emaclose=bt.indicators.EMA(self.data.close, period=4)
        self.emalow=bt.indicators.EMA(self.data.low, period=4)
        
        
        self.mfi=bt.talib.MFI(self.data.high,self.data.low,self.data.close,self.data.volume, timeperiod=14 )
        self.ultosc=bt.talib.ULTOSC(self.data.high,self.data.low,self.data.close)
        
        self.minusdi=bt.talib.MINUS_DI(self.data.high,self.data.low,self.data.close)
        self.plusdi=bt.talib.PLUS_DI(self.data.high,self.data.low,self.data.close)
     
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.mfi < 30 and \
            self.ultosc < 30 and \
            self.minusdi > 20: \
            #self.minusdi > self.plusdi:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.mfi > 85  and \
            self.ultosc > 85  and \
            self.plusdi > 20:
                self.sell()

#write strategy with i in it for iteration later
class volumestrat41(bt.Strategy):
 
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
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)

    def next(self):
        if not self.position: #not in the market
            if self.adx > 23 and \
            self.mfi < 21 and \
            self.ultosc > 40 and \
            self.minusdi > self.plusdi and \
            self.rsi < 35: \
            #self.minusdi > self.plusdi:
                self.buy()
                
                #add plusdi
        else:
            if  self.adx > 23 and \
                self.rsi > 75:
                self.sell()

class volumestrat5(bt.Strategy):
 
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        #populate exponential moving averages
        self.emahigh=bt.indicators.EMA(self.data.high, period=4)
        self.emaclose=bt.indicators.EMA(self.data.close, period=4)
        self.emalow=bt.indicators.EMA(self.data.low, period=4)
        
        
        self.mfi=bt.talib.MFI(self.data.high,self.data.low,self.data.close,self.data.volume, timeperiod=14 )
        self.ultosc=bt.talib.ULTOSC(self.data.high,self.data.low,self.data.close)
        
        self.minusdi=bt.talib.MINUS_DI(self.data.high,self.data.low,self.data.close)
        self.plusdi=bt.talib.PLUS_DI(self.data.high,self.data.low,self.data.close)
     
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.data.open < self.emalow and \
            self.mfi < 30 and \
            self.ultosc < 30 and \
            self.minusdi > 25 and \
            self.minusdi > self.plusdi:
                self.buy()
                
                
        else:
            if self.data.open >= self.emahigh and \
            self.mfi > 85  and \
            self.ultosc > 85  and \
            self.minusdi > 25 and \
            self.minusdi < self.plusdi:
                self.sell()
                
class volumestrat33(bt.Strategy):

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
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.adx > 22 and \
            self.mfi < 25 and \
            self.ultosc < 25 and \
            self.rsi < 32  and \
            self.minusdi > self.plusdi and \
            self.minusdi > 25: \
            #self.minusdi > self.plusdi:
                self.buy()
                
                
        else:
            if self.mfi > 63  and \
            self.adx > 22 and \
            self.plusdi > 25 and \
            self.minusdi < self.plusdi and \
            self.rsi > 73:
                self.sell()
                
#write strategy with i in it for iteration later
class volumestrat34(bt.Strategy): 
    
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
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.adx > 22 and \
            self.mfi < 25 and \
            self.ultosc < 25 and \
            self.rsi < 33  and \
            self.minusdi > self.plusdi and \
            self.minusdi > 25: \
            #self.minusdi > self.plusdi:
                self.buy()
                
                
        else:
            if self.mfi > 63  and \
            self.adx > 22 and \
            self.plusdi > 25 and \
            self.minusdi < self.plusdi and \
            self.rsi > 75:
                self.sell()

#write strategy with i in it for iteration later
class volumestrat35(bt.Strategy):  
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
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)
        
        
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy
#uses indicators to determine buy and sell

    def next(self):
        if not self.position: #not in the market
            if self.adx > 22 and \
            self.mfi < 25 and \
            self.ultosc < 25 and \
            self.rsi < 33  and \
            self.minusdi > self.plusdi and \
            self.minusdi > 25: \
            #self.minusdi > self.plusdi:
                self.buy()
                
                
        else:
            if self.adx > 22 and \
            self.rsi > 75:
                self.sell()


Marketopen = dt.time(9,30)
Marketclose = dt.time(12+4,0)
Earlyclose = dt.time(12+3,30) #30 minutes before close
JBclose = dt.time(12+3,55) #5 minutes before close, catch this time for liquidation
Lateopen = dt.time(10,0) #30 minutes after open
#volumestrat41 variants follow. L = no late trading, E = no early trading,
#Q = liquidates position at day's end
class volumestrat41_L(bt.Strategy):
    #L = no late trading
 
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
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)

    def next(self):
        if self.data.datetime.time() < Earlyclose:
            if not self.position: #not in the market
                if self.adx > 23 and \
                self.mfi < 21 and \
                self.ultosc > 40 and \
                self.minusdi > self.plusdi and \
                self.rsi < 35: \
                #self.minusdi > self.plusdi:
                    self.buy()
                    
                    #add plusdi
            else:
                if  self.adx > 23 and \
                    self.rsi > 75:
                    self.sell()

class volumestrat41_E(bt.Strategy):
    #E = no early trading
 
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
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)

    def next(self):
        if self.data.datetime.time() > Lateopen:
            if not self.position: #not in the market
                if self.adx > 23 and \
                self.mfi < 21 and \
                self.ultosc > 40 and \
                self.minusdi > self.plusdi and \
                self.rsi < 35: \
                #self.minusdi > self.plusdi:
                    self.buy()
                    
                    #add plusdi
            else:
                if  self.adx > 23 and \
                    self.rsi > 75:
                    self.sell()
                    
#Variants of the above, but they're forced to sell everything at the end of the day.             
class volumestrat41_QL(bt.Strategy):
 
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
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)

    def next(self):
        if self.data.datetime.time() < Earlyclose:
            if not self.position: #not in the market
                if self.adx > 23 and \
                self.mfi < 21 and \
                self.ultosc > 40 and \
                self.minusdi > self.plusdi and \
                self.rsi < 35: \
                #self.minusdi > self.plusdi:
                    self.buy()
                    
                    #add plusdi
            else:
                if  self.adx > 23 and \
                    self.rsi > 75:
                    self.sell()
        #Liquidate
        elif self.data.datetime.time() >= Earlyclose:
            if self.position:
                self.sell()

class volumestrat41_QE(bt.Strategy):
 
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
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)

    def next(self):
        if self.data.datetime.time() > Lateopen and self.data.datetime.time() < JBclose:
            if not self.position: #not in the market
                if self.adx > 23 and \
                self.mfi < 21 and \
                self.ultosc > 40 and \
                self.minusdi > self.plusdi and \
                self.rsi < 35: \
                #self.minusdi > self.plusdi:
                    self.buy()
                    
                    #add plusdi
            else:
                if  self.adx > 23 and \
                    self.rsi > 75:
                    self.sell()
        #Liquidate
        elif self.data.datetime.time() >= JBclose:
            if self.position:
                self.sell()

class volumestrat41_Q(bt.Strategy):
 
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
        self.stoch=bt.talib.STOCHF(self.data.high, self.data.low, self.data.close, \
                                   fastk_period=5, slowk_period=3, slowd_period=3)
        self.fastk=self.stoch.fastk
        self.fastd=self.stoch.fastd
        #1 for down, -1 for up
        
        #creat stochastic momentum indicators 
        #1 for down, -1 for up
        #self.fastcross=bt.indicators.CrossOver(self.fastk, self.fastd)
        
        self.cci=bt.talib.CCI(self.data.high,self.data.low,self.data.close, timeperiod=14 )
        #create Average Directional Movement Index
        self.adx=bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=14)

    def next(self):
        if self.data.datetime.time() <= JBclose:
            if not self.position: #not in the market
                if self.adx > 23 and \
                self.mfi < 21 and \
                self.ultosc > 40 and \
                self.minusdi > self.plusdi and \
                self.rsi < 35: \
                #self.minusdi > self.plusdi:
                    self.buy()
                    
                    #add plusdi
            else:
                if  self.adx > 23 and \
                    self.rsi > 75:
                    self.sell()
        #Liquidate
        else:
            if self.position:
                self.sell()
