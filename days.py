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
    '2018-04-28',
    '2018-06-09',
    '2018-12-29',
]

# Будни, которые официально стали нерабочими
OFF_DAYS = [
    Days('2018-01-01', '2018-01-08'),
    '2018-02-23',
    '2018-02-24',
    '2018-03-08',
    '2018-03-09',
    '2018-04-30',
    '2018-05-01',
    '2018-05-02',
    '2018-05-09',
    '2018-06-11',
    '2018-06-12',
    '2018-11-05',
    '2018-12-31',
    Days('2019-01-01', '2019-01-08'),
    '2019-03-08',
    Days('2019-05-01', '2019-05-03'),
    Days('2019-05-09', '2019-05-10'),
    '2019-06-12',
    '2019-11-04',
]
