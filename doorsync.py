#!/usr/bin/env python3
import datetime
import os
import urllib.request
import config
import logging
import json


def write(filename, inouts):
    logging.debug('write %s', inouts)
    open(filename, 'w').write('\n'.join(inouts) + '\n')


def get_door_inouts(date):
    inouts = []

    url = 'http://itools.ispsystem.net/door'
    print(url)
    log = urllib.request.urlopen(
        '{}/monthly/{}/user/{}?json'.format(url, date, config.CARDNUM))
    text = log.read().decode('utf-8')
    doorjson = json.loads(text)
    for _, obj in doorjson.items():
        if 'times' not in obj:
            continue
        for t in obj["times"]:
            inout = None
            if t[1] in (148898,30501,25956):
                inout = 'in'
            elif t[1] in (149051,26108):
                inout = 'out'
            else:
                continue
            inouts.append('{} {}'.format(t[0].replace('T', ' '), inout))

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
    except (ValueError,IndexError):
        write(jobstatfile, inouts)
        return

    write(jobstatfile, exist_inouts + inouts[index + 1:])


if __name__ == '__main__':
    main()
