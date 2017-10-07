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


print('jedziemy z koksem')
acc_doc = openpyxl.load_workbook('accounts.xlsx')
acc_sheet = acc_doc.active
cells = acc_sheet['A1': 'H7']

while True:
    print('**************     start cycle    **************')
    startTime = datetime.now()
    for a, b, c, d, e, f, g, h in cells:
        try:
            start_time = datetime.now()
            login = a.value
            password = b.value
            server = c.value
            uni = d.value

            print('login : ' + login)
            print('server : ' + server)
            print('uni : ' + uni)

            if e.value == 'eco':
                bot = Bot(login, password, server, uni)
                bot.start_eco()
            if e.value == 'def':
                bot = Bot(login, password, server, uni)
                bot.start_def()
        except Exception as e:
            print('-----======------- Error happend in bot -----======-------')
            print(e)
        finally:
            time_elapsed = datetime.now() - start_time
            print('Time elapsed for {} is {}[hh:mm:ss.ms]'.format(login, time_elapsed))

    timeElapsed = datetime.now() - startTime
    wait_time = random.uniform(1300, 1600)
    print('{}: **************     ENDED CHECKING ALL ACCOUNTS: elapsed cycle time: {}[hh:mm:ss.ms], '
          'defend time: {:6.2f}[m]'.format(datetime.now(), timeElapsed, wait_time/60))

    print('**************     STARTING DEFENDING      ***************')
    account = ""
    for a, b, c, d, e, f, g, h in cells:
        try:
            start_time = datetime.now()
            login = a.value
            password = b.value
            server = c.value
            uni = d.value

            print('login : ' + login)
            print('server : ' + server)
            print('uni : ' + uni)

            account = login
            if e.value == 'def':
                # bot = Bot(login, password, server, uni)
                ogame = OGame(uni, login, password, server)
                timeout = time.time() + wait_time  # (60*5) 5 minutes from now
                while True:
                    if time.time() > timeout:
                        break
                    Bot.check_anti_ballistic_missiles_on_main_planet(ogame)
        except Exception as e:
            print('-----======------- Error happend in bot -----======-------')
            print(e)
        finally:
            time_elapsed = datetime.now() - start_time
            print('Time elapsed for defending{} is {}[hh:mm:ss.ms]'.format(login, str(time_elapsed)))
        print('**************     ENDED DEFENDING ACCOUNT: {} elapsed cycle time: {}[hh:mm:ss.ms]'
              .format(account, time_elapsed))
    # sleep(wait_time)




