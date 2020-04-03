#!/usr/bin/env python
# coding: utf-8

# In[18]:



from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------
import talib.abstract as tab
from typing import Dict, List
from functools import reduce
from pandas import DataFrame, DatetimeIndex, merge
# --------------------------------
import talib as ta
import numpy  # noqa

#to insert config folder
import sys
sys.path.insert(0, '../')


# In[19]:


def populateindicators(dataframe) -> DataFrame:
        dataframe['ema_high'] = tab.EMA(dataframe, timeperiod=5, price='high')
        dataframe['ema_close'] = tab.EMA(dataframe, timeperiod=5, price='close')
        dataframe['ema_low'] = tab.EMA(dataframe, timeperiod=5, price='low')
        stoch_fast = tab.STOCHF(dataframe, 10.0, 3.0, 0.0, 3.0, 0.0)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']
        dataframe['adx'] = tab.ADX(dataframe)

        # required for graphing
        bollinger =ta.BBANDS(data.close,timeperiod=10)
        dataframe['bb_lowerband'] = bollinger[2]
        dataframe['bb_upperband'] = bollinger[0]
        dataframe['bb_middleband'] = bollinger[1]

        return dataframe


# In[20]:


class Scalp(bt.Strategy):
    """
        this strategy is based around the idea of generating a lot of potential buys and make tiny profits on each trade
        we recommend to have at least 60 parallel trades at any time to cover non avoidable losses.
        Recommended is to only sell based on ROI for this strategy
    """ 
#populate a dataframe with indicators
    
    
    
#------------------------------------strategy starts here--------------------------------------------------------------    
    def __init__(self):
        self.indics=populateindicators(self.data)
# if open score is less than ema_low, adx is greater than 30, fastk fastd less than 30, then buy


    def next(self):
        if not self.position:
            if self.indics['open'] < 30 and             self.indics['adx'] > 30 and             self.indics['fastk'] < 30 and             self.indics['fastd'] < 30:
                self.buy(size=100)
                
                
        else:
            if self.indics['open'] < self.indics['ema_low'] and             self.indics['adx'] > 30 and             self.indics['fastk'] < 70 and             self.indics['fastd']< 70:
                self.sell(size=100)



# In[ ]:




