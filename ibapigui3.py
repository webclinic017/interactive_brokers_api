# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 17:21:29 2019

@author: Dennis
"""

import ibapi
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from ibapi.wrapper import EWrapper
from ibapi.client import EClient

from threading import Thread

from time import sleep, strftime, time, localtime

TickerId = int
#ListOfContractDescription = list

class msgHandler(object):
	def handleHistoricalData(self, reqId: int, bar: ibapi.common.BarData):
		pass
	def handleHistoricalDataEnd(self, reqId:int, start:str, end:str):
		pass
	def handlesymbolSamples(self, reqId:int, contractDescriptions:ibapi.common.ListOfContractDescription):
		pass
	def handlefundamentalData(self, reqId:TickerId , data:str):
		pass


class IBWrapper(EWrapper):
	
	def __init__(self):
		EWrapper.__init__(self)
		self.exporter = None
		self.contractDetailsObtained = False
		
	def init_withExporter(self, exporter):
		EWrapper.__init__(self)
		self.exporter = exporter
		self.contractDetailsObtained = False
		
	def historicalData(self, reqId: int, bar: ibapi.common.BarData):
		""" returns the requested historical data bars
		
		reqId - the request's identifier
		date  - the bar's date and time (either as a yyyymmss hh:mm:ssformatted
			string or as system time according to the request)
		open  - the bar's open point
		high  - the bar's high point
		low   - the bar's low point
		close - the bar's closing point
		volume - the bar's traded volume if available
		count - the number of trades during the bar's timespan (only available
			for TRADES).
		WAP -   the bar's Weighted Average Price
			hasGaps  -indicates if the data has gaps or not. """
			
		if self.exporter == None:
			self.logAnswer(ibapi.utils.current_fn_name(), vars())
			return
		else:
			self.exporter.handleHistoricalData(reqId, bar)
	
	def historicalDataEnd(self, reqId:int, start:str, end:str):
		""" Marks the ending of the historical bars reception. """
		if self.exporter == None:
			self.logAnswer(ibapi.utils.current_fn_name(), vars())
			return
		else:
			self.exporter.handleHistoricalDataEnd(reqId, start, end)
	
	def contractDetails(self, reqId:int, contractDetails:ibapi.contract.ContractDetails):
		"""Receives the full contract's definitons. This method will return all
		contracts matching the requested via EEClientSocket::reqContractDetails.
		For example, one can obtain the whole option chain with it."""
		self.resolved_contract = contractDetails.contract
		self.logAnswer(ibapi.utils.current_fn_name(), vars())
		
	def contractDetailsEnd(self, reqId:int):
		"""This function is called once all contract details for a given
		request are received. This helps to define the end of an option
		chain."""
		self.contractDetailsObtained = True
		self.logAnswer(ibapi.utils.current_fn_name(), vars())
	
	def symbolSamples(self, reqId:int, contractDescriptions:ibapi.common.ListOfContractDescription):
		""" returns array of sample contract descriptions """
		if self.exporter == None:
			self.logAnswer(ibapi.utils.current_fn_name(), vars())
			return
		else:
			self.exporter.handlesymbolSamples(reqId, contractDescriptions)
		
	def fundamentalData(self, reqId:TickerId , data:str):
		"""This function is called to receive Reuters global fundamental
		market data. There must be a subscription to Reuters Fundamental set
		up in Account Management before you can receive this data."""
		if self.exporter == None:
			self.logAnswer(ibapi.utils.current_fn_name(), vars())
			return
		else:
			self.exporter.handlefundamentalData(reqId, data)



class IBClient(EClient):
	
	def __init__(self, wrapper):
		EClient.__init__(self, wrapper)


class tApp(IBWrapper, IBClient):
	
	def __init__(self, IPAddress, PortID, ClientID, msgHandler):
		IBWrapper.init_withExporter(self, msgHandler)
		IBClient.__init__(self, wrapper = self)
		
		self.connect(IPAddress, PortID, ClientID)
		
		thread = Thread(target = self.run, name = "Main Thread")
		thread.start()
		
		setattr(self, "_thread", thread)
		
class Application(tk.Frame, msgHandler):
	
	def __init__(self):
		
		msgHandler.__init__(self)
		
		self.root = tk.Tk()
		
		ttk.Frame.__init__(self, self.root)
		
		self.root.title("IB Python API GUI")
		self.root.geometry("800x900")
		#root.attributes("-topmost", True)
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		
		now = strftime('%Y%m%d %H:%M:%S', localtime(int(time())))
		
		self.varDateTimeEnd = tk.StringVar(self.root, value = now)
		self.varDuration = tk.StringVar(self.root, value = '1 M')
		self.varBarSize = tk.StringVar(self.root, value = '1 day')
		self.varTicker = tk.StringVar(self.root, value = 'AAPL')
		
		self.root.mainloop()
		
		
	def create_widgets(self):
		
		#now = strftime('%Y%m%d %H:%M:%S', localtime(int(time())))
		#self.varDateTimeEnd.set(now)
		
		myfont = ('Arial', 10)
		
		self.btnConnect = ttk.Button(self.root, text = "Connect", command = self.connect_to_tws)
		self.btnConnect.grid(row=0, column=0, sticky=tk.W)
		
		self.btnGetBarData = ttk.Button(self.root, text = "GetBarData", command = self.getHistData)
		self.btnGetBarData.grid(row=0, column=1, sticky=tk.W)
		
		self.btnGetFundamentalData = ttk.Button(self.root, text = "GetFundamentalData", command = self.getFundamentalData)
		self.btnGetFundamentalData.grid(row=0, column=2, sticky=tk.W)
		
		self.btnGetContractData = ttk.Button(self.root, text = "SearchContractDetails", command = self.searchContract)
		self.btnGetContractData.grid(row=0, column=3, sticky=tk.W)
		
		self.label_datetime = tk.Label(self.root, font=myfont, text = 'End Datetime').grid(row=3, column=0, padx=5, pady=5)
		self.label_duration = tk.Label(self.root, font=myfont, text = 'Duration').grid(row=3, column=1, padx=0, pady=5)
		self.label_barsize = tk.Label(self.root, font=myfont, text = 'BarSize').grid(row=3, column=2, padx=5, pady=5)
		self.label_ticker = tk.Label(self.root, font=myfont, text = 'Ticker').grid(row=3, column=3, padx=0, pady=5)
		
		self.cbDateTimeEnd = tk.Entry(self.root, font=myfont, textvariable = self.varDateTimeEnd).grid(row=4, column=0)
		
		self.cbDuration = ttk.Combobox(self.root, font = myfont, textvariable = self.varDuration)
		self.cbDuration['values'] = ('1 Y', '1 M', '6 M', '1 D', '7 D')
		self.cbDuration.grid(row=4, column=1, columnspan=1, sticky=tk.W)
		
		self.cbBarSize = ttk.Combobox(self.root, font=myfont, textvariable = self.varBarSize)
		self.cbBarSize['values'] = ('1 day', '1 min', '2 mins', '5 mins')
		self.cbBarSize.grid(row=4, column=2, columnspan=1, sticky=tk.W)
		
		self.cbTicker = tk.Entry(self.root, font=myfont, textvariable = self.varTicker).grid(row=4, column=3)
		
		self.listbox1 = tk.Listbox(self.root, font=("",12), width=75, height=30)
		self.listbox1.grid(row=6, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W)

		self.msgBox = tk.Listbox(self.root, font=("",12), width=75, height=10)
		self.msgBox.grid(row=7, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W)
		
		
	def connect_to_tws(self):
		
		if self.isConnected:
			self.tws_client.disconnect()
			self.btnConnect.config(text = 'Connect')
			self.msgBox.insert(tk.END, "Disconnected from IB")
			self.isConnected = False
		else:
			self.tws_client = tApp('LocalHost', self.port, self.clientID, self)  #loaded itelf as msgHandler
			
			timePassed = 0
			while not(self.tws_client.isConnected()):
				if (timePassed > 5):
					self.msgBox.insert(tk.END, "Waited more than 5 secs to establish connection to TWS")
					return
				sleep(0.1)
				timePassed += 0.1
			
			self.isConnected = True
			self.msgBox.insert(tk.END, "Successfully connected to IB")
			self.btnConnect.config(text = 'Disconnect')
			
	def searchContract(self):
		
		if not(self.isConnected):
			self.msgBox.insert(tk.END, "Not Connected to IB yet")
			return
		
		ticker = self.varTicker.get()
		
		self.msgBox.insert(tk.END, "Searching for "+ticker)
		
		self.contractlist=[]
		self.symbolSearchRecieved = False
		
		self.tws_client.reqMatchingSymbols(reqId = 1, pattern = ticker)
		
		timePassed = 0 
		while not (self.symbolSearchRecieved):
			if (timePassed > 10):
				self.msgBox.insert(tk.END, "Waited more than 10 secs for contract list request")
				return
			sleep(0.1)
			timePassed += 0.1
		
		self.msgBox.insert(tk.END, "Successfully obtained contract list")
		
		for singleContract in self.contractList:
			contractStr = singleContract.contract.__str__()
			self.msgBox.insert(tk.END, contractStr)
		
	def getHistData(self):
		
		if not(self.isConnected):
			self.msgBox.insert(tk.END, "Not Connected to IB yet")
			return
		
		self.listbox1.delete(0, tk.END)
		
		self.contract = ibapi.contract.Contract()
		self.contract.symbol = "AAPL"
		self.contract.secType = "STK"
		self.contract.exchange = "ISLAND"
		self.contract.currency = "USD"
		#self.contract.lastTradeDateOrContractMonth = "201801"
		
		self.tws_client.contractDetailsObtained = False
		
		self.msgBox.insert(tk.END, "Requesting Contract Details")
		self.tws_client.reqContractDetails(reqId = 2, contract=self.contract)
		
		timePassed = 0 
		while not (self.tws_client.contractDetailsObtained):
			if (timePassed > 10):
				self.msgBox.insert(tk.END, "Waited more than 10 secs for contract details request")
				return
			sleep(0.1)
			timePassed += 0.1
		
		self.msgBox.insert(tk.END, "Successfully obtained contract details")
		aContract = self.tws_client.resolved_contract
		
		#aContract.includeExpired = True
		
		now = self.varDateTimeEnd.get()
		duration = self.varDuration.get()
		barsize = self.varBarSize.get()
		
		self.tws_client.reqHistoricalData(reqId = 1, 
									contract = aContract,
									endDateTime = now,
									durationStr = duration,
									barSizeSetting = barsize,
									whatToShow = "TRADES",
									useRTH = 1,
									formatDate = 1,
									keepUpToDate = False,
									chartOptions = [])
		
	def getFundamentalData(self):
		
		if not(self.isConnected):
			self.msgBox.insert(tk.END, "Not Connected to IB yet")
			return
		
		self.listbox1.delete(0, tk.END)
		
		self.contract = ibapi.contract.Contract()
		self.contract.symbol = "AAPL"
		self.contract.secType = "STK"
		self.contract.exchange = "ISLAND"
		self.contract.currency = "USD"
		#self.contract.lastTradeDateOrContractMonth = "201801"
		
		self.tws_client.contractDetailsObtained = False
		
		self.msgBox.insert(tk.END, "Requesting Contract Details")
		self.tws_client.reqContractDetails(reqId = 2, contract=self.contract)
		
		timePassed = 0 
		while not (self.tws_client.contractDetailsObtained):
			if (timePassed > 10):
				self.msgBox.insert(tk.END, "Waited more than 10 secs for contract details request")
				return
			sleep(0.1)
			timePassed += 0.1
		
		self.msgBox.insert(tk.END, "Successfully obtained contract details")
		aContract = self.tws_client.resolved_contract
		
		self.tws_client.reqFundamentalData(reqId = 1, 
									contract = aContract,
									reportType = "ReportsFinStatements",
									fundamentalDataOptions=[])
		
	def disconnect(self):
		if self.isConnected:
			self.tws_client.disconnect()
			self.isConnected = False
			
			
	#handlers
	
	def handleHistoricalData(self, reqId: int, bar: ibapi.common.BarData):
		str_open = str(bar.open)
		str_high = str(bar.high)
		str_low = str(bar.low)
		str_close = str(bar.close)
		str_volume = str(bar.volume)
		
		histData = bar.date + "," + str_open + "," + str_high + "," + str_low + "," + str_close + "," + str_volume
		
		self.listbox1.insert(tk.END, histData)
		
	def handleHistoricalDataEnd(self, reqId:int, start:str, end:str):
		self.msgBox.insert(tk.END, "Finished downloading historical data")
		
	def handlefundamentalData(self, reqId:TickerId , data:str):
		self.listbox1.insert(tk.END, data)
		#self.msgBox.insert(tk.END, "Finished downloading historical data")
		
	def handlesymbolSamples(self, reqId:int, contractDescriptions:ibapi.common.ListOfContractDescription):
		self.symbolSearchRecieved = True
		self.contractList = contractDescriptions
	
	def on_closing(self):
		if messagebox.askokcancel("Quit", "Do you want to quit?"):
			self.disconnect()
			self.root.destroy()




app = Application()


