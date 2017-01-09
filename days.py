#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

class Days:
	def __init__(self, start_str, end_str):
		self.days = []
		day = datetime.timedelta(days=1)
		date = datetime.datetime.strptime(start_str, '%Y-%m-%d').date()
		while str(date) <= end_str:
			self.days.append(str(date))
			date += day

def addDays(config_days, result_list):
	for r in config_days:
		if type(r) is str:
			result_list.append(r)
		else:
			result_list += r.days

# Выходные, которые официально стали рабочими
WORK_DAYS = [
]

# Будни, которые официально стали нерабочими
OFF_DAYS = [
	Days('2017-01-01', '2017-01-08'),
	'2017-02-23',
	'2017-02-24',
	'2017-03-08',
	'2017-05-01',
	'2017-05-08',
	'2017-05-09',
	'2017-06-12',
	'2017-11-06',
]
