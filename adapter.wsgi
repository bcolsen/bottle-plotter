import bottle_plot  # This loads your application # noqa: F401
import sys
import os
import bottle

sys.path = ['/var/www/plot/'] + sys.path
os.chdir(os.path.dirname(__file__))


application = bottle.default_app()
