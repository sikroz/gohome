#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import os
import config
IN = "in"
OUT = "out"
INCLUDE_DAYS = config.ADD_WORK_DAYS

EXCLUDE_DAYS = config.SUB_WORK_DAYS

now = datetime.datetime.now()
#now = datetime.datetime(2016, 3, 31, 23, 0, 0)
today = now.date()

def readStatFile(month):
	statfile = open(os.path.expanduser('%s/%02d' % (config.JOBSTAT_DIRECTORY, month)))
	inouts = []
	for line in statfile:
		line = line.strip()
		date, time, inout = line.split(" ")
		date_time = datetime.datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
		date = date_time.date()
		time = date_time

		if len(inouts) and inout == inouts[-1][2]:
			print "Double {}: '{} {}', '{} {}'".format(inout, inouts[-1][0], inouts[-1][1], date, time)
			continue

		inouts.append((date, time, inout))
	return inouts

def mergeByDate(inoutslist):
	#Объединить входы выходы по датам
	result = {}
	for i in inoutslist:
		date = i[0]
		time = i[1]
		inout = i[2]
		if date in result:
			result[date].append((time, inout))
		else:
			result[date] = [(time, inout)]
	return result

def daySeconds(inoutsday):
	if inoutsday[0][1] == 'out':
		d = inoutsday[0][0]
		d = datetime.datetime(d.year, d.month, d.day, 0, 0, 0)
		inoutsday.insert(0, (d, 'in'))
	if inoutsday[-1][1] == 'in':
		d = inoutsday[-1][0]
		d = datetime.datetime(d.year, d.month, d.day, 23, 59, 59)
		inoutsday.append((d, 'out'))

	inseconds = 0
	if len(inoutsday) % 2:
		print "То ли не вышел, то ли не вошел"
		exit(1)
	i = 0
	while i < len(inoutsday):
		_in = inoutsday[i]
		_out = inoutsday[i+1]
		if _in[1] != IN:
			print "Вместо входа - выход"
			exit(1)
		if _out[1] != OUT:
			print "Вместо выхода - вход"
			exit(1)

		_in_time = _in[0]
		_out_time = _out[0]
		inseconds += (_out_time - _in_time).seconds
		i += 2

	fullday = inoutsday[-1][0] - inoutsday[0][0]
	outseconds = fullday.seconds - inseconds
	print secondsToStrtime(inseconds)
	return (inseconds, outseconds)

def tillYesterdaySeconds(inoutsdict):
	result = 0
	day = datetime.timedelta(days=1)
	first_of_month = datetime.date(today.year, today.month, 1)
	it = first_of_month
	while it < today:
		if it in inoutsdict:
			inouts = inoutsdict[it]
			result += daySeconds(inouts)[0]
		it += day
	return result

def needMinsPerDay():
	return config.NEED_MINUTES_PER_DAY

def tillYesterdayDays(inoutsdict):
	result = 0
	day = datetime.timedelta(days=1)
	first_of_month = datetime.date(today.year, today.month, 1)
	it = first_of_month
	while it < today:
		if str(it) not in EXCLUDE_DAYS:
			result += 1
		it += day
	return result

def plus(time, seconds):
	dt = t2dt(time) + datetime.timedelta(seconds=seconds)
	return datetime.time(dt.hour, dt.minute, dt.second)

def t2dt(time):
	return datetime.datetime(today.year, today.month, today.day, time.hour, time.minute, time.second)

def secondsToStrtime(seconds):
	minutes = seconds / 60
	h = minutes / 60
	m = minutes % 60
	return "%02d:%02d:%02d" % (h, m, seconds % 60)

def printTotal(total, shouldbe):
	need = shouldbe - total
	print 'Total: %s / %s. Diff %s%s. Go: %s' % (
		secondsToStrtime(total),
		secondsToStrtime(shouldbe),
		'-' if need < 0 else '',
		secondsToStrtime(abs(need)),
		datetime.datetime.strftime(now + datetime.timedelta(seconds=need), '%H:%M:%S'))

def fillExcludeDays():
	day = datetime.timedelta(days=1)
	first_of_month = datetime.date(today.year, today.month, 1)
	it = first_of_month
	while it <= today:
		if it.weekday() in (5, 6) and str(it) not in INCLUDE_DAYS:
			EXCLUDE_DAYS.append(str(it))
		it += day

def main():
	fillExcludeDays()
	inouts = readStatFile(now.month)
	inouts = mergeByDate(inouts)
	#Сколько отработали за предыдущие дни
	prev_seconds = tillYesterdaySeconds(inouts)
	#Сколько отработали сегодня
	if today in inouts and str(today) not in EXCLUDE_DAYS:
		today_inouts = inouts[today]
		i_am_in = False
		if len(today_inouts) % 2 and today_inouts[-1][1] == IN:
			today_inouts.append((now, OUT)) #Типа вышли только что
			i_am_in = True
		today_seconds_work, today_seconds_away = daySeconds(today_inouts)
		camein = t2dt(today_inouts[0][0])
		print 'Came in: ' + datetime.datetime.strftime(camein, '%H:%M:%S')
		print 'Was away: %s' % (secondsToStrtime(today_seconds_away))
		gohome = t2dt(plus(plus(camein, today_seconds_away), needMinsPerDay() * 60))
		print 'Go home: ' + datetime.datetime.strftime(gohome, '%H:%M:%S')
		if i_am_in:
			if gohome > now:
				d = gohome - now
				print 'Time left {}'.format(secondsToStrtime(d.seconds))
			else:
				d = now - gohome
				print 'Time left 00:00. Overwork {}'.format(secondsToStrtime(d.seconds))

		shouldbe_minutes = (tillYesterdayDays(inouts) + 1) * needMinsPerDay()
		total = prev_seconds + today_seconds_work
		printTotal(total, shouldbe_minutes * 60)
	else:
		shouldbe_minutes = tillYesterdayDays(inouts) * needMinsPerDay()
		today_seconds_work = 0
		if str(today) in EXCLUDE_DAYS and today in inouts:
			today_inouts = inouts[today]
			if len(today_inouts) % 2 and today_inouts[-1][1] == IN:
				today_inouts.append((now, OUT)) #Типа вышли только что
			today_seconds_work, _  = daySeconds(today_inouts)
		total = prev_seconds + today_seconds_work
		printTotal(total, shouldbe_minutes * 60)

if __name__ == '__main__':
	main()
