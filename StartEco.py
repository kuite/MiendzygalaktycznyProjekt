from Bot import Bot
from ogame import OGame
import openpyxl
import time
from random import randint
from time import sleep
import itertools
import random
import datetime
from datetime import datetime

try:
    print('jedziemy z koksem')
    acc_doc = openpyxl.load_workbook('accounts.xlsx')
    acc_sheet = acc_doc.active
    cells = acc_sheet['A1': 'H20']
    begin_bot_time = datetime.now()


    print('**************     start cycle    **************')
    startTime = datetime.now()
    for a, b, c, d, e, f, g, h in cells:
        if a.value is None or a.value == "":
            continue
        # if e.value != 'eco':
        #     continue
        try:
            start_time = datetime.now()
            login = a.value
            password = b.value
            server = c.value
            uni = d.value

            print('login : ' + login)
            print('server : ' + server)
            print('uni : ' + uni)

            bot = Bot(login, password, server, uni)
            bot.start_supplier()
        except Exception as e:
            print('-----======------- Error happend in bot -----======-------')
            print(e)
        finally:
            time_elapsed = datetime.now() - start_time
            print('Time elapsed for {} is {}[hh:mm:ss.ms]'.format(login, time_elapsed))

    timeElapsed = datetime.now() - startTime
    wait_time = random.uniform(1200, 1400)
    print('{}: **************     ENDED CHECKING ALL ECO ACCOUNTS: elapsed cycle time: {}[hh:mm:ss.ms], '
          'defend time: {:6.2f}[m]'.format(datetime.now(), timeElapsed, wait_time/60))
except Exception as e:
    print('-----======------- Error happend in StartEco -----======-------')
    print(e)



