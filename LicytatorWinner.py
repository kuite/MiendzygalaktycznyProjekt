from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random


wait_time = random.uniform(1800, 1600)
print('**************     ENDED CHECKING ALL ACCOUNTS: elapsed cycle time: [hh:mm:ss.ms], '
      'defend time: {:6.2f}[m]'.format(wait_time / 60))
