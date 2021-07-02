#!/bin/env python3
import os
import sys
import datetime
import time
import argparse
from bs4 import BeautifulSoup
import pandas

class HtmlToCsv:
	def __init__(self, htmldate):
		try:
			datetime.datetime.strptime(htmldate, '%Y%m%d')
			self.htmldate = htmldate
			self.logWriter = open('./log/htmltocsv.log', 'a', encoding='utf-8')
			os.makedirs('unfiltered_csv', exist_ok=True)
			os.makedirs('unfiltered_csv/d_ido', exist_ok=True)
		except ValueError:
			print('Invalid time format')
			sys.exit(1)
		except IOError:
			print('IO error')
			sys.exit(2)

		if not os.path.exists(f'source_dl/d_ido/{self.htmldate}.txt'):
			print('No source found for given date')
			sys.exit(3)

		self.log('Starting application..')
		convStartTime = time.time()

		if self.convert():
			convFinishTime = time.time()
			self.log(f'Successfully converted source({self.htmldate}) to csv')
			self.log(f'Took {convFinishTime - convStartTime} seconds')
		else:
			self.log('Failed conversion')
			sys.exit(4)
		
		self.log('Quitting..')
		self.logWriter.close()
	
	def log(self, msg):
		currtimestamp = str(datetime.datetime.now())
		print(f'{currtimestamp}: {msg}')
		self.logWriter.write(f'{currtimestamp}: {msg}\n')

	def convert(self):
		with open(f'source_dl/d_ido/{self.htmldate}.txt', 'r', encoding='utf-8') as fp:
			soup = BeautifulSoup(fp, 'html.parser')

			html_table = soup.find('table', class_='tt').find_all('tr')[:0:-1]
			headers = ['domain', 'igenylo', 'date']
			data = []
			for elem in html_table:
				sub_data = []
				# domain
				sub_data.append(elem.td.next_sibling.get_text())
				# igenylo
				sub_data.append(elem.td.next_sibling.next_sibling.get_text().strip().replace('"', '').replace('\'', '').replace('\\', '').replace(';', ''))
				# date
				sub_data.append(elem.td.next_sibling.next_sibling.next_sibling.get_text())
				data.append(sub_data)

			pandas.DataFrame(data).to_csv(f'unfiltered_csv/d_ido/{self.htmldate}.csv', header=headers, index=False, quoting=1)
		
		if os.path.getsize(f'unfiltered_csv/d_ido/{self.htmldate}.csv') > 500:
			return True
		else:
			return False

parser = argparse.ArgumentParser()
parser.add_argument('htmldate')
args = parser.parse_args()

h = HtmlToCsv(args.htmldate)
