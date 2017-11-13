import sys
import os
sys.stdout = sys.stderr
p = '/data/home/qqin/lisa_web'

activate_this = os.path.join('/data/home/qqin/rabit/rabitqqin/', 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

sys.path.append(p)

from lisa_web import app as application

