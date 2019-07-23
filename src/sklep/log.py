import logging
import sys

loger = logging.getLogger('sklep')
#loger.setLevel('DEBUG')


# Logging filter used in sklep base settings to disable admin mails while running UTs
class UtNotRunning(logging.Filter):
    def filter(self, record):
        return False if 'test' in sys.argv else True
