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

class MomentumBasedTacticalAllocation(QCAlgorithm):
    
    def Initialize(self):
        
        self.SetStartDate(2007, 8, 1) 
        self.SetEndDate(2010, 8, 1)
        #set starting cash for backtesting
        self.SetCash(3000)  
        
        ###Setting up tactical asset allocation
        #subscribe to SPY - S&P500 - using daily resolution
        self.spy = self.AddEquity("SPY", Resolution.Daily)  
        #subscribe to BND - Vanguarg total Bond market ETF - daily resolution
        self.bnd = self.AddEquity("BND", Resolution.Daily)  
        #Set up 50-day Momentum Percentage indicatiors for both securities
        self.spyMomentum = self.MOMP("SPY", 50, Resolution.Daily) 
        self.bondMomentum = self.MOMP("BND", 50, Resolution.Daily) 
        #set SPY benchmark
        self.SetBenchmark(self.spy.Symbol)  
        #warm up algorithm for 50 days to populate the indicators prior to the start date
        self.SetWarmUp(50) 
  
    def OnData(self, data):
        #check if indicators are ready
        if self.IsWarmingUp:
            return
        
        ###limit trading to happen once per week
        #sets trades to occur on tuesdays, with market orders being filled on the next day (given daily resolution), meaning trades are placed on wednesdays
        if self.Time.weekday() != 1:
            return
        ###using the signal to flip:
        #if SPY has more upward momentum than BND, then liquidate all holdings in BND and allocate 100% of equity to SPY
        if self.spyMomentum.Current.Value > self.bondMomentum.Current.Value:
            self.Liquidate(bnd.symbol)
            self.SetHoldings("SPY", 1) SetHoldings method automatically calculates the number of asset units to purchase according to the fraction of the portfolio value provided.
        #otherwise, liquidate all SPY holdings and allocate 100% of portfolio to BND
        else:
            self.Liquidate("SPY")
            self.SetHoldings("BND", 1)
