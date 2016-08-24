#!env python
import re
import datetime
import os
import urllib2
import config

def write(filename, inouts):
	open(filename, 'w').write('\n'.join(inouts) + '\n')

now = datetime.datetime.now()
date = datetime.datetime.strftime(now, '%Y-%m')

inout_pattern = re.compile('(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d) (in|out)')
inouts = []

log = urllib2.urlopen('http://wiki.ispsystem.net/door.py?month={}&cardnum={}&log'.format(date, config.CARDNUM))
text = log.read()
inout_match = inout_pattern.search(text)
while inout_match is not None:
	inouts.append(inout_match.group(0))
	inout_match = inout_pattern.search(text, inout_match.end())

jobstatfile = os.path.expanduser('%s/%02d' % (config.JOBSTAT_DIRECTORY, now.month))
exist_inouts = [line.strip() for line in open(jobstatfile)]
if len(exist_inouts) > 0 and inouts[0] == exist_inouts[0]:
	should_add = False
	for inout in inouts:
		if should_add:
			exist_inouts.append(inout)
			continue
		if inout == exist_inouts[-1]:
			should_add = True
	write(jobstatfile, exist_inouts)
	if not should_add:
		write(jobstatfile, inouts)
else:
	write(jobstatfile, inouts)
