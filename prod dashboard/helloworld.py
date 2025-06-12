import direct_redis
import pandas as pd 
import datetime
from xxx.live_ems import EventInterface

r = direct_redis.DirectRedis()
# active_clients=r.hgetall('clients_live_today')
from xxx.ems import *
import math,glob,os
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from matplotlib import pyplot as plt
import plotly.express as px
import mibian as mb
from xxx.comms import *
from xxx.live_ems import EventInterface

tg = Comms()
import threading

def send_telegram_alert(message,channel='rms'):
    tg.ping(message,channel)

send_telegram_alert("hello")