import os
from django_addon import startup


application = startup.wsgi(path=os.path.dirname(__file__))
