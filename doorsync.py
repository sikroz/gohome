#!/usr/bin/env python3
import re
import datetime
import os
import urllib.request
import config
import logging


def write(filename, inouts):
    logging.debug('write %s', inouts)
    open(filename, 'w').write('\n'.join(inouts) + '\n')


def get_door_inouts(date):
    inout_pattern = re.compile(r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) (in|out)')
    inouts = []

    log = urllib.request.urlopen(
        'http://wiki.ispsystem.net/door.py?month={}&cardnum={}&log'.format(date, config.CARDNUM))
    text = log.read().decode('utf-8')
    inout_match = inout_pattern.search(text)
    while inout_match is not None:
        inouts.append(inout_match.group(0))
        inout_match = inout_pattern.search(text, inout_match.end())
    logging.debug('door %s', inouts)
    return inouts


def get_saved_inouts(jobstatfile):
    if os.path.exists(jobstatfile):
        return [line.strip() for line in open(jobstatfile)]
    return None


def main():
    now = datetime.datetime.now()
    date = datetime.datetime.strftime(now, '%Y-%m')
    inouts = get_door_inouts(date)

    jobstatdir = os.path.expanduser(config.JOBSTAT_DIRECTORY)
    if not os.path.exists(jobstatdir):
        os.mkdir(jobstatdir)

    jobstatfile = '{}/{:02}'.format(jobstatdir, now.month)
    exist_inouts = get_saved_inouts(jobstatfile)
    logging.debug('exist_inouts %s', exist_inouts)
    if exist_inouts is None:
        write(jobstatfile, inouts)
        return

    # Дополняем новыми, не меняя старые
    try:
        index = inouts.index(exist_inouts[-1])
    except ValueError:
        write(jobstatfile, inouts)
        return

    write(jobstatfile, exist_inouts + inouts[index + 1:])


if __name__ == '__main__':
    main()
