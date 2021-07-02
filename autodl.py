#!/usr/bin/env python3.8
# -*- coding: utf-8 -*

# This script is used to download the list of newly registered and expiring .hu TLD domains from the official domain registry page (domain.hu)
# Recommended schedule frequency is once a day
# Announced domains are listed for up to 14 days (usually 6-7), parked domains for 60 days
# Recommended Python version: 3.8+

import datetime
import os
from pathlib import Path
import random
import requests
import sys
import time

config = {
	"outputDir": Path("source_dl"),
	"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
	"proxy": {
	}
}

class AutoDL:
	_logFile = "autodl.log"
	_logWriter = None
	_urls = {
		"d_abc": "https://info.domain.hu/varolista/hu/abc.html",
		"d_ido": "https://info.domain.hu/varolista/hu/ido.html",
		"p_abc": "https://info.domain.hu/parkolas/hu/abc.html",
		"p_ido": "https://info.domain.hu/parkolas/hu/ido.html"
	}

	def download(self):
		currdate = datetime.date.today().strftime("%Y%m%d")
		uaheader = {'User-Agent': self._userAgent}
		retries = 5
		r = None

		for key in self._urls:
			url = self._urls[key]
			self.log(f"Downloading {key}")
			
			for i in range(1, retries+1):
				time.sleep(random.randint(5, 10))
				try:
					r = requests.get(url, proxies=self._proxy, headers=uaheader)

					if r.status_code != 200 or len(r.text) < 100:
						raise Exception

					# save original response in case encoding gets changed without noticing
					open(self._downloadPath / f"{key}/{currdate}.txt", "wb").write(r.content)
					
					self.log("Done")
					break
				except:
					if i != retries:
						self.log(f"Failed to download {key} (attemp {i}) or cannot write to output, retrying..")
					else:
						self.log(f"Failed to download {key} at last attempt or cannot write to output, quitting.")
						sys.exit(2)

	def log(self, msg):
		print(f"{str(datetime.datetime.now())}: {msg}")
		self._logWriter.write(f"{str(datetime.datetime.now())}: {msg}\n")

	def __init__(self, config):
		self._downloadPath = config["outputDir"]

		try:
			self._logWriter = open(self._logFile, "a", encoding="utf-8")

			# make dirs for output if not existing
			os.makedirs(self._downloadPath, exist_ok=True)
			for key in self._urls:
				os.makedirs(self._downloadPath / key, exist_ok=True)
		except:
			print("IO error")
			sys.exit(1)
		
		self._proxy = config["proxy"]
		self._userAgent = config["userAgent"]

		self.log("Starting application..")
		self.download()
		self.log("Download finished, closing application..")

		self._logWriter.close()

hud = AutoDL(config)
