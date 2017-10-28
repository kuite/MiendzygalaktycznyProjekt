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
import sys


try:
    acc_doc = openpyxl.load_workbook('accounts.xlsx')
    acc_sheet = acc_doc.active
    cells = acc_sheet['A1': 'H100']
    begin_bot_time = datetime.now()
    acc_num = int(sys.argv[1])

    login = cells[acc_num][0].value
    password = cells[acc_num][1].value
    server = cells[acc_num][2].value
    uni = cells[acc_num][3].value
    mode = cells[acc_num][4].value

    if login is None or login == "":
        quit()

    print('**************     start bot for {}   **************'.format(login))
    start_time = datetime.now()
    try:
        print('login : ' + login)
        print('server : ' + server)
        print('uni : ' + uni)
        if mode == 'supplier':
            print('supplier mode on')
            # bot = Bot(login, password, server, uni)
            # bot.start_supplier()
        if mode == 'eco':
            bot = Bot(login, password, server, uni)
            bot.start_eco()
        if mode == 'def':
            bot = Bot(login, password, server, uni)
            bot.start_def()
    except Exception as e:
        print('-----======------- Error happend in bot -----======-------')
        print(e)
    finally:
        time_elapsed = datetime.now() - start_time
        print('Time elapsed for {} is {}[hh:mm:ss.ms]'.format(login, time_elapsed))

except Exception as e:
    print('-----======------- Error happend in StartDef -----======-------')
    print(e)




