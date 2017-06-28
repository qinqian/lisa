#!/usr/bin/env python

import os
import configparser
import sys

if len(sys.argv) > 2:
    sys.stderr.write('too many parameters...')
    sys.exit(1)

c = configparser.ConfigParser()
c.read(sys.argv[1])

for s in c.sections():
    for k in c[s].keys():
        if k == 'bwa_index':
            continue
        if os.path.exists(c.get(s, k)):
            print(c.get(s, k))
        else:
            print(c.get(s, k))
            raise Exception
