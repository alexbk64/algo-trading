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

###<summary>
### A simple buy-and-hold strategy, which uses a dynamically updated stop loss to manage risk in the orders.
### Also plots price and stop levels on a single chart for illustration.
###</summary>

class BuyAndHoldTrailingStop(QCAlgorithm):
    
    # Order ticket for our stop order, Datetime when stop order was last hit
    stopMarketTicket = None
    stopMarketOrderFillTime = datetime.min
    highestSPYPrice = -1
    
    def Initialize(self):
        self.SetStartDate(2018, 12, 1)
        self.SetEndDate(2018, 12, 10)
        self.SetCash(100000)
        spy = self.AddEquity("SPY", Resolution.Daily)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
    def OnData(self, data):
        
        #plot the current SPY price to "Data Chart" on series "Asset Price"
        self.Plot("Data Chart","Asset Price",self.Securities["SPY"].Close)

        #limit trade frequency to 15 days
        if (self.Time - self.stopMarketOrderFillTime).days < 15:
            return

        if not self.Portfolio.Invested:
            self.MarketOrder("SPY", 500) #long 500 shares of SPY
            self.stopMarketTicket = self.StopMarketOrder("SPY", -500, 0.9 * self.Securities["SPY"].Close) #add stop loss at 90% of current price
        
        else:
            
            #plot the moving stop price on "Data Chart" with "Stop Price" series name
            self.Plot("Data Chart","Stop Price", self.stopMarketTicket.Get(OrderField.StopPrice))
            
            # check if the SPY price is higher that highestSPYPrice: if so, update highestSPYPrice to current SPY price
            #update stop price to 90% of new highest recorded SPY price
            if self.Securities["SPY"].Close > self.highestSPYPrice:
                self.highestSPYPrice = self.Securities["SPY"].Close
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.highestSPYPrice * 0.9
                self.stopMarketTicket.Update(updateFields) 
            
    def OnOrderEvent(self, orderEvent):
        
        #only act on fills
        if orderEvent.Status != OrderStatus.Filled:
            return
        
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: 
            self.stopMarketOrderFillTime = self.Time
