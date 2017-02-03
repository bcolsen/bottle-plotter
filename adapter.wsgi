import sys, os, bottle

sys.path = ['/var/www/plot/'] + sys.path
os.chdir(os.path.dirname(__file__))

import bottle_plot # This loads your application

application = bottle.default_app()
