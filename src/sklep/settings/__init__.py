import socket

PROD_HOSTS = ['vps507708']

from .base import *

host = socket.gethostname()

if host in PROD_HOSTS:
    from .production import *

else:
    try:
        from .local import *
    except:
        raise EnvironmentError("Error in settings/local.py")

print('*' + CURRENT_SETTINGS + '*')
