from clr import AddReference
AddReference("System")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *
from QuantConnect.Securities import *
from QuantConnect.Data.Market import *
from QuantConnect.Orders import *
from datetime import datetime

### Places trades if prices break out of opening range

class OpeningRangeBreakout(QCAlgorithm):
    #declare global variable openingBar
    openingBar = None 
    
    def Initialize(self):
        self.SetStartDate(2018, 7, 10)  
        self.SetEndDate(2019, 6, 30)  
        self.SetCash(100000)
        self.AddEquity("TSLA", Resolution.Minute)
        #consolidate tick data into a 30 min bar (TickBar object)
        self.Consolidate("TSLA", timedelta(minutes=30), self.OnDataConsolidated)
        
        #create a scheduled event triggered at 13:30 calling the ClosePositions function, so as to close all open positions at 13:30 each day
        dateRules = self.DateRules.EveryDay("TSLA")
        timeRules = self.TimeRules.At(13,30)
        self.Schedule.On(dateRules, timeRules, self.ClosePositions)
    def OnData(self, data):
        #ensures we only place one position per day
        if self.Portfolio.Invested or self.openingBar is None:
            return
        ### place position on range breakout
        #long 100% tesla if close price is above opening range
        if data["TSLA"].Close > self.openingBar.High:
            self.SetHoldings("TSLA", 1)
        #short 100% tesla if close price is below opening range
        elif data["TSLA"].Close < self.openingBar.Low:
            self.SetHoldings("TSLA", -1)  
    #ensures we are only working with opening data     
    def OnDataConsolidated(self, bar):
        #record first bar on market open
        if bar.Time.hour == 9 and bar.Time.minute == 30:
            self.openingBar = bar
    
    #closes all open positions with a market order and closes any open limit orders
    def ClosePositions(self):
        self.openingBar = None
        self.Liquidate("TSLA")