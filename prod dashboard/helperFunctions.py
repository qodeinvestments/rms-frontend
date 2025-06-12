# Helper functions (keep your existing helper functions here)
import datetime
import pandas as pd
import direct_redis
from datetime import date
import json
from fastapi import WebSocket 
import functools
from typing import Dict, List, Any
from multiprocessing import Pool
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday
from dateutil.relativedelta import relativedelta
from xxx.comms import Comms
import re
from typing import List, Dict, Optional , Union

from live_ems2 import DataInterface
ei = DataInterface()
tg = Comms()

import math,glob,os
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from matplotlib import pyplot as plt
import plotly.express as px
import mibian as mb
import pickle
import threading
from functools import lru_cache

import pickle
from typing import Dict, List, Any , Set , Tuple
import ast





r = direct_redis.DirectRedis()
pipe = r.pipeline()
symbolTOzerodhasymbol = r.get('symbolTOzerodhasymbol')
system_tags=r.hgetall('system_tags')
swan_basket = r.hgetall('live_baskets')
clients = r.hgetall('live_clients')
active_clients=r.hgetall('clients_live_today')
live_weights = r.hgetall('live_weights')
symbolTOexchange = r.get('symbolTOexchange')
pf_values=r.hgetall('user_pf_value')
params=r.hgetall('pos_size_params')
zerodhasymbolTOsymbol=r.get('zerodhasymbolTOsymbol')
exchangeToSymbol=r.get('exchangeTOsymbol')
cashalertinputs=r.hgetall('cash_alert_input')
valid_index=['BANKNIFTY' , 'NIFTY' , 'FINNIFTY' , 'BANKNIFTY' , 'SENSEX']
today=datetime.datetime.today().date()
User_Broker_Map={}
user_pf_map={}
squareOffFlagDict=r.hgetall('sq_off_flag')
squareOffModeDict=r.hgetall('sq_off_mode')


userIdToUserNameMap={}
userNameToUserIdMap={}
for client,value in clients.items():
    userIdToUserNameMap[value['user_id']]=client
    userNameToUserIdMap[client]=value['user_id']


for client, value in clients.items():
    if not active_clients.get(client):
        continue
    User_Broker_Map[client]=value['broker']
    user_id = value['user_id']
    user_pf_map[user_id] = {
        arr['Date']: {
           'pf': arr['portfolio_value'],
           'limits':arr['limits'],
           'client_multiplier':arr['client_multiplier']
        }
        for arr in r.lrange(f'ALL_USER_FUND_SUMMARY.{client}', 0, -1)
        if 'portfolio_value' in arr
    }
    user_pf_map[user_id][today]={
       'pf': pf_values[user_id],
       'limits':params[user_id] if user_id in params else None,
       'client_multiplier':value['client_multiplier'],
    }



uidlist = {uid for val in live_weights.values() for uid, j in val.items() if j == 1}
system_tag_map={}
system_tag_to_strat={}
strat_params=r.hgetall('Strategy_Parameter_Monitoring')
systemweightage=pd.read_csv('/root/algo/xxx/live_support_data/strategy_pos_size_data.csv')


for strat in live_weights.keys():
    system_tag_map[strat]=[]
    uids=live_weights[strat]
    for key,value in uids.items():
        system_tag_map[strat].append(system_tags[key])
        system_tag_to_strat[system_tags[key]]=strat

long_options_system = {
    "BANKNIFTYFINNIFTY": {
        "LONG1":  {"time": "09:15:00", "type": "o", "check": "15:00:00", "percentage": 0.5},
        "LONG2":  {"time": "09:15:00", "type": "c", "check": "15:30:00", "percentage": 0.5},
        "LONG3":  {"time": "09:15:00", "type": "o", "check": "16:00:00", "percentage": 0.5},
        "LONG4":  {"time": "09:15:00", "type": "c", "check": "16:30:00", "percentage": 0.5},
        "LONG5":  {"time": "09:15:00", "type": "o", "check": "17:00:00", "percentage": 0.5},
        "LONG6":  {"time": "09:15:00", "type": "c", "check": "17:30:00", "percentage": 0.5},
        "LONG7":  {"time": "12:00:00", "type": "o", "check": "17:30:00", "percentage": 0.3},
        "LONG8":  {"time": "12:00:00", "type": "c", "check": "18:00:00", "percentage": 0.3},
        "LONG9":  {"time": "12:00:00", "type": "o", "check": "18:30:00", "percentage": 0.3},
        "LONG10": {"time": "12:00:00", "type": "c", "check": "19:00:00", "percentage": 0.3},
        "LONG11": {"time": "12:00:00", "type": "o", "check": "19:30:00", "percentage": 0.3},
        "LONG12": {"time": "12:00:00", "type": "c", "check": "20:00:00", "percentage": 0.3}
    },
    "NIFTYSENSEX": {
        "LONG1":  {"time": "09:15:00", "type": "o", "check": "15:00:00", "percentage": 0.5},
        "LONG2":  {"time": "09:15:00", "type": "c", "check": "15:00:00", "percentage": 0.5},
        "LONG3":  {"time": "09:15:00", "type": "o", "check": "15:30:00", "percentage": 0.5},
        "LONG4":  {"time": "09:15:00", "type": "c", "check": "15:30:00", "percentage": 0.5},
        "LONG5":  {"time": "09:15:00", "type": "o", "check": "16:00:00", "percentage": 0.5},
        "LONG6":  {"time": "09:15:00", "type": "c", "check": "16:00:00", "percentage": 0.5},
        "LONG7":  {"time": "09:15:00", "type": "o", "check": "16:30:00", "percentage": 0.5},
        "LONG8":  {"time": "09:15:00", "type": "c", "check": "16:30:00", "percentage": 0.5},
        "LONG9":  {"time": "09:15:00", "type": "o", "check": "17:00:00", "percentage": 0.5},
        "LONG10": {"time": "09:15:00", "type": "c", "check": "17:00:00", "percentage": 0.5},
        "LONG11": {"time": "09:15:00", "type": "o", "check": "17:30:00", "percentage": 0.5},
        "LONG12": {"time": "09:15:00", "type": "c", "check": "17:30:00", "percentage": 0.5},
        "LONG13": {"time": "12:00:00", "type": "o", "check": "17:30:00", "percentage": 0.3},
        "LONG14": {"time": "12:00:00", "type": "c", "check": "17:30:00", "percentage": 0.3},
        "LONG15": {"time": "12:00:00", "type": "o", "check": "18:00:00", "percentage": 0.3},
        "LONG16": {"time": "12:00:00", "type": "c", "check": "18:00:00", "percentage": 0.3},
        "LONG17": {"time": "12:00:00", "type": "o", "check": "18:30:00", "percentage": 0.3},
        "LONG18": {"time": "12:00:00", "type": "c", "check": "18:30:00", "percentage": 0.3},
        "LONG19": {"time": "12:00:00", "type": "o", "check": "19:00:00", "percentage": 0.3},
        "LONG20": {"time": "12:00:00", "type": "c", "check": "19:00:00", "percentage": 0.3},
        "LONG21": {"time": "12:00:00", "type": "o", "check": "19:30:00", "percentage": 0.3},
        "LONG22": {"time": "12:00:00", "type": "c", "check": "19:30:00", "percentage": 0.3},
        "LONG23": {"time": "12:00:00", "type": "o", "check": "20:00:00", "percentage": 0.3},
        "LONG24": {"time": "12:00:00", "type": "c", "check": "20:00:00", "percentage": 0.3}
    }
}


Nifty_Spot_Data=ei.get_all_ticks_by_symbol('NIFTYSPOT')
SENSEX_Spot_Data=ei.get_all_ticks_by_symbol('SENSEXSPOT')

pd.set_option('future.no_silent_downcasting', True)

def get_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_time():
    return datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')

def get_index_ltp():
    ltp_dict = {}
    # for i in ['NIFTYSPOT', 'BANKNIFTYSPOT', 'FINNIFTYSPOT', 'MIDCPNIFTYSPOT', 'SENSEXSPOT']:
    for i in ['NIFTYSPOT', 'BANKNIFTYSPOT', 'FINNIFTYSPOT', 'SENSEXSPOT']:
        ltp = r.get(f'ltp.{i}')
        if ltp is not None:
            ltp_dict[i] = ltp
    return ltp_dict

def get_rms_prev_day(client):
    map=[]
    trades=r.hget('live_user_rms_prev_day',client)
    for trade in trades:
            sym=  trade.get('symbol', trade.get('tradingsymbol'))
            map.append({
                'Symbol': zerodhasymbolTOsymbol[sym] if sym in zerodhasymbolTOsymbol else sym  ,  
                'AveragePrice': trade.get('average_price', trade.get('OrderAverageTradedPrice')),
                'Quantity': -trade.get('filled_quantity', trade.get('CumulativeQuantity'))
                            if trade.get('transaction_type', trade.get('OrderSide')) == 'SELL'
                            else trade.get('filled_quantity', trade.get('CumulativeQuantity')),
                'Type': trade.get('transaction_type', trade.get('OrderSide'))
            })
    
    return map



class NSECalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('Republic Day', month=1, day=26),
        Holiday('Mahashivratri', month=2, day=26),
        Holiday('Holi', month=3, day=14),
        Holiday('eid', month=3, day=31),
        Holiday('Shri Mahavir Jayanti', month=4, day=10),
        Holiday('Dr. Baba Saheb Ambedkar Jayanti', month=4, day=14),
        Holiday('Good Friday', month=4, day=18),
        Holiday('Maharashtra Day', month=5, day=1),
        Holiday('Independence Day', month=8, day=15),
        Holiday('Shri Ganesh Chaturthi', month=8, day=27),
        Holiday('Mahatma Gandhi Jayanti', month=10, day=2),
        Holiday('Diwali Laxmi Pujan', month=10, day=21),
        Holiday('Balipratipada', month=10, day=22),
        Holiday('Prakash Gurpurb Sri Guru Nanak Dev', month=11, day=5),
        Holiday('Christmas', month=12, day=25)
        	
        # Add more holidays here
    ]

class FlexibleCustomBusinessDay(CustomBusinessDay):
    def __init__(self, *args, **kwargs):
        self.working_saturdays = kwargs.pop('working_saturdays', [])
        super().__init__(*args, **kwargs)

    def is_on_offset(self, dt):
        if dt.date() in self.working_saturdays:
            return True
        return super().is_on_offset(dt)

def get_holidays(start_date, end_date):
    calendar = NSECalendar()
    return calendar.holidays(start=start_date, end=end_date).date.tolist()

def get_nse_working_days(start_date, end_date, working_saturdays=[]):
    business_days = FlexibleCustomBusinessDay(calendar=NSECalendar(), weekmask='Mon Tue Wed Thu Fri', working_saturdays=working_saturdays)
    date_range = pd.date_range(start=start_date, end=end_date, freq=business_days)
    return date_range.tolist()

def is_working_day(date, working_saturdays=[]):
    if isinstance(date, datetime.date):
        date = date
    
    # Get holidays for the specific date
    holidays = get_holidays(date, date)
    
    # Check if it's a holiday
    if date in holidays:
        return False
    
    # Check if it's a weekend (not a working Saturday)
    if date.weekday() >= 5 and date not in working_saturdays:
        return False
    
    return True

def get_previous_working_day(date, working_saturdays=[]):
    if isinstance(date, datetime.date):
        date = date
    
    current_date = date - datetime.timedelta(days=1)
    while not is_working_day(current_date, working_saturdays):
        current_date -= datetime.timedelta(days=1)
    return current_date

def get_history_index_ltp_Date():
    today = datetime.datetime.now().date()
    working_saturdays = [
        # datetime.date(2024, 1, 20),  # Example working Saturday
        # datetime.date(2024, 3, 16),  # Another example working Saturday
        # datetime.date(2024, 9, 28)
    ]
    prev_working_day = get_previous_working_day(today, working_saturdays)
    return prev_working_day



def get_history_index_ltp():
    ltp_dict = {}
    today = datetime.datetime.now()
    yesterday = get_history_index_ltp_Date()
    yesterday=yesterday.strftime('%Y-%m-%d')
    for i in ['NIFTYSPOT', 'BANKNIFTYSPOT', 'FINNIFTYSPOT', 'MIDCPNIFTYSPOT', 'SENSEXSPOT']:
        ltp = r.hget(f'l.tick_{yesterday} 15:29:00',i)
        if ltp is not None:
            ltp_dict[i] = ltp['c']
    return ltp_dict


def get_ideal_client_margin(margin):
    
    return round(float(margin)) if margin is not None else 0



def get_client_client_balance(client,name,data):
     if client in data:
      if name in data[client]:
          return float(data[client][name])
     return 0
  


def get_ideal_client_var(client):
    return r.hget('curr_client_var', client)


def get_client_rms_df(client):
    return r.hget('live_client_rms_df', client)


def get_net_qty(pos):
    if pos is not None:
        return sum([x for x in pos.values()])
    return 0

def get_open_qty(pos):
    if pos is not None:
        return sum([abs(x) for x in pos.values()])
    return 0

def get_idealMTM(client):
    val = r.hgetall('curr_client_ideal_mtm')
    if client in val:
        return float(val[client])
    return 0


def get_zerodha_order_book(client):
    cols=[ 'OrderAverageTradedPrice']
    val=r.hget('live_user_whole_ob', client)
    if val==None:
        return None
    for obj in val:
        for key, value in obj.items():
            if key in cols:
                obj[key]=float(obj[key]) if len(obj[key])>0 else None
            if key=='TradingSymbol':
                obj[key]=exchangeToSymbol[obj['ExchangeInstrumentID']] if obj['ExchangeInstrumentID'] in exchangeToSymbol else value
            if key=='tradingsymbol':
                obj[key]=zerodhasymbolTOsymbol[value] if value in zerodhasymbolTOsymbol else value
            if isinstance(value, datetime.datetime):
                obj[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # Convert to string format
        
    val = sorted(val, key=lambda x: x['OrderGeneratedDateTime' if 'OrderGeneratedDateTime' in val[0] else 'order_timestamp'], reverse=True)
 
    return val

def get_zerodha_position_book(client):
    cols=['BuyAveragePrice', 'SellAveragePrice']
    val=r.hget('client_positions',client)
    if val==None:
        return None
    for obj in val:
        for key,value in obj.items():
            if key in cols:
                obj[key]=float(obj[key])
            if key=='TradingSymbol':
                num=int(obj['ExchangeInstrumentId'])
                obj[key]=exchangeToSymbol[num] if num in exchangeToSymbol else None
            if key=='tradingsymbol':
                obj[key]=zerodhasymbolTOsymbol[value] if value in zerodhasymbolTOsymbol else value
    
    return val

def get_client_holding(client):
    
    val=r.hget(f'client_holdings', client)
    if val==None:
        return None
    df=pd.DataFrame(val)
    df['EntryContractValue']=df['average_price']*df['quantity']
    df['ExitContractValue']=df['last_price']*df['quantity']
    return df.to_dict('records')

 

def get_actual_client_MTM(client):
    arr=r.hgetall(f'live_client_mtm.{client}')
    if not arr:
        return 0
    max_key = sorted(arr.keys()) 
    return arr[max_key[-1]]

def getRejectedOrders(rejected_orders):
    
    return int(rejected_orders) if rejected_orders is not None else 0

def getPendingOrders(pending_orders):
    return int(pending_orders) if pending_orders is not None else 0

def change_chart_data_to_epoch(chart_data):
    df = pd.DataFrame(list(chart_data.items()), columns=['datetime', 'value'])
    df['datetime'] = pd.to_datetime(df['datetime'], format="%Y-%m-%d %H:%M:%S", utc=True)
    df['value'] = df['value'].astype(float)
    df['time'] = df['datetime'].astype(int) // 10**9
    arr = df[['time', 'value']].to_dict(orient='records')
    return arr


def change_chart_data(client):
    ltp_dict =r.hgetall(f'live_client_mtm.{client}')
    ltp_dict = pd.Series(ltp_dict)
    ltp_dict = ltp_dict[ltp_dict != 0]
    ltp_dict = ltp_dict.sort_index()
    arr=change_chart_data_to_epoch(ltp_dict)
    return arr


async def get_basketData_swan(client):
    ltp_dict = r.hgetall(f'live_client_ideal_mtm.{client}')

    return  {
        "time":get_time(),
        "live":get_live_client_basket_data(client),
        "curr":get_curr_client_basket_data(client),
        'ideal_MTMTable': get_idealMTMTable(ltp_dict),
        "MTMTable": change_chart_data(client),
        'signalPosition': get_signal_position(client),
        
    }




def get_curr_client_basket_data(client):
    userid=clients[client]['user_id']
    client_multiplier=clients[client]['client_multiplier']
    val=r.hgetall('curr_mtm_swan')
    arr=[]
    for basket in val.keys() :
        if basket in client_multiplier and userid in val[basket]  :
            MTM_revised_value=val[basket][userid]*client_multiplier[basket]
            val_obj={"basket":basket,"MTM":format(MTM_revised_value,'.2f')}
            arr.append(val_obj)

    val=r.hgetall('curr_mtm')
    for basket,value in val.items() :
        if basket in client_multiplier :
            MTM_revised_value=value*client_multiplier[basket]
            val_obj={"basket":basket,"MTM": format(MTM_revised_value,'.2f')}
            arr.append(val_obj)

    return arr


# def get_live_client_basket_data(client):
#     userid = clients[client]['user_id']
#     client_multiplier = clients[client]['client_multiplier']
#     map = {}
#     time_delta = datetime.timedelta(hours=5, minutes=30)
#     def process_basket(basket_key, mtm_key):
#         if basket_key in client_multiplier:
#             if basket_key not in map.keys() :
#                 map[basket_key]=[]
#             data = r.hgetall(f'{mtm_key}.{basket_key}')
#             sorted_data = sorted(data.items(), key=lambda item: datetime.datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S')) 
#             for key, value in sorted_data:
#                 updated_time = datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S') + time_delta
#                 epoch_time = int(updated_time.timestamp())
#                 if mtm_key == 'live_mtm_swan' :
#                     if userid in value:
#                         mtm_value = float(value[userid]) * client_multiplier[basket_key]
#                         map[basket_key].append({"time": epoch_time, "value": mtm_value})
#                 else :
#                     mtm_value = float(value) * client_multiplier[basket_key]
#                     map[basket_key].append({"time": epoch_time, "value": mtm_value})
    
#     for basket in live_weights:
#         process_basket(basket, 'live_mtm_swan') 
#         process_basket(basket, 'live_mtm') 

#     return map


def get_live_client_basket_data(client):
    userid = clients[client]['user_id']
    client_multiplier = clients[client]['client_multiplier']
    map_data = {}
    time_delta = datetime.timedelta(hours=5, minutes=30)

    def process_basket(basket_key, mtm_key):
        if basket_key in client_multiplier:
            if basket_key not in map_data:
                map_data[basket_key] = []
            data = r.hgetall(f'{mtm_key}.{basket_key}')
            # Sort *this chunk* by timestamp
            sorted_data = sorted(
                data.items(),
                key=lambda item: datetime.datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S')
            )
            for key, value in sorted_data:
                updated_time = datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S') + time_delta
                epoch_time = int(updated_time.timestamp())

                if mtm_key == 'live_mtm_swan':
                    # 'value' is a string containing user-data (check if user exists)
                    if userid in value:
                        mtm_value = float(value[userid]) * client_multiplier[basket_key]
                        map_data[basket_key].append({"time": epoch_time, "value": mtm_value})
                else:
                    # 'value' is just a single float-like string
                    mtm_value = float(value) * client_multiplier[basket_key]
                    map_data[basket_key].append({"time": epoch_time, "value": mtm_value})

    # Process both 'live_mtm_swan' and 'live_mtm' for each basket
    for basket in live_weights:
        process_basket(basket, 'live_mtm_swan')
        process_basket(basket, 'live_mtm')

    # 1) Final sort for each basket's array, 2) remove duplicates by 'time'
    for basket_key, data_list in map_data.items():
        # Sort by 'time'
        data_list.sort(key=lambda x: x["time"])
        
        # Remove duplicates by time (keep the first encountered)
        unique_data = []
        seen_times = set()
        for row in data_list:
            if row["time"] not in seen_times:
                seen_times.add(row["time"])
                unique_data.append(row)
        map_data[basket_key] = unique_data

    return map_data





def read_pulse_updates():
    arr= r.get('rms_heartbeat')
    filtered_arr = {k: v for k, v in arr.items() 
                    if not k.startswith('pulse_trader') or (k.startswith('pulse_trader') and k.split(':')[1] in active_clients and active_clients[k.split(':')[1]])}

    return (filtered_arr)

def read_position_mismatch():
    # Fetch data from Redis (simulated here as fetched data)
    data = r.hgetall('net_positions_verification')
    
    # Iterate through the data and convert any DataFrames to dictionaries
    for key, value in data.items():
        if isinstance(value, pd.DataFrame):
            # Convert the DataFrame to a dictionary of records
            data[key] = value.to_dict(orient='records')
    
    return data



def get_client_live_trade_book(client: str) -> List[Dict[str, Any]]:
    tb = r.hget('live_user_tb', client)
    if not tb:
        return []

    df = pd.DataFrame(tb)
    if df.empty:
        return []

    broker = clients[client]['broker']
    
    if broker == 'xts':
        columns = [
            'OrderGeneratedDateTime', 'ExchangeTransactTime',
            'OrderAverageTradedPrice', 'OrderSide', 'OrderQuantity'
        ]
    elif broker == 'zerodha':
        columns = [
            "exchange", "tradingsymbol", "product", "average_price", "quantity",
            "transaction_type", "fill_timestamp", "order_timestamp", "exchange_timestamp"
        ]
    else:
        return []  # Unsupported broker type

    df = df[columns]

    if df.empty:
        return []

    # Convert datetime columns to string
    date_columns = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns
    df[date_columns] = df[date_columns].astype(str)

    return df.to_dict('records')


    
def get_client_combined_df(client: str) -> List[Dict[str, Any]]:
    tb = r.hget(f'combined_ob_sg', client)
    if tb is None:
        return []

    df = pd.DataFrame(tb)
    if df.empty:
        return []

    df = df.fillna('').infer_objects(copy=False)

    broker = clients[client]['broker']
    
    if broker == 'xts':
        columns = [
            "order_fill_lag","uid", 'place_order_lag', "timestamp", "action", 
            "qty", "price", "value", "system_timestamp",
            "note", "basket", "effective_qty", "AppOrderID",  
            "ExchangeSegment", "OrderType", "ProductType", "OrderQuantity",
            "OrderStatus", "OrderAverageTradedPrice",
            "OrderGeneratedDateTime", "ExchangeTransactTime", "TradingSymbol",
            "OrderUniqueIdentifier","system_tag","signal_lag"
        ]
    elif broker == 'zerodha':
        columns = [
            "order_fill_lag","trade_id", "uid", "timestamp", "action", "action_int", "qty",
            "qty_dir", "symbol", "price_x", "value", "buy_value",
            "sell_value", "system_timestamp", "note", 
            "basket", "qty_multiplier", "effective_qty", "status", "order_timestamp",
            "exchange_update_timestamp", "exchange_timestamp", "variety",
            "modified", "exchange", "tradingsymbol", 
            "order_type", "transaction_type", "validity", "validity_ttl", "product",
            "quantity_y", "disclosed_quantity", "price_y", "trigger_price",
            "average_price", "filled_quantity", "pending_quantity",
            "cancelled_quantity", "market_protection",  "OrderQuantityDir", "effective_cal_sum", 
            "place_order_lag", "system_tag","signal_lag"
        ]
    else:
        return []  # Unsupported broker type

    df = df[df.columns.intersection(columns)]

    # Convert datetime columns to string
    date_columns = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns
    df[date_columns] = df[date_columns].astype(str)

    return df.to_dict('records')



def get_client_combined_orders(client: str) -> List[Dict[str, Any]]:
    tb = r.hget(f'combined_ob_sg_remaining_orders', client)
    if tb is None:
        return []

    df = pd.DataFrame(tb)
    if df.empty:
        return []

    df = df.fillna('').infer_objects(copy=False)

    broker = clients[client]['broker']
    
    if broker == 'xts':
        columns = [
            'LoginID', 'ClientID', 'AppOrderID', 'OrderReferenceID', 'GeneratedBy',
            'ExchangeOrderID', 'OrderCategoryType', 'ExchangeSegment', 'OrderSide', 'OrderType', 'ProductType',
            'TimeInForce', 'OrderPrice', 'OrderQuantity', 'OrderStopPrice',
            'OrderStatus', 'OrderAverageTradedPrice', 'LeavesQuantity',
            'CumulativeQuantity', 'OrderDisclosedQuantity',
            'OrderGeneratedDateTime', 'ExchangeTransactTime', 'TradingSymbol',
            'LastUpdateDateTime', 'OrderExpiryDate', 'CancelRejectReason',
            'OrderUniqueIdentifier', 'OrderLegStatus', 'BoLegDetails', 'IsSpread',
            'BoEntryOrderId', 'ApiOrderSource', 'MessageCode', 'MessageVersion',
            'TokenID', 'ApplicationType', 'SequenceNumber', 'trade_ids',
            'OrderQuantityDir'
        ]
    elif broker == 'zerodha':
        columns = [
            "status", "status_message", "status_message_raw",
        	"order_timestamp", "exchange_update_timestamp", "exchange_timestamp",
            "variety", "modified", "exchange", "tradingsymbol",
            "order_type", "transaction_type", "validity", "validity_ttl", "product",
            "quantity", "disclosed_quantity", "price", "trigger_price",
            "average_price", "filled_quantity", "pending_quantity",
            "cancelled_quantity", "market_protection", "tag", "tags", "OrderQuantityDir"
        ]
    else:
        return []  # Unsupported broker type

    df = df[df.columns.intersection(columns)]

    # Convert datetime columns to string
    date_columns = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns
    df[date_columns] = df[date_columns].astype(str)

    return df.to_dict('records')




def get_client_combined_trades(client: str) -> List[Dict[str, Any]]:
    tb = r.hget(f'combined_ob_sg_remaining_trades', client)
    if tb is None:
        return []

    df = pd.DataFrame(tb)
    if df.empty:
        return []

    df = df.fillna('').infer_objects(copy=False)

    broker = clients[client]['broker']
    
    if broker == 'xts':
        columns = [
           'trade_id', 'uid', 'timestamp', 'action', 'action_int', 'qty',
       'qty_dir', 'symbol', 'price', 'price_provided', 'value', 'buy_value',
       'sell_value', 'system_timestamp', 'note', 'quantity',
       'basket', 'qty_multiplier', 'effective_qty'
        ]
    elif broker == 'zerodha':
        columns = [
            "trade_id", "uid", "timestamp", "action", "action_int", "symbol",
        		"price", "price_provided", "buy_value", "sell_value",
        		"system_timestamp", "note", "quantity", "qty", "qty_dir", "value",
        		"signal_number", "basket", "qty_multiplier", "effective_qty"
        ]
    else:
        return []  # Unsupported broker type

    df = df[df.columns.intersection(columns)]

    # Convert datetime columns to string
    date_columns = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns
    df[date_columns] = df[date_columns].astype(str)

    return df.to_dict('records')

def get_open_and_complete_order_count(client):
    # Split by space and get the last word
    map={
        'xts': ['Filled', 'Rejected', 'Cancelled'],
        'zerodha': ['COMPLETE', 'REJECTED', 'CANCELLED']
    }
    tb = r.hget('live_user_ob', client)
    if tb==None:
        return 0,0
    last_word = clients[client]['broker']
    column='status'
    if last_word=='xts':
        column='OrderStatus'
    filled_count = sum(1 for order in tb if order[column] == map[last_word][0])
    non_excluded_count = sum(1 for order in tb if order[column] not in map[last_word])
    return filled_count,non_excluded_count


def get_client_live_order_book(client: str) -> List[Dict[str, Any]]:
    tb = r.hget('live_user_ob', client)
    if not tb:
        return []

    df = pd.DataFrame(tb)
    if df.empty:
        return []

    broker = clients[client]['broker']
    columns = {
        'xts': [
            'OrderGeneratedDateTime', 'ExchangeTransactTime', 'OrderType',
            'TradingSymbol', 'OrderAverageTradedPrice', 'OrderSide',
            'LeavesQuantity', 'OrderQuantity', 'OrderStatus',
            'CancelRejectReason', 'CumulativeQuantity','AppOrderID'
        ],
        'default': [
            "status","order_id", "status_message", "order_timestamp", "exchange_update_timestamp",
            "exchange_timestamp", "variety", "modified", "exchange", "tradingsymbol",
            "order_type", "transaction_type", "validity", "validity_ttl", "product",
            "quantity", "disclosed_quantity", "price", "trigger_price", "average_price",
            "filled_quantity", "pending_quantity", "cancelled_quantity",
            "market_protection"
        ]
    }

    df = df[columns.get(broker, columns['default'])]

    # Convert datetime columns to string
    date_columns = df.select_dtypes(include=['datetime64[ns]', 'datetime64']).columns
    df[date_columns] = df[date_columns].astype(str)

    return df.to_dict('records')

def get_idealMTMTable(ltp_dict):
   
    ltp_dict = pd.Series(ltp_dict)
    ltp_dict = ltp_dict[ltp_dict != 0]
    ltp_dict = ltp_dict.sort_index()
    arr=change_chart_data_to_epoch(ltp_dict)
    return arr




async def send_initial_data(websocket:WebSocket):
    obj = {basket: list(val.keys()) for basket, val in live_weights.items()}
    initial_data = {
        # "live_weights": obj,
        "time": get_time(),
        # Add any other initial data you want to send
    }
    await websocket.send_text(json.dumps(initial_data))


def check_user_errorLogs(val):
    filtered_keys = {}
    for key, value in val.items():
        if key.startswith("pulse_trader_xts") or key.startswith("pulse_trader_zerodha"):
            filtered_keys[key] = value
        
    user_errors={}
    for key in filtered_keys:
        if(not filtered_keys[key]):
            user_errors[key.split(":")[1]]={
                "time":get_time(),
                "message":f"{key.split(':')[1]} is not working"
            }
    return user_errors


def check_rs_errorLogs(val):
    if not val:
        return None
    if not val['pulse_run_strats']:
        return {
            "time":get_time(),
            "message" :"Run Strats Stopped",
            "checked":False
        }
    return None


# def get_client_fund_summary(client):
#     temp_tb = r.lrange(f'ALL_USER_FUND_SUMMARY.{client}', 0, -1)
    
#     for record in temp_tb:
#         if 'Date' in record and isinstance(record['Date'], date):
#             record['Date'] = record['Date'].isoformat()
#         # Convert NumPy integers to Python ints
#         for key, value in record.items():
#             if isinstance(value, np.integer):
#                 record[key] = int(value)
#             elif isinstance(value, np.floating):
#                 record[key] = float(value)
    
#     return temp_tb



# def get_client_fund_summary(
#     client,
#     fields=('Date', 'Actual MTM', 'Ideal MTM', 'Peak Margin', 'portfolio_value'),
#     percentage: float = 1.0
# ):
#     raw = r.lrange(f'ALL_USER_FUND_SUMMARY.{client}', 0, -1)
#     def _cast_and_scale(v):
#         if isinstance(v, date):
#             return v.isoformat()
#         if isinstance(v, np.generic):
#             v = v.item()
#         if isinstance(v, (int, float)) and percentage:
#             return v * percentage
#         return v

#     return [
#         { field: _cast_and_scale(rec.get(field)) for field in fields }
#         for rec in raw
#     ]

def convert_str_date(str_date):
    return datetime.datetime.strptime(str_date['startDate'], '%Y-%m-%d').date()

def get_client_fund_summary(
    client,
    fields=('Date', 'Actual MTM', 'Ideal MTM', 'Peak Margin', 'portfolio_value','holdingsdaypl'),
    fund_dates=[]
):
    raw = r.lrange(f'ALL_USER_FUND_SUMMARY.{client}', 0, -1)

    user_id = clients[client]['user_id']
    file_path = f'/root/algo/testing/combined_user_tradebooks/{user_id}_combined.csv'
    
    if os.path.exists(file_path):
        settlement_price_df = pd.read_csv(file_path)
    else:
        settlement_price_df = pd.DataFrame()  # initialize empty DataFrame

    if not fund_dates:
        return [{
            **{
                field: (
                    record[field].isoformat()
                    if isinstance(record[field], (datetime.date, datetime.datetime))
                    else float(record[field]) if isinstance(record[field], (np.integer, np.floating))
                    else int(record[field]) if isinstance(record[field], np.integer)
                    else record[field]
                )
                for field in fields
                if field in record
            },
            'Settlement Price': float(settlement_price_df[
                settlement_price_df['File Date'] == (
                    record['Date'].strftime('%Y-%m-%d') if isinstance(record['Date'], (datetime.date, datetime.datetime)) else record['Date']
                )
            ]['PNL Amount Settlement'].sum())
        } for record in raw]
    
    arr=[]
    i =len(raw)-1
    j =0
    while(i>=0) :
         if raw[i]['Date']>=convert_str_date(fund_dates[j]):
                break
         i-=1
    while(i>=0 and j<len(fund_dates)):
        while(j<len(fund_dates)):
            end=convert_str_date(fund_dates[j+1]) - datetime.timedelta(days=1) if(j+1<len(fund_dates)) else date.today()
            if raw[i]['Date']<=end:
                break
            j=j+1
        if(j==len(fund_dates)):
            start=date.today()
            end=date.today()
        obj={}
        for field  in fields:
            if field !='Date':
                per=100
                if j<len(fund_dates):
                    per=fund_dates[j]['percentage']
                obj[field]=raw[i][field]*per*0.01
            else:
                obj[field]=raw[i][field]
        arr.append(obj)
        i=i-1
        
    return arr

def check_websocket_error(val,old_data):
    if not val:
        return None
    message=""
    if not val['pulse_web_socket4'] and not val['pulse_web_socket3']:
        message="WebSocket 3 and 4 Stopped"
    elif not val['pulse_web_socket4'] :
        message="WebSocket 4 Stopped"
    elif not val['pulse_web_socket3'] :
        message="WebSocket 3 Stopped"
    if len(message)>0:
        error_msg= {
                "time":get_time(),
                "message":message,
                "checked":False,
        }
        old_data.append(error_msg)
    return old_data 





def read_all_keydb_logs(stream_key='keydb_logs'):

    # Read all data from the stream
    result = r.xread({stream_key: '0-0'}, count=None)
    all_messages = []
    if result:
        for stream, messages in result:
            stream_name = stream.decode('utf-8')
            for message_id, message_data in messages:
                message = {
                   k.decode('utf-8'): v.decode('utf-8') for k, v in message_data.items()
                }
                all_messages.append(message)
                
    all_messages.reverse()
    return {
        "time":get_time(),
        "keydblogs":all_messages
    }

def get_keydblogs_data():
    return read_all_keydb_logs()

def change_time_column_to_epoch(df):
    df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d %H:%M:%S", utc=True)
    df['time'] = df['time'].astype(int) // 10**9
    
    # Drop duplicates to ensure unique timestamps
    df = df.drop_duplicates(subset=['time'], keep='first')
    
    return df

def get_combined_df_latency(client):
    tb = r.hget(f'combined_ob_sg', client)
    if len(tb) > 0:
        tb = pd.DataFrame(tb)
        tb = tb.fillna('').infer_objects(copy=False)
        possible_columns = ["timestamp", 'place_order_lag']
        temp_tb = tb[possible_columns]
        temp_tb = temp_tb.sort_values(by='timestamp', ascending=True)
        # Rename columns
        temp_tb = temp_tb.rename(columns={'timestamp': 'time', 'place_order_lag': 'value'})
        # Convert 'time' to epoch
        temp_tb = change_time_column_to_epoch(temp_tb)
        
        return temp_tb.to_dict('records')
    
    
def get_userLagData_data(client):
    val = {
        "time":get_time(),
        # 'rms_latency':get_latency_data(client,"rms_trader_latency_"),
        # 'mtm_margin_latency':get_latency_data(client,"mtm_margin_latency_"),
        # 'sys_tag_lat':get_latency_data(client,"sys_tag_latency_"),
        'xts_trader_lat':get_latency_data(client,"xts_trader_latency_"),
        'pos_agg_latency':get_latency_data("","pos_agg_latency"),
        "combined_df_latency":get_combined_df_latency(client),
    }
    return val

def get_signal_delay():
    all_trades = r.hgetall('live_trades')
    if all_trades is not None:
        trades = sum(all_trades.values(), [])
        tb_ = pd.DataFrame(trades)
        if len(tb_) > 0:
            # Convert columns to datetime
            tb_['system_timestamp'] = pd.to_datetime(tb_['system_timestamp'])
            tb_['timestamp'] = pd.to_datetime(tb_['timestamp'])
            
            # Sort by 'timestamp'
            tb_ = tb_.sort_values('timestamp')
            system_timestamp_ = tb_['system_timestamp']
            timestamp_ = tb_['timestamp']
            
            # Calculate delay
            tb_['delay'] = (system_timestamp_ - timestamp_).dt.total_seconds()
            
            # Subtract 60 from delay values greater than 60
            tb_['delay'] = tb_['delay'].apply(lambda x: x - 60 if x > 60 else x)
            
            # Convert delay to a list (array)
            delay_array = tb_['delay'].tolist()
            return delay_array

    return []


def get_lagsData_data():
    return {
        "time": get_time(),
        "WS7L": r.get('candle_init_lag7') if r.get('candle_init_lag7') is not None else [],
        "WS8L": r.get('candle_init_lag8') if r.get('candle_init_lag8') is not None else [],
        "signal_delay": get_signal_delay() if get_signal_delay() is not None else []
    }


@functools.lru_cache(maxsize=128, typed=False)
def get_latency_data(client, prefix):
    # Combine the prefix and client to form the key
    data = r.lrange(f'{prefix}{client}')

    processed_data = {}
    for entry in data:
        for dt, value in entry.items():
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            processed_data[formatted_date] = value

    def change_chart_data_to_epoch(chart_data):
        df = pd.DataFrame(list(chart_data.items()), columns=['datetime', 'value'])
        df['datetime'] = pd.to_datetime(df['datetime'], format="%Y-%m-%d %H:%M:%S", utc=True)
        df['value'] = df['value'].astype(float)
        df['time'] = df['datetime'].astype(int) // 10**9
        arr = df[['time', 'value']].to_dict(orient='records')
        return arr

    ltp_dict = pd.Series(processed_data)
    ltp_dict = ltp_dict[ltp_dict != 0]
    ltp_dict = ltp_dict.sort_index()
    arr = change_chart_data_to_epoch(ltp_dict)

    return arr



def get_cpu_data():
    return r.lrange('server:cpu_usage_log', 0, -1)

def get_redis_usage_data():
    return r.lrange('server:redis_usage_log', 0, -1)

def get_ram_data():
    return r.lrange('server:ram_usage_log', 0, -1)

def get_serverData_data():
    return{
        "time":get_time(),
        "CPU":get_cpu_data(),
        "RAM":get_ram_data(),
        "Redis":get_redis_usage_data(),
    }

def get_broker(client):
    return clients[client]['broker']

def get_signal_position(client):
    baskets = clients[client]['client_multiplier']
    trades = r.hgetall('live_positions')
    swan_trades = r.hgetall('swan_live_positions')
    
    userid=clients[client]['user_id']
    map={}
    for basket,multiply in baskets.items():
        arr=[]
        positions={}
        if basket in swan_trades:
            if userid in swan_trades[basket]:
                positions=swan_trades[basket][userid]
        elif basket in trades :
            positions=trades[basket]
        for position,value in positions.items():
            arr.append({"Symbol": position, "IdealQuantity": float(multiply) * value})
        map[basket]=arr
    return map


def get_client_slippage(MTM,Ideal_MTM):
    return MTM - Ideal_MTM

def get_client_slippage_per(Slippage,Ideal_MTM,Slippage1):
    return Slippage/(Ideal_MTM - Slippage1) 


def get_client_pnl_overall_percentage(MTM,pf_value):
    pnl=round(MTM, 2)
    return round(((pnl /pf_value) * 100),2)

def get_client_pnl_Utilized_percentage(MTM,Peak_Margin):
    pnl = round(MTM, 2)
    if Peak_Margin == 0:
        return 0.0 
    utilization = (pnl / Peak_Margin) * 100
    return round(utilization, 2)


def get_client_peak_margin(client):
    today_date = get_date()
    peak_margin = r.hget(f'peak_margin.{client}', today_date)
    peak_margin = float(peak_margin) if peak_margin else 0.0
    
    return round(peak_margin, 2)


def round_slippage(slip):
     if slip==None:
         slip=0
     return round(slip,2)

def give_percentage_change(new, old):
    return round((new - old) / old * 100, 2)


def give_longoptions_indicators():
    
    # Get today's date components formatted with two digits for month and day
    today = datetime.datetime.today().date()
    year = today.year
    month = f"{today.month:02d}"
    day = f"{today.day:02d}"

    # Define tick times for sessions
    tick_times = {
        "morning": "09:15:00",
        "afternoon": "12:00:00"
    }
    def get_tick_value(time_label, index, key):
        """Retrieve and convert tick value for a given session time, index and key ('o' or 'c')."""
        tick_data = r.hget(f'l.tick_{year}-{month}-{day} {tick_times[time_label]}', f'{index}SPOT')
        return float(tick_data[key]) if tick_data and key in tick_data else None

    map={}
    indices = ['BANKNIFTY', 'NIFTY', 'FINNIFTY', 'SENSEX']
    for index in indices:
        map[index]={}
        ltp_val = r.get(f'ltp.{index}SPOT')
        ltp = float(ltp_val) if ltp_val is not None else None

        # Retrieve tick values for morning and afternoon
        morning_open = get_tick_value("morning", index, 'o')
        morning_close = get_tick_value("morning", index, 'c')
        afternoon_open = get_tick_value("afternoon", index, 'o')
        afternoon_close = get_tick_value("afternoon", index, 'c')
        
        # Calculate percentage changes if values are present
        map[index]['09:15 O']= give_percentage_change(ltp, morning_open) if ltp and morning_open else 0
        map[index]['09:15 C']= give_percentage_change(ltp, morning_close) if ltp and morning_close else 0
        map[index]['12:00 O']= give_percentage_change(ltp, afternoon_open) if ltp and afternoon_open else 0
        map[index]['12:00 C']= give_percentage_change(ltp, afternoon_close) if ltp and afternoon_close else 0
    
    return map



# def format_to_rupees(number):
#  # Check if the number is negative
#     is_negative = number < 0
#     number = abs(float(number))  # Convert to float and get absolute value

#     # Convert to string and split into whole and decimal parts
#     whole, decimal = f"{number:.2f}".split(".")
    
#     # Format the whole number part
#     reversed_whole = whole[::-1]
#     groups = [reversed_whole[:3]]
#     groups.extend(reversed_whole[3:][i:i+2] for i in range(0, len(reversed_whole[3:]), 2))
#     whole_with_commas = ','.join(group[::-1] for group in reversed(groups))

#     # Prepare the formatted string with ₹ symbol
#     formatted_string = f"{whole_with_commas}.{decimal}"
    
#     # If the number was negative, prepend the minus sign
#     if is_negative:
#         formatted_string = f"-{formatted_string}"
    
#     return formatted_string

def safe_convert_number(value):
    """Convert numpy numbers to native Python types"""
    if value is None:
        return 0
    try:
        return float(value)  # This will handle both int64 and float64
    except (TypeError, ValueError):
        return 0
    
# def send_ping_in_thread(message):
#     def _send_ping():
        
#         try:
#             tg.ping(message)
#         except Exception as e:
#             print(f"Error sending ping: {str(e)}")
    
#     # Start a new thread for the ping
#     thread = threading.Thread(target=_send_ping)
#     thread.daemon = True  # Make sure thread doesn't block program exit
#     thread.start()
#     return


def send_telegram_alert(message, channel='rms'):
    """Synchronous Telegram alert without async/await."""
    def _send():
        tg.ping(message, channel)  # Direct synchronous call
    thread = threading.Thread(target=_send)
    thread.start()

def get_open_trade_to_signalbook_mismatch():
    print("getting in open trade to signal book mismatch")
    # This returns a list of Python dicts
    open_trades = pd.DataFrame(r.lrange('open_trades', 0, -1))  
    all_trades = pd.DataFrame(r.lrange('all_trades', 0, -1))


    open_trades['date'] = pd.to_datetime(open_trades['timestamp']).dt.date
    all_trades['date'] = pd.to_datetime(all_trades['timestamp']).dt.date

    open_trades=open_trades[open_trades['date']<datetime.datetime.now().date()]
    all_trades=all_trades[all_trades['date']<datetime.datetime.now().date()]

    df_open_not_in_all = open_trades[
        ~open_trades["trade_id"].isin(all_trades["trade_id"])
    ]

    df_all_not_in_open = all_trades[
     ~all_trades["trade_id"].isin(open_trades["trade_id"])
    ]


    tell = len(df_open_not_in_all) > 0
    if tell:
        send_telegram_alert("Mismatch in Open Trades To SignalBook")
    else:
        send_telegram_alert("No Mismatch in Open Trades To SignalBook")

    tell = len(df_all_not_in_open) > 0
    if tell:
        send_telegram_alert("Mismatch in SignalBook To Open Trades")
    else:
        send_telegram_alert("No Mismatch in SignalBook To Open Trades")



    return {'open_not_in_all':df_open_not_in_all, "all_not_in_open":df_all_not_in_open}


def get_clientData():
    clients_obj = []  # Initialize an empty list to store client data

    # Loop through all clients
    for client in active_clients.keys():
        if active_clients[client] == True:
            MTM = get_actual_client_MTM(client)
            client_data = {
                'name': client,  # Client name
                'MTM': round(MTM, 2),
                'Portfolio Value': pf_values[clients[client]['user_id']]
            }
            # Append the client's data to the list
            clients_obj.append(client_data)


    # Loop through each client data to update order counts
    for client_data in clients_obj:
        order_counts = get_open_and_complete_order_count(client_data['name'])
        client_data['openOrderCount'] = order_counts[1]
        client_data['CompleteOrderCount'] = order_counts[0]

    return {
        "client_data": clients_obj,
        "connection_data": {
            'time': get_time(),
            "live_index": get_index_ltp(),
            'history_live_index': get_history_index_ltp(),
        },
        "time": get_time()
    }


# def give_var_alert():
#     # Configuration: allowed users and their alert limits
#     user_groups = {
#         'Jainam Accounts': {
#             'users': {'Swan Prop Live XTS', 'Swan Prop Live XTS 2', 'Swan Prop Live XTS 3', 'Swan Prop Live XTS 4'},
#             'limit': -150_000_000,
#             'label': 'Prop Accounts'
#         },
#         'KsMarwadiXTS': {
#             'users': {'Kavan Marwadi Prop'},
#             'limit': -22500000,
#             'label': 'Kavan Marwadi Account'
#         }
#     }

#     # Fields we care about
#     fields_to_keep = {'User', 'BrokerUpside', 'BrokerDownside'}

#     # Fetch data
#     data, _ = get_uservarcalculations(20)

#     def process_group(group_name, group_info):
#         filtered = [
#             {key: entry[key] for key in fields_to_keep}
#             for entry in data
#             if entry['User'] in group_info['users']
#         ]

#         total_up = sum(entry['BrokerUpside'] for entry in filtered)
#         total_down = sum(entry['BrokerDownside'] for entry in filtered)

#         if total_up <= group_info['limit']:
#             r.hset('heartbeat_custom','var_alert',False)
#             send_telegram_alert(f'Upside Var Breached  For {group_info["label"]}: {total_up}')
#         elif total_down <= group_info['limit']:
#             r.hset('heartbeat_custom','var_alert',False)
#             send_telegram_alert(f'Downside Var Breached  For {group_info["label"]}: {total_down}')
#         else:
#             r.hset('heartbeat_custom','var_alert',True)
        

#     # Process each user group
#     for group in user_groups:
#         process_group(group, user_groups[group])


import datetime

def give_var_alert():
    # Configuration per group, including the get_uservarcalculations() parameter
    user_groups = {
        'Jainam Accounts': {
            'users':      {'Swan Prop Live XTS', 'Swan Prop Live XTS 2', 'Swan Prop Live XTS 3', 'Swan Prop Live XTS 4'},
            'limit':      -130000000,
            'label':      'Prop Accounts',
            'check_time': datetime.time(9, 15),  # start after 09:15
            'lookback':   20                     # <-- pass this into get_uservarcalculations()
        },
        'KsMarwadiXTS': {
            'users':      {'Kavan Marwadi Prop'},
            'limit':      -22500000,
            'label':      'Kavan Marwadi Account',
            'check_time': datetime.time(15, 16), # start after 15:16
            'lookback':   10                     # <-- and this
        }
    }

    fields_to_keep = {'User', 'BrokerUpside', 'BrokerDownside'}
    now = datetime.datetime.now().time()

    for group_name, info in user_groups.items():
        # skip if it's not yet time to check this group
        if now < info['check_time']:
            continue

        # fetch VAR data with the group-specific lookback
        data, _ = get_uservarcalculations(info['lookback'])

        # filter to just this group's users
        filtered = [
            {k: entry[k] for k in fields_to_keep}
            for entry in data
            if entry['User'] in info['users']
        ]

        total_up   = sum(e['BrokerUpside']   for e in filtered)
        total_down = sum(e['BrokerDownside'] for e in filtered)

        # fire or clear the alert as before
        if total_up <= info['limit']:
            r.hset('heartbeat_custom', 'var_alert', False)
            send_telegram_alert(f"Upside Var Breached For {info['label']}: {total_up}")
        elif total_down <= info['limit']:
            r.hset('heartbeat_custom', 'var_alert', False)
            send_telegram_alert(f"Downside Var Breached For {info['label']}: {total_down}")
        else:
            r.hset('heartbeat_custom', 'var_alert', True)




def get_userid(client):
    return clients.get(client).get('user_id')

def get_main_data():
    now_time = datetime.datetime.now()
    global squareOffFlagDict,squareOffModeDict       
    if (now_time.hour== 8 and now_time.minute==00) or (now_time.hour== 3 and now_time.minute==35) :
        squareOffFlagDict=r.hgetall('sq_off_flag')
        squareOffModeDict=r.hgetall('sq_off_mode')

    clients_obj = []  # Initialize an empty list to store client data
 

    # Loop through all clients
    for client in active_clients.keys():
        if active_clients[client] == True:
            MTM = get_actual_client_MTM(client)
            Ideal_MTM = get_idealMTM(client)
            Peak_Margin = get_client_peak_margin(client)
            balance=r.hgetall('client_balance')
            idealturnover=r.hget("Ideal Turn Over", client) or 1
            slip2=r.hget('Slippage 1', client)
            rejected_orders = r.hget('rejected_orders', client)
            pending_orders = r.hget('pending_orders', client)
            position = r.hget('live_user_positions', client)
            margin = r.hget('curr_client_margin', client)
            api_pnl=r.hget('client_api_pnl',client)
            cashperpf=round((get_client_client_balance(client, 'cashAvailable',balance)/pf_values[clients[client]['user_id']])*100,2)
            slippage=round(get_client_slippage(MTM, Ideal_MTM), 2)
            holdingdaypnl=r.hget('client_holdingspnl', client) or 0
            broker=get_broker(client)
            userid=get_userid(client)
            client_data = {
                'name': client,  # Client name
                'broker': broker,
                'ideal_MTM': round(Ideal_MTM, 2),
                'MTM': round(MTM, 2),
                'IdealTurnover':round(idealturnover,2), 
                'Slippage2': round_slippage(slip2),
                'Rejected_orders': getRejectedOrders(rejected_orders),
                'Pending_orders': getPendingOrders(pending_orders),
                'OpenQuantity': get_open_qty(position),
                "NetQuantity": get_net_qty(position),
                'HoldingPnl':holdingdaypnl,
                "Live_Client_Margin": get_ideal_client_margin(margin),
                # "Live_Client_Var": get_ideal_client_var(client),
                'Slippage': slippage,
                # 'SlippagePer':round(get_client_slippage_per(slippage,Ideal_MTM,slip2), 2),
                'SlippagePer':(slippage / idealturnover) * 100,
                'PNL Overall %': get_client_pnl_overall_percentage(MTM,pf_values[clients[client]['user_id']]),
                'PNL Utilized %': get_client_pnl_Utilized_percentage(MTM, Peak_Margin),
                'Portfolio Value': pf_values[clients[client]['user_id']],
                'API DAY PNL': round(safe_convert_number(api_pnl['api_day_pnl'] if api_pnl is not None else 0.0), 2),
                'API NET PNL': round(safe_convert_number(api_pnl['api_net_pnl'] if api_pnl is not None else 0.0), 2),
                'Peak Margin': Peak_Margin,
                "availableMargin": round(get_client_client_balance(client, 'marginAvailable',balance), 2),
                "cashAvailable": round(get_client_client_balance(client, 'cashAvailable',balance), 2),
                'marginUtilized': round(get_client_client_balance(client, 'marginUtilized',balance), 2),
                'Cashperpf': cashperpf,
                'AccountId':clients[client].get('username'),
                'ob_cnt':r.hget('system_ob_cnt', client),
                'cashalertper':cashalertinputs.get(userid),
                'squareOffFlag':squareOffFlagDict.get(client),
                'squareOffMode':squareOffModeDict.get(client)
            }
            now_time = datetime.datetime.now()
            # define cutoff as 15:30:00
            cutoff = datetime.time(15, 30, 0)


            cash_alert_percentage=cashalertinputs[userid]
            if cashperpf <= cash_alert_percentage:
                if now_time.minute == 30 and now_time.second == 0 and (now_time<=cutoff):
                    send_telegram_alert(f'{client} cash is less than {cashperpf}%')
                    
            if now_time.minute%2==0 and now_time.second==0 and (now_time.time() <= cutoff) :
                give_var_alert()
                


            # Append the client's data to the list
            clients_obj.append(client_data)


    # Loop through each client data to update order counts
    for client_data in clients_obj:
        order_counts = get_open_and_complete_order_count(client_data['name'])
        client_data['openOrderCount'] = order_counts[1]
        client_data['CompleteOrderCount'] = order_counts[0]

    # Prepare the final response dictionary

      # Check trading hours
    current_time = datetime.datetime.now().time().replace(microsecond=0)

    # if current_time in[datetime.time(16, 00,00)]:
    #     eod_checks()

    b_p_mis,p_b_mis=give_pos_mismatch()
    return {
        "client_data": clients_obj,
        "connection_data": {
            'time': get_time(),
            "live_index": get_index_ltp(),
            'long_options_indicator':give_longoptions_indicators(),
            'history_live_index': get_history_index_ltp(),
            'pulse': read_pulse_updates(),
            'position_mismatch': read_position_mismatch(),
            "ws3": {},
            "ws4": {},
            'broker_Position_Mismatch':b_p_mis,
            'position_broker_Mismatch':p_b_mis,
            'get_open_trade_to_signalbook_mismatch': get_open_trade_to_signalbook_mismatch() if current_time in [datetime.time(9, 11,00)] else [] ,
            "custom_pulse":r.hgetall('heartbeat_custom')
        },
        "time": get_time(),
    }


def make_test_error():
    arr = [
        'websocket_shut_down',
        'shut_down_my_program',
        'trader_xts_shut_down',
        'trader_zerodha_shut_down',
        'shut_down_pulse_run_strats',
        'shut_down_pulse_check_net_positions'
    ]
    map={}
    for key in arr:
        shutdowns = r.lrange(key, 0, -1)  # Assuming 'r' is a Redis connection or similar object
        shutdowns.reverse()
        map[key]=shutdowns
    return map



def give_mismatch(map_a,map_b,ignore,client,type):
     arr=[]
     for key,value in map_a.items():
            if value == 0 :
                continue
            gg = ignore[ignore['Symbol'] == key].get(client, [])
            ignore_qt=0
            if len(gg) > 0:
                ignore_qt=gg.tolist()[0]

            if key in map_b:
                temp_qt=value-map_b[key]
                if temp_qt==0:
                    continue
                checked=False
                if ignore_qt == ( (value-map_b[key]) if type==0 else (map_b[key]-value)):
                    checked=True
                arr.append({'Symbol':key,'Quantity':value-map_b[key],'Checked':checked})      
            else:
                checked=False
                if ignore_qt==value:
                    checked=True
                arr.append({'Symbol':key,'Quantity':value,'Checked':checked})    
            
     return arr

def filter_list(symbol_to_remove,client_data):
    return list(filter(lambda x: x["Symbol"] != symbol_to_remove, client_data))

def give_pos_mismatch():
    ignore_broker_position_mismatch_trades=r.get('broker_position_mismatch')
    user_map={}
    user_map_2={}
    for client,val in clients.items():
        if active_clients[client]==False:
            continue
        broker=val['broker']
        a=get_zerodha_position_book(client)
        b=get_client_rms_df(client)
        if a==None or b==None :
            user_map[client]=[]
            user_map_2[client]=[]
            continue

        map_broker={}
        map_pos={}

        symbol_in_a='tradingsymbol'
        quantity_in_a='quantity'

        if broker=='xts':
            symbol_in_a='TradingSymbol'
            quantity_in_a='Quantity'


        for trade in a:
            map_broker[trade[symbol_in_a]]= map_broker[trade[symbol_in_a]] + int(trade[quantity_in_a]) if trade[symbol_in_a] in map_broker else int(trade[quantity_in_a])
            
        for trade in b:
            map_pos[trade['symbol']]=map_pos[trade['symbol']] + int(trade['net_qty']) if trade['symbol'] in map_pos else int(trade['net_qty'])


        user_map[client] = give_mismatch(map_broker, map_pos,ignore_broker_position_mismatch_trades,client,0)
        user_map_2[client] = give_mismatch(map_pos,map_broker,ignore_broker_position_mismatch_trades,client,1)

    return user_map ,user_map_2 

    






def make_new_order_error():
    rejected_orders = []

    for user, order_details in r.hgetall('live_user_ob').items():
        if user in active_clients and active_clients[user]:
            for order in order_details:
                if 'status' in order:
                    if order['status'] == 'REJECTED':
                        timestamp = order['order_timestamp'].strftime("%d-%m-%Y %H:%M:%S")
                        obj = {
                            'Account': user,
                            'Reason': order['status_message'],
                            'Order Id': order['order_id'],
                            'Status': order['status'],
                            'Time': timestamp,
                            'Symbol': order['tradingsymbol'],
                            'Order Type': order['order_type'],
                            'Transaction Type': order['transaction_type'],
                            'Quantity': order['quantity'],
                            'Price': order['price'],
                            # 'Average Price': order['average_price'],
                            # 'Filled Quantity': order['filled_quantity'],
                            'Pending Quantity': order['pending_quantity']
                        }
                       
                        rejected_orders.append(obj)
                else:
                    if order['OrderStatus'] == 'Rejected':
                        timestamp = order['OrderGeneratedDateTime']
                        obj = {
                            'Account': user,
                            'Reason': order['CancelRejectReason'],
                            'Order Id': order['AppOrderID'],
                            'Status': order['OrderStatus'],
                            'Time': timestamp.isoformat() if isinstance(timestamp, datetime.datetime) else timestamp,
                            'Symbol': order['TradingSymbol'],
                            'Order Type': order['OrderType'],
                            'Transaction Type': order['OrderSide'],
                            'Quantity': order['OrderQuantity'],
                            'Price': order['OrderPrice'],
                            # 'Average Price': order['OrderAverageTradedPrice'],
                            # 'Filled Quantity': order['CumulativeQuantity'],
                            'Pending Quantity': order['LeavesQuantity']
                        }
                  
                        
                        rejected_orders.append(obj)

    # Sort the list in descending order by Time
    rejected_orders.sort(
        key=lambda x: datetime.datetime.strptime(x['Time'], '%d-%m-%Y %H:%M:%S') if isinstance(x['Time'], str) else x['Time'],
        reverse=True
    )

    return rejected_orders


    

# Data fetching functionsmake_new_order_error
def get_errorLogs_data():
    
    # val=r.get('rms_heartbeat')
    temp={
        "New_Order_Errors":make_new_order_error(),
        # "Websocket_Errors":check_websocket_error(val),
        #"RS_Errors":check_rs_error(val),
        # "User_Errors":check_user_error(val),
        # "Pulse_Errors":make_test_error(),
        "time":get_time(),
        'User Map': User_Broker_Map
    }
    return temp

def get_signalbook_data():
    today = pd.Timestamp.today().date()
    trades_list = r.lrange('all_trades', 0, -1)
    signal_tradebook = pd.DataFrame(trades_list)
    # signal_tradebook = signal_tradebook[signal_tradebook['timestamp'].dt.date == today]
    signal_tradebook = signal_tradebook.sort_values(by='timestamp', ascending=False)
    signal_tradebook = signal_tradebook.fillna('').infer_objects(copy=False)
    signal_tradebook['time_diff'] = signal_tradebook['system_timestamp'] - signal_tradebook['timestamp']

    # Format time_diff as total seconds with milliseconds
    # Subtract 60 seconds if time_diff is above 60 seconds
    signal_tradebook['time_diff'] = signal_tradebook['time_diff'].apply(
        lambda x: f"{(x.total_seconds() - 60):.3f}" if x.total_seconds() > 60 else f"{x.total_seconds():.3f}"
    )
    # timestamp_column_names = signal_tradebook.select_dtypes(include=['datetime64[ns]']).columns
    timestamp_column_names = signal_tradebook.columns
    # Convert each timestamp column to string
    for column in timestamp_column_names:
        signal_tradebook[column] = signal_tradebook[column].astype(str)   

    # signal_tradebook['quantity']=signal_tradebook['quantity'].astype(str)   
    return {
       "table_data" :signal_tradebook.to_dict(orient='records'),
       "time":get_time()
    }

def signalbook_checker_strat_ignore(uid,action):
    first=uid.split('_')[0]
    if first=='swanpbsar' and action=='BUY':
        return True
    if (first=='swanbtstdir' or first=='swanbtstdirv2') and action =='SELL':
        return True
    return False   




def strategy_wise_quantity_checker(trades,strategy_name,row):
        if pd.isna(row['spot']):
            print("i got na")

        if signalbook_checker_strat_ignore(row['uid'],row['action']):
            return {},True
            

        spot=float(row['spot'])
        price=float(row['price'])
        trade_type= 1
        strat_params_row=strat_params[strategy_name]
        index_quantity=strat_params_row['Strike multiplier'][row['index']]
        system=row['system_tag']
        map={}
        date_row= row['timestamp'].date()
        indices=strat_params_row['Indices']
        systems=strat_params_row['Systems']     
        all_check=True

        today=datetime.datetime.today().date()

        if date_row!=today:
            return {},True
      
        for username,qt in trades.items():
    
            if username not in user_pf_map:
                map[username]=qt
                continue

            capital=row['portfolio_value'][username]
            # if date_row not in user_pf_map[username]:
            #     multiplier=user_pf_map[username][min(user_pf_map[username].keys())]['limits'][strategy_name]['factor1']
            # else:
            #     multiplier=user_pf_map[username][date_row]['limits'][strategy_name]['factor1']

            multiplier = None
            temp_start_date = date_row
            end_date = min(temp_start_date + datetime.timedelta(days=7), today)

            current_date = temp_start_date
            while current_date <= end_date:
                if current_date not in user_pf_map[username]:
                    current_date += datetime.timedelta(days=1)
                    continue
                if user_pf_map[username][current_date]['limits']!=None:
                    multiplier = user_pf_map[username][current_date]['limits'][strategy_name]['factor1']
                    break 
                current_date += datetime.timedelta(days=1)

            if multiplier is None:
                multiplier = user_pf_map[username][max(user_pf_map[username].keys())]['limits'][strategy_name]['factor1']


            if strategy_name=='swanlongoptions' or strategy_name=='swanlongoptions_v2':
                total_exposure=strat_params_row['Exposure']*capital*multiplier
                deno=(indices*systems*price)
                quantity=total_exposure/deno
                if row['index']=='BANKNIFTY' or row['index']=='FINNIFTY':
                   quantity=quantity*2
                correct_quantity = max(round(quantity/index_quantity),1)
                correct_quantity = correct_quantity * index_quantity * trade_type
               
                
                if qt!=correct_quantity:
                    all_check=False
                    map[username]=float(f"{correct_quantity:.1f}")

                 
            elif strategy_name=='swan_positional':
                total_exposure=capital*systemweightage.loc[systemweightage['strat'] == system, 'equityfactor'].values[0]
                quantity= total_exposure/spot*multiplier
                strike_mul=strat_params_row['Strike multiplier'][row['index']]
                correct_quantity=max(round(quantity/strike_mul),1)
                correct_quantity=strike_mul*correct_quantity
                correct_quantity=-correct_quantity
                if qt!=correct_quantity:
                    all_check=False
                    map[username]=float(f"{correct_quantity:.1f}")
            
            elif strategy_name=='swan_dma':
                pass
                
                
           
        
        return map,all_check


def give_portfolio_values(row,trades):
    date_row= row['timestamp'].date()
    map={}
    for user in trades.keys():
        if user in user_pf_map:
            if date_row in user_pf_map[user]:
                map[user]=user_pf_map[user][date_row]['pf']
            else :
                map[user]=user_pf_map[user][min(user_pf_map[user].keys())]['pf']
        else :
            map[user]=0
    return map



# def get_signalbook_data():
#     def getSymbol(symbol):
#         for i, char in enumerate(symbol):
#             if char.isdigit():
#                 return symbol[:i]
#         return symbol

#     key_field_pairs: Set[Tuple[str, str]] = set()
#     trades_list = r.lrange('all_trades', 0, -1)
#     signal_tradebook = pd.DataFrame(trades_list)
#     signal_tradebook['portfolio_value'] = None
#     signal_tradebook['quantity_check'] = None
#     signal_tradebook['checker']=True
#     # signal_tradebook = signal_tradebook[signal_tradebook['timestamp'].dt.date == today]
#     signal_tradebook = signal_tradebook.sort_values(by='timestamp', ascending=False)
#     signal_tradebook = signal_tradebook.fillna('').infer_objects(copy=False)
#     signal_tradebook['time_diff'] = signal_tradebook['system_timestamp'] - signal_tradebook['timestamp']
#     signal_tradebook['time_diff'] = signal_tradebook['time_diff'].apply(
#         lambda x: f"{(x.total_seconds() - 60):.3f}" if x.total_seconds() > 60 else f"{x.total_seconds():.3f}"
#     )
   



#     signal_tradebook['index'] = signal_tradebook['symbol'].apply(getSymbol)
#     # Add hget commands to the pipeline

#     for idx, row in signal_tradebook.iterrows():
#         # Initialize 'ohlc' to 'c'
#         signal_tradebook.at[idx, 'ohlc'] = 'c'
        
#         # Check if the time part of 'timestamp' is 09:07:00
#         if row["timestamp"].strftime("%H:%M:%S") == "09:07:00":
#             signal_tradebook.at[idx, 'ohlc'] = 'c'
#             # Replace time to 09:15:00
#             new_timestamp = row["timestamp"].replace(hour=9, minute=7, second=0, microsecond=0)
#         else:
#             new_timestamp = row["timestamp"]
        
#         # Assign the new timestamp
#         signal_tradebook.at[idx, 'new_timestamp'] = new_timestamp

    
#         key = f'l.tick_{new_timestamp}'
#         field = f"{row['index']}SPOT"

#         key_field_pairs.add((key, field))
#         if (len(row['quantity'])>0) :
#             trades = row['quantity']
#             pf_row= give_portfolio_values(row,trades)
#             signal_tradebook.at[idx, 'portfolio_value'] = pf_row

#     for key, field in sorted(key_field_pairs):  # Sorting ensures consistent order
#         pipe.hget(key, field)

   
#     # Execute the pipeline and retrieve the results
#     results = pipe.execute()
 
#     deserialized_results = [pickle.loads(result) if result else None for result in results]

#     map={}
#     c=0
#     for key, field in sorted(key_field_pairs):  # Sorting ensures consistent order
#         map[key.split('_')[1]+"-"+field]=deserialized_results[c] 
#         c=c+1        

#     signal_tradebook['price_key'] = (signal_tradebook['new_timestamp'].astype(str) + '-' +  signal_tradebook['index'] + 'SPOT' )
    
#     signal_tradebook.loc[:, 'spot'] = signal_tradebook['price_key'].map(map)
#     signal_tradebook['spot'] = signal_tradebook.apply( lambda row: row['spot'][row['ohlc']],   axis=1
#     )
   
#     signal_tradebook.drop('price_key', axis=1, inplace=True)

#     signal_book_position_heartbeat=r.hget('heartbeat_custom','signalbook_position_checker')
#     tell_heartbeat=True
#     for idx, row in signal_tradebook.iterrows():
#         if (len(row['quantity'])>0) :
#             trades = row['quantity']
#             strategy_name=system_tag_to_strat[row['system_tag']]
#             signal_tradebook.loc[idx, ['quantity_check', 'checker']] = strategy_wise_quantity_checker(trades, strategy_name, row)
#             if(signal_tradebook.at[idx, 'checker']==False):
#                 tell_heartbeat=False


#     if signal_book_position_heartbeat!=tell_heartbeat:
#         r.hset('heartbeat_custom','signalbook_position_checker',tell_heartbeat)
        

            


#     for column in signal_tradebook.columns:
#         signal_tradebook[column] = signal_tradebook[column].astype(str)


#     return {
#        "table_data" :signal_tradebook.to_dict(orient='records'),
#        "time":get_time()
#     }






def get_user_uid_curr_data(client):
    userid=clients[client]['user_id']
    client_multiplier=clients[client]['client_multiplier']
    swan_curr_uid_mtm=r.hgetall('swan_live.curr_mtm')
    curr_uid_mtm=r.hgetall('live.curr_mtm')
    arr=[]
    for basket in live_weights.keys():
        if basket in client_multiplier:
            for uid,value in live_weights[basket].items():
                system_tag=r.hget('system_tags',uid)
                if uid in swan_curr_uid_mtm :
                    if userid in swan_curr_uid_mtm[uid]:
                        MTM_revised_value=swan_curr_uid_mtm[uid][userid]*client_multiplier[basket]
                        obj={"UID":system_tag,"MTM": MTM_revised_value}
                        arr.append(obj)
                elif uid in curr_uid_mtm:
                    MTM_revised_value=curr_uid_mtm[uid]*client_multiplier[basket]
                    obj={"UID":system_tag,"MTM": MTM_revised_value}
                    arr.append(obj)
                else :
                    obj={"UID":system_tag,"MTM": 0}
                    arr.append(obj)

    return arr

# def get_user_uid_curr_data(client):
#     userid=clients[client]['user_id']
#     client_multiplier=clients[client]['client_multiplier']
#     swan_curr_uid_mtm=r.hgetall('swan_live.curr_mtm')
#     curr_uid_mtm=r.hgetall('live.curr_mtm')
#     arr=[]
#     for basket in live_weights.keys():
#         if basket in client_multiplier:
#             for uid,value in live_weights[basket].items():
#                 if uid in swan_curr_uid_mtm:
#                     MTM_revised_value=swan_curr_uid_mtm[uid][userid]*client_multiplier[basket]
#                     obj={"UID":uid,"MTM": MTM_revised_value}
#                     arr.append(obj)
#                 elif uid in curr_uid_mtm:
#                     MTM_revised_value=curr_uid_mtm[uid]*client_multiplier[basket]
#                     obj={"UID":uid,"MTM": MTM_revised_value}
#                     arr.append(obj)
#                 else :
#                     obj={"UID":uid,"MTM": 0}
#                     arr.append(obj)
#     return arr


def get_user_uid_live_data(client,systemTagNeeded):
    userid = clients[client]['user_id']
    client_multiplier = clients[client]['client_multiplier']
    systemTagDict = {}
    systemTagWithoutNumbersDict={}
    time_delta = datetime.timedelta(hours=5, minutes=30)
    today = datetime.datetime.now().date()
    systemTagList=[]
    systemTagWithoutNumberList=set()
    for basket, weights in live_weights.items():
        if basket in client_multiplier:
            for uid in weights.keys():
                system_tag=r.hget('system_tags', uid)
                systemTagList.append(system_tag)
                systemTagWithoutNumberList.add(strip_trailing_digits(system_tag))
                if system_tag not in systemTagNeeded:
                    continue
                if uid in swan_basket:
                    a = r.hgetall(f'swan_live.mtm_{uid}')
                    sorted_dict = dict(sorted(a.items(), key=lambda item: datetime.datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S')))
                    arr = []
                    for key, value in sorted_dict.items():
                        updated_time = datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S') + time_delta
                        if updated_time.date() == today:
                            epoch_time = int(updated_time.timestamp())
                            if userid in value:
                                MTM_revised_value = value[userid] * client_multiplier[basket]
                                obj = {"time": epoch_time, "value": MTM_revised_value}
                                arr.append(obj)
                    systemTagDict[system_tag] = arr
                else:
                    ltp_dict = r.hgetall(f'live.mtm_{uid}')
                    sorted_dict = dict(sorted(ltp_dict.items(), key=lambda item: datetime.datetime.strptime(item[0], '%Y-%m-%d %H:%M:%S')))
                    arr = []
                    for key, value in sorted_dict.items():
                        updated_time = datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S') + time_delta
                        if updated_time.date() == today:
                            epoch_time = int(updated_time.timestamp())
                            MTM_revised_value = value * client_multiplier[basket]
                            obj = {"time": epoch_time, "value": MTM_revised_value}
                            arr.append(obj)
                    systemTagDict[system_tag] = arr
    return systemTagDict,systemTagList,list(systemTagWithoutNumberList)


def get_user_uid_last_data(client: str) -> Dict[str, dict]:
    userid = clients[client]['user_id']
    
    client_multiplier = clients[client]['client_multiplier']
    time_delta = datetime.timedelta(hours=5, minutes=30)
    def get_latest_data(data: Dict[str, str], basket: str, uid: str) -> dict:
        if not data:
            return {"time": None, "value": 0}
        # Get the latest key-value pair
        max_time = max(data.keys(), key=lambda k: datetime.datetime.strptime(k, '%Y-%m-%d %H:%M:%S'))
        last_value = data[max_time]
        # Adjust time and calculate MTM revised value
        updated_time = datetime.datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S') + time_delta
        epoch_time = int(updated_time.timestamp())
        if uid in swan_basket:
            if userid in last_value:
                mtm_value= float(last_value[userid])
            else :
                mtm_value=0
        else :
            mtm_value=float(last_value)

        mtm_revised_value = mtm_value * client_multiplier[basket]
        return {"time": epoch_time, "value": mtm_revised_value}
    result_map = {}
    for basket, weights in live_weights.items():
        if basket in client_multiplier:
            for uid in weights.keys():
                data_key = f'swan_live.mtm_{uid}' if uid in swan_basket else f'live_mtm.{uid}'
                data = r.hgetall(data_key)
                result_map[uid] = get_latest_data(data, basket, uid)
    return result_map

async def get_last_strategy_data(client):
    clientStrategyList=get_user_uid_curr_data(client)
    systemTagPnlDict={}
    systemTagPnlList=[]
    for strategyObject in clientStrategyList:
        strat_name=strip_trailing_digits(strategyObject['UID'])
        if strat_name not in systemTagPnlDict:
            systemTagPnlDict[strat_name]=0
        systemTagPnlDict[strat_name]+=strategyObject['MTM']

    for system_tag,pnl in systemTagPnlDict.items():
        systemTagPnlList.append({'SystemTag':system_tag,'PNL':pnl})


    arr={
        # "last":get_user_uid_last_data(client),
        "last":None,
        "curr":clientStrategyList,
        "systemTagPnl":systemTagPnlList,
        "time":get_time()
    }
    return arr



def strip_trailing_digits(s: str) -> str:
    # remove one or more digits at end of string
    return re.sub(r'\d+$', '', s)

async def get_strategy_data(client):
    clientStrategyList=get_user_uid_curr_data(client)
    systemTagPnlDict={}
    systemTagPnlList=[]
    for strategyObject in clientStrategyList:
        strat_name=strip_trailing_digits(strategyObject['UID'])
        if strat_name not in systemTagPnlDict:
            systemTagPnlDict[strat_name]=0
        systemTagPnlDict[strat_name]+=strategyObject['MTM']

    for system_tag,pnl in systemTagPnlDict.items():
        systemTagPnlList.append({'SystemTag':system_tag,'PNL':pnl})

    arr={
        # "live":get_user_uid_live_data(client),
        "live":None,
        "curr":clientStrategyList,
        "systemTagPnl":systemTagPnlList,
        "time":get_time()
    }
    return arr




#IV CHART 


def calculate_minutes_to_next_expiry(given_datetime, name):
   
    if name == 'NIFTY':
        # Nifty expiry is on Thursday
        days_until_thursday = (3 - given_datetime.weekday()) % 7
        next_expiry = given_datetime + datetime.timedelta(days=days_until_thursday)
        expiry_time = next_expiry.replace(hour=15, minute=30, second=0, microsecond=0)
    
    elif name == 'SENSEX':
        # Special logic for Sensex
        if given_datetime.date() >= datetime.date(2025, 1, 1):
            # After or on January 1st, 2025, expiry is on Tuesday
            days_until_tuesday = (1 - given_datetime.weekday()) % 7
            next_expiry = given_datetime + datetime.timedelta(days=days_until_tuesday)
        else:
            # Before January 1st, 2025, expiry is on Friday
            days_until_friday = (4 - given_datetime.weekday()) % 7
            next_expiry = given_datetime + datetime.timedelta(days=days_until_friday)
        expiry_time = next_expiry.replace(hour=15, minute=30, second=0, microsecond=0)
    
    else:
        raise ValueError("Invalid name. Please provide 'nifty' or 'sensex'.")

    # Calculate the time difference in minutes
    time_difference_minutes = int((expiry_time - given_datetime).total_seconds() / 60)
    return time_difference_minutes

 
def get_strike_price(symbol):
    for index in ['NIFTY', 'SENSEX']:
        if index in symbol:
            return symbol.split(index)[1][6:-2]
        

#Pricing Function
def black_scholes(S, K, T, r, sigma, option_type):
    
    # Black-Scholes calculation for Call and Put options
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
 
    if option_type == "CE":
        # Call option formula
        option_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type == "PE":
        # Put option formula
        option_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'CE' for Call or 'PE' for Put.")
    
    return option_price
 
#Historical Volatility
def sigma_value(now,window):
    eq_data = ei.get_all_ticks_by_symbol('NIFTYSPOT')
    eq_data = eq_data[(eq_data['timestamp'].dt.date <= now.date())]
    eq_data=eq_data[eq_data['timestamp'].dt.time==datetime.time(15,29)]
    log_returns = np.log(eq_data['c'] / eq_data['c'].shift(1))
    rolling_std = log_returns.rolling(window=window).std()
    volatility = rolling_std * np.sqrt(252)  # Annualize the standard deviation
    sigma = volatility.iloc[-1]
    # print("Historic volatility:", sigma)
    return sigma
 
#Vega
def vega(S, K, T, R, sigma):
    d1 = (math.log(S / K) + (R + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    vega_value = S * norm.pdf(d1) * math.sqrt(T)
    return vega_value
 
#IV Vega Based derivation
def implied_volatility_NR(S, K, T, R, market_price, sigma,op,tol=1e-5, max_iter=100):
    # sigma = sigma_value()  # Initial guess for volatility
    for i in range(max_iter):
        price = black_scholes(S, K, T, R, sigma,op)  # Use call pricing function
        vega_value = vega(S, K, T, R, sigma)
        diff = market_price - price
        
        if abs(diff) < tol:
            return sigma
        
        sigma = (sigma + diff / vega_value)
    return sigma
 
def implied_volatility_BQ(S, K, T, r, market_price, option_type="CE"):
    # Objective function for Brent's method: difference between model price and market price
    def objective_function(s_val):
        return black_scholes(S, K, T, r, s_val, option_type) - market_price
 
    # Brent's method to find the implied volatility (root of objective function)
    iv = brentq(objective_function, 1e-6, 5.0)  # IV is typically between 0 and 5 (in decimal form)
    
    
    return iv





# Symbol to track
def give_iv_underlying_chart(index,year,month,day):

    symbol = index+'SPOT'
    spot_data=ei.get_all_ticks_by_symbol(symbol)
    spot_data['timestamp'] = pd.to_datetime(spot_data['timestamp'])

    # Start time (9:15 AM) and end time (3:30 PM)
    start_time = datetime.datetime(year, month, day, 9, 15)
    end_time = datetime.datetime(year, month, day, 15, 29)

    # Function to calculate implied volatility
    def calculate_iv(underlying_price, strike_price, time_to_expiry, ltp, option_type):
        try:
            return implied_volatility_BQ(
                float(underlying_price),
                float(strike_price),
                time_to_expiry,
                0.07,
                float(ltp),
                option_type
            ) * 100
        except Exception as e:
            print(f"Error calculating implied volatility ({option_type}): {e}")
            return 0

    # Function to fetch option details and calculate IV
    def process_option(current_time, underlying_price, time_to_expiry, option_type):
        # Fetch option details
        option_symbol = ei.find_symbol_by_moneyness(current_time, index , 0, option_type, 0)
        strike_price = get_strike_price(option_symbol)
        ltp = ei.get_tick(current_time, option_symbol)['c']
         # Validate LTP
        if ltp is None or math.isnan(ltp):
            return None
            


            

        # Calculate implied volatility
        iv = calculate_iv(underlying_price, strike_price, time_to_expiry, ltp, option_type)

        return {
            f'symbol{option_type}': option_symbol,
            f'strikePrice{option_type}': strike_price,
            f'ltp{option_type}': ltp,
            f'iv{option_type}': iv
        }

    # Main processing loop
    def process_data(start_time, end_time):
        arr = []
        current_time = start_time

        # Ensure end_time does not exceed the current time
        now = datetime.datetime.now()
        end_time = min(end_time, now)

        while current_time <= end_time:
            obj = {}
            obj['timestamp'] = current_time 

            # Get underlying price
            underlying_price = ei.get_tick(current_time, symbol)['c']
            obj['underlying'] = underlying_price

            # Calculate time to expiry
            time_to_expiry = calculate_minutes_to_next_expiry(current_time,index) / 525600
            #obj['time_to_expiry'] = time_to_expiry

            # Process CE and PE options
            ce_details = process_option(current_time, underlying_price, time_to_expiry, 'CE')
            pe_details = process_option(current_time, underlying_price, time_to_expiry, 'PE')

            # # Merge details into the object
            # obj.update(ce_details)
            # obj.update(pe_details)

            # Calculate average implied volatility
            if ce_details is None or pe_details is None :
                current_time += datetime.timedelta(minutes=1)
            else:
                obj['ivavg'] = (ce_details['ivCE'] + pe_details['ivPE']) / 2
                obj['ltpsum'] = (ce_details['ltpCE'] + pe_details['ltpPE']) 

                # Append the result
                arr.append(obj)

                # Increment by one minute
                current_time += datetime.timedelta(minutes=1)

        return arr

    # Execute the process and convert results to DataFrame
    data = process_data(start_time, end_time)
    return data


def give_bid_ask_spread_chart(index,expiry):
        
    # pick today's date
    today = datetime.datetime.today().date()

    # define start and end as full datetimes
    start = datetime.datetime.combine(today, datetime.time(9, 15))
    end   = datetime.datetime.combine(today, datetime.time(15, 30))


    # loop minute by minute
    current = start
    map={1:[],2:[],3:[],4:[],5:[],6:[],'Details':{
        1:{'above_ce':0,'above_pe':0},2:{'above_ce':0,'above_pe':0},
        3:{'above_ce':0,'above_pe':0},4:{'above_ce':0,'above_pe':0},
        5:{'above_ce':0,'above_pe':0},6:{'above_ce':0,'above_pe':0}
    }}
    while current <= end:
                # or replace with your per-minute logic
        spot=r.hget(f'l.tick_{current}', f'{index}SPOT')
        if spot==None:
            break
        spot=spot['c']
        
        strike_diff = ei.get_strike_diff(index)
        map_ce={1:0,2:0,3:0,4:0,5:0,6:0}
        map_pe={1:0,2:0,3:0,4:0,5:0,6:0}
        for i in range(1,7):
            #for ce
            itm_ce=spot - (spot*i*0.01)
            itm_pe=spot + (spot*i*0.01)
            itm_ce = f'{index}{expiry}{round(itm_ce/strike_diff)*strike_diff}CE'
            itm_pe = f'{index}{expiry}{round(itm_pe/strike_diff)*strike_diff}PE'
            try :
                bid_data_ce=r.hget(f'bid.tick_{current}',itm_ce)
                ask_data_ce=r.hget(f'ask.tick_{current}',itm_ce)
                bid_data_pe=r.hget(f'bid.tick_{current}',itm_pe)
                ask_data_pe=r.hget(f'ask.tick_{current}',itm_pe)
                map_ce[i]=(ask_data_ce - bid_data_ce) / bid_data_ce * 100
                map_pe[i]=(ask_data_pe - bid_data_pe) / bid_data_pe * 100
            except:
                map_ce[i]=0
                map_pe[i]=0


            map_ce[i]=round(map_ce[i],2)
            map_pe[i]=round(map_pe[i],2)
            gg=current+datetime.timedelta(hours=5,minutes=30)
            
            map[i].append({"timestamp": gg.strftime("%Y-%m-%dT%H:%M:%S"), "bidaskspreadCE":map_ce[i], "bidaskspreadPE":map_pe[i] })
            map['Details'][i]['Symbol_CE']=itm_ce
            map['Details'][i]['Symbol_PE']=itm_pe

            if map_ce[i]>1.0:
                map['Details'][i]['above_ce']+=1
            if map_pe[i]>1.0:
                map['Details'][i]['above_pe']+=1

        current += datetime.timedelta(minutes=1)

    return map



def remap_usernames(
    data: Dict[str, Union[Dict[str, float], float]],
    user_map: Dict[str, str]
) -> Dict[str, Union[Dict[str, float], float]]:
    result = {}
    for system_tag, inner in data.items():
        if isinstance(inner, dict):
            result[system_tag] = {
                user_map.get(username, username): value
                for username, value in inner.items()
            }
        else:
            result[system_tag] = inner
    return result


def compute_live_strategies():
    system_tags=r.hgetall('system_tags')
    def lasted_trade(tradebook,symbol,uid):
        result=None
        price=0
        action=None
        for i in tradebook:
            if i['uid']==uid and i['symbol']==symbol:
                if result==None:
                    result=i['timestamp']
                    price=i['price']
                    action=i['action']
                else :
                    if i['timestamp']>result:
                        result=i['timestamp']
                        price=i['price']
                        action=i['action']
        a=result.strftime("%Y-%m-%d %H:%M:%S") if result else None
        return a,price,action


    live_strats = r.hgetall('live_strats')
    shub_basket_set = set(r.lrange('all_baskets', 0, -1)) - set(r.lrange('swan_baskets', 0, -1))
    active_user_multipliers = {
        user: clients[user]['client_multiplier'] 
        for user, ispresent in active_clients.items() if ispresent
    }

    formatted_strats = {}
    for uid, strat_data in live_strats.items():
        if strat_data.positions and (uid in uidlist):
            basket = swan_basket[uid][0]
            positions = remap_usernames(strat_data.positions,userIdToUserNameMap)
            trades = strat_data.trades
            # Transform positions if basket is in shub_basket_set
            if basket in shub_basket_set:
                positions = {
                    trade: {
                        user: qt * basket_mul[basket]
                        for user, basket_mul in active_user_multipliers.items()
                        if basket in basket_mul
                    }
                    for trade, qt in positions.items()
                }
               # Convert position keys using symbolTOzerodhasymbol
            transformed_positions = {}
            timing={}
            price={}
            action={}
            live_ltp={}
            new_pnl_table={}
            for symbol, pos_data in positions.items():
                transformed_positions[symbol] = pos_data
                timing[symbol],price[symbol],action[symbol]=lasted_trade(trades,symbol,uid)
                live_ltp[symbol]=r.get(f'ltp.{symbol}')
                mpp={}
                for user,qt in pos_data.items():
                    username = userIdToUserNameMap[user] if user in userIdToUserNameMap else user
                    mpp[username]=round((live_ltp[symbol] - price[symbol]) * qt, 2)

                new_pnl_table[symbol]=mpp
            

            formatted_strats[uid] = {
                'systemtag': system_tags[uid],
                'strategyType': basket,
                'positions': transformed_positions,
                'timing':timing,
                'price':price,
                'action':action,
                'ltp':live_ltp,
                'pnl':new_pnl_table
            }
    return formatted_strats

def give_strike(symbol):
    if symbol == None:
        return None , None , None
    for i,char in enumerate(symbol):
        if char.isdigit():
            if symbol[:i] not in valid_index:
              return symbol[:i],None,None
            return symbol[:i],int(symbol[i+6:-2]),symbol[-2:]
    return None , None , None
    

def calculate_intrinsic_value(spot,strike,tradetype):
    if tradetype =='CE':
       return spot-strike if spot>strike else 0
    else:
       return strike-spot if spot<strike else 0




def get_uservarcalculations(percentage):
    usermap = {}
    userqt={}

    for client, value in clients.items():
        if active_clients[client]:
            usermap[client] = {'Upside': 0, 'Downside': 0, 'BrokerUpside': 0, 'BrokerDownside': 0 }
            userqt[client]={
                'NIFTY':{'CE':{},'PE':{}},'BANKNIFTY':{'CE':{},'PE':{}},'SENSEX':{'CE':{},'PE':{}},'FINNIFTY':{'CE':{},'PE':{}},
                'NIFTYBROKER':{'CE':0,'PE':0},'BANKNIFTYBROKER':{'CE':0,'PE':0},'SENSEXBROKER':{'CE':0,'PE':0},'FINNIFTYBROKER':{'CE':0,'PE':0}
            }
            for basket in r.lrange('all_baskets', 0, -1):
                usermap[client][f'{basket}Upside'] = 0
                usermap[client][f'{basket}Downside'] = 0

    for key, value in compute_live_strategies().items():
        for symbol, positions in value['positions'].items():
            
            for user, qt in positions.items():
                if user not in usermap:
                    continue
                    # usermap[user] = {'Upside': 0, 'Downside': 0}
                    # userqt[user]={
                    #     'NIFTY':{'CE':{},'PE':{}},'BANKNIFTY':{'CE':{},'PE':{}},'SENSEX':{'CE':{},'PE':{}},'FINNIFTY':{'CE':{},'PE':{}},
                    #     'NIFTYBROKER':{'CE':0,'PE':0},'BANKNIFTYBROKER':{'CE':0,'PE':0},'SENSEXBROKER':{'CE':0,'PE':0},'FINNIFTYBROKER':{'CE':0,'PE':0}
                    # }
                
                strat_nameup=f'{value["strategyType"]}Upside'
                strat_namedown=f'{value["strategyType"]}Downside'
                if strat_nameup not in usermap[user] or strat_namedown not in usermap[user]:
                    usermap[user][f'{value["strategyType"]}Upside'] = 0
                    usermap[user][f'{value["strategyType"]}Downside'] = 0

                ltp = value['ltp'][symbol]
                index, strike, tradetype = give_strike(symbol)
                if index not in valid_index:
                    continue
                spot = r.get(f'ltp.{index}SPOT')
                upchange = spot * (percentage / 100) + spot
                downchange = spot - spot * (percentage / 100)
                upchangedltp = calculate_intrinsic_value(upchange, strike, tradetype)
                downchangedltp = calculate_intrinsic_value(downchange, strike, tradetype)
                profitlossup = (upchangedltp - ltp) * qt
                profitlossdown = (downchangedltp - ltp) * qt
                usermap[user]['Upside'] += profitlossup
                usermap[user]['Downside'] += profitlossdown
                usermap[user][f'{value["strategyType"]}Upside'] += profitlossup
                usermap[user][f'{value["strategyType"]}Downside'] += profitlossdown
                userqt[user][index][tradetype][value["strategyType"]] = userqt[user][index][tradetype].get(value["strategyType"], 0) + qt


    for client, value in clients.items():
        if not active_clients[client]:
            continue
        gg = get_zerodha_position_book(client)
        if gg is None:
            continue
        symbolkey = 'TradingSymbol'
        quantity = 'Quantity'
        user = client
        if value['broker'] == 'zerodha':
            symbolkey = 'tradingsymbol'
            quantity = 'quantity'
        for trade in gg:
            symbol_trade = trade[symbolkey]
            quantity_trade = int(trade[quantity])
            ltp = r.get(f'ltp.{symbol_trade}')
            if ltp is None:
                continue
            index, strike, tradetype = give_strike(symbol_trade)
            if index not in valid_index:
                continue
            spot = r.get(f'ltp.{index}SPOT')
            if spot is None:
                continue
            upchange = spot * (percentage / 100) + spot
            downchange = spot - spot * (percentage / 100)
            upchangedltp = calculate_intrinsic_value(upchange, strike, tradetype)
            downchangedltp = calculate_intrinsic_value(downchange, strike, tradetype)
            profitlossup = (upchangedltp - ltp) * quantity_trade
            profitlossdown = (downchangedltp - ltp) * quantity_trade
            usermap[user]['BrokerUpside'] += profitlossup
            usermap[user]['BrokerDownside'] += profitlossdown
            userqt[user][f'{index}BROKER'][tradetype]+=quantity_trade

    pf_values = r.hgetall('user_pf_value')
    arr = []
    for key, value in usermap.items():
        new_record = {'User': key}
        usernewmap = {}
        for side, pnl in value.items():
            usernewmap[side] = pnl
            usernewmap[f'{side}%'] = round(((pnl * 100) / pf_values[userNameToUserIdMap[key]]), 2)
        new_record.update(usernewmap)
        arr.append(new_record)
  
    return arr,userqt





def give_columns_sum(columns,map_of_strat):
    upside=0
    downside=0
    for column in columns:
        upside+=map_of_strat[f'{column}Upside']
        downside+=map_of_strat[f'{column}Downside']
    return upside , downside


def give_trade_calc(trades,percentage,quantity_map):
    upcustomtrade=0
    downcustomtrade=0
    premium = 0
    for trade in trades:
        qt=trade['quantity']
        ltp =  r.get(f'ltp.{trade["symbol"]}')
        premium+=(qt*ltp)
        index, strike, tradetype = give_strike(trade['symbol'])
        if index not in valid_index:
            continue
        spot = r.get(f'ltp.{index}SPOT')
        upchange = spot * (percentage / 100) + spot
        downchange = spot - spot * (percentage / 100)
        upchangedltp = calculate_intrinsic_value(upchange, strike, tradetype)
        downchangedltp = calculate_intrinsic_value(downchange, strike, tradetype)
        profitlossup = (upchangedltp - ltp) * qt
        profitlossdown = (downchangedltp - ltp) * qt
        upcustomtrade += profitlossup
        downcustomtrade += profitlossdown
        quantity_map[index][tradetype]+=qt
        quantity_map[f'{index}BROKER'][tradetype]+=qt
    return upcustomtrade,downcustomtrade,premium

def summarize_ce_pe(df):
    valid_index = ('NIFTY', 'BANKNIFTY', 'SENSEX', 'FINNIFTY')
    df_t = df.set_index('Symbol').T
    result = {}
    for user, row in df_t.iterrows():
        result[user] = {prefix: {'CE': 0, 'PE': 0} for prefix in valid_index}
        for symbol, qty in row.items():
            prefix = next((idx for idx in valid_index if symbol.startswith(idx)), None)
            if not prefix:
                continue
            if symbol.endswith('CE'):
                result[user][prefix]['CE'] += qty
            elif symbol.endswith('PE'):
                result[user][prefix]['PE'] += qty
    return result


def give_quantity_map(users,quantities):

    valid_index = ('NIFTY', 'BANKNIFTY','SENSEX','FINNIFTY')
    manual_order_all_user = summarize_ce_pe(r.get('broker_position_mismatch'))
    map={}

    for user in users:
        username=user['userId']
        user_baskets=user['baskets']
        defaultQuantityMap={'NIFTY': {'CE': 0, 'PE': 0}, 'BANKNIFTY': {'CE': 0, 'PE': 0}, 'SENSEX': {'CE': 0, 'PE': 0}, 'FINNIFTY': {'CE': 0, 'PE': 0}}
        user_quantity=quantities[username]
        manual_order = manual_order_all_user[username] if username in manual_order_all_user else defaultQuantityMap
        for v_i in valid_index:
            if v_i not in map:
                map[v_i]={'CE':0,'PE':0}
                map[f'{v_i}BROKER']={'CE':0,'PE':0}
            
        for index,value in user_quantity.items():
            for type, quan in value.items():
                if isinstance(quan, dict):
                    for strat, qt in quan.items():
                        if strat in user_baskets:
                            map[index][type]+=qt
                            map[f'{index}BROKER'][type]+=qt
        for index,value in manual_order.items():
            map[f'{index}BROKER']['CE']+=value['CE']
            map[f'{index}BROKER']['PE']+=value['PE']
    return map


def give_var_table(request,compute_live_strategies,percentage_range):
    usermap={}
    client=request['client']
    user_info=clients[client]
    user_id=user_info['user_id']
    broker=user_info['broker']

    if active_clients[client]:
        for percentage in range(1,percentage_range+1):
            usermap[f'{percentage}%']={'Upside':0,'Downside':0,'BrokerUpside':0,'BrokerDownside':0}
            for basket in r.lrange('all_baskets', 0, -1):
                usermap[f'{percentage}%'][f'{basket}Upside']=0
                usermap[f'{percentage}%'][f'{basket}Downside']=0


    for key,value in compute_live_strategies.items():
        for symbol,positions in value['positions'].items():
            for user,qt in positions.items():
                if user !=user_id:
                    continue
            
                ltp=value['ltp'][symbol]
                index,strike,tradetype=give_strike(symbol)
                if index not in valid_index:
                    continue
                spot=r.get(f'ltp.{index}SPOT')
                for percentage in range(1,percentage_range+1):
                    
                    
                    upchange=spot*(percentage/100) + spot
                    downchange=spot-spot*(percentage/100) 
                    upchangedltp=calculate_intrinsic_value(upchange,strike,tradetype)
                    downchangedltp=calculate_intrinsic_value(downchange,strike,tradetype)
                    profitlossup=(upchangedltp-ltp)*qt
                    profitlossdown=(downchangedltp-ltp)*qt
                    usermap[f'{percentage}%']['Upside']+=profitlossup
                    usermap[f'{percentage}%']['Downside']+=profitlossdown
                    usermap[f'{percentage}%'][f'{value["strategyType"]}Upside']+=profitlossup
                    usermap[f'{percentage}%'][f'{value["strategyType"]}Downside']+=profitlossdown

    gg= get_zerodha_position_book(client)
    symbolkey='TradingSymbol'
    quantity='Quantity'

    if broker=='zerodha':
        symbolkey='tradingsymbol'
        quantity='quantity'

    for trade in gg:
        symbol_trade = trade[symbolkey]
        quantity_trade = int(trade[quantity])
        ltp = r.get(f'ltp.{symbol_trade}')
        if ltp is None:
            continue
        index, strike, tradetype = give_strike(symbol_trade)
        if index not in valid_index:
            continue
        spot = r.get(f'ltp.{index}SPOT')
        if spot is None:
            continue
        for percentage in range(1,percentage+1):
            upchange = spot * (percentage / 100) + spot
            downchange = spot - spot * (percentage / 100)
            upchangedltp = calculate_intrinsic_value(upchange, strike, tradetype)
            downchangedltp = calculate_intrinsic_value(downchange, strike, tradetype)
            profitlossup = (upchangedltp - ltp) * quantity_trade
            profitlossdown = (downchangedltp - ltp) * quantity_trade
            usermap[f'{percentage}%']['BrokerUpside']+=profitlossup
            usermap[f'{percentage}%']['BrokerDownside']+=profitlossdown

    pf_values=r.hgetall('user_pf_value')
    arr = []
    for key, value in usermap.items():
        new_record = {'User': key}
        usernewmap={}
        for side,pnl in value.items():
            usernewmap[side]=pnl
            usernewmap[f'{side}%']=round(((pnl*100)/pf_values[user_id]),2)
        new_record.update(usernewmap)
        arr.append(new_record)


    return arr

def strip_side(s: str,suffix) -> str:
    if s.lower().endswith(suffix.lower()):
        return s[:-len(suffix)]
    return None

def combine_by_user(arrays: List[List[Dict[str, Union[float, str]]]]
                  ) -> List[Dict[str, Union[float, str]]]:
    # 1) collect all rows per User
    user_map: Dict[str, List[Dict[str, Union[float, str]]]] = {}
    for arr in arrays:
        for entry in arr:
            user = entry['User']
            user_map.setdefault(user, []).append(entry)

    # 2) for each user, sum/average across their rows
    combined = []
    for user, rows in user_map.items():
        n = len(rows)
        result = {'User': user}
        for key in rows[0].keys():
            if key == 'User':
                continue
            vals = [r[key] for r in rows]
            if key.endswith('%'):
                result[key] = round(sum(vals) / n, 2)
            else:
                result[key] = round(sum(vals), 2)
        combined.append(result)

    return combined


# 1) Cache your strptime – avoid reparsing the same string over and over
@lru_cache(maxsize=None)
def parse_ts(ts_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")

def get_user_systemTag_without_number_live_data(client, systemTagNeeded):
    userid = clients[client]['user_id']
    multipliers = clients[client]['client_multiplier']
    time_delta = datetime.timedelta(hours=5, minutes=30)
    today = datetime.datetime.now().date()

    systemTagDict = {}

    for basket, weights in live_weights.items():
        if basket not in multipliers:
            continue
        client_mul = multipliers[basket]

        for uid, _ in weights.items():
            system_tag = strip_trailing_digits(r.hget('system_tags', uid))
            if system_tag not in systemTagNeeded:
                continue

            # ensure our bucket exists
            systemTagDict.setdefault(system_tag, {})

            # pick the right key prefix
            key_prefix = 'swan_live.mtm_' if uid in swan_basket else 'live.mtm_'
            raw = r.hgetall(f"{key_prefix}{uid}")

            # Instead of sorting all entries every time,
            # filter *and* convert timestamp once:
            for ts_str, raw_val in raw.items():
                # parse once
                dt = parse_ts(ts_str) + time_delta
                if dt.date() != today:
                    continue

                epoch = int(dt.timestamp())
                # extract the numeric value for MTM
                if uid in swan_basket:
                    # raw_val is a dict-like; only include if this user is in it
                    if userid not in raw_val:
                        continue
                    val = raw_val[userid] * client_mul
                else:
                    val = raw_val * client_mul

                # accumulate
                systemTagDict[system_tag].setdefault(epoch, 0.0)
                systemTagDict[system_tag][epoch] += val

    # Build chart-friendly list, sorted by time
    systemTagChartData = {}
    for tag, point_dict in systemTagDict.items():
        # sort by epoch ascending
        data = [
            {"time": ts, "value": pnl}
            for ts, pnl in sorted(point_dict.items())
        ]
        systemTagChartData[tag] = data

    return systemTagChartData



def give_psar_chart(dff,custom_psar_af,custom_psar_max_af):
    today_9am = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 0))
    last30kBefore9am = dff[dff['timestamp'] <= today_9am].tail(30000)
    after9amToday=dff[dff['timestamp'] > today_9am]
    combined_df = pd.concat([last30kBefore9am, after9amToday]).reset_index(drop=True)
    combined_df = combined_df.sort_values(by='timestamp').reset_index(drop=True)
    dff=combined_df

    dff['timestamp'] = pd.to_datetime(dff['timestamp'])
    mask_907 = (dff['timestamp'].dt.hour == 9) & (dff['timestamp'].dt.minute == 7)
    df_907 =dff[mask_907].copy()
    df_907['timestamp'] = df_907['timestamp'] + pd.Timedelta(minutes=3)
    df_907=pd.DataFrame(df_907)
    df_no_907 = dff[~mask_907].copy()
    df_no_907['timestamp'] = pd.to_datetime(df_no_907['timestamp'])
    df_no_907['group_end'] = df_no_907['timestamp'].dt.floor('5T') + pd.Timedelta(minutes=4)
    bars5 = (
        df_no_907
        .groupby('group_end', as_index=False)
        .agg(
            o   = ('o',  'first'),
            h   = ('h',  'max'),
            l   = ('l',  'min'),
            c   = ('c',  'last'),
            v   = ('v',  'sum'),
            oi  = ('oi', 'last'),
        )
        .rename(columns={'group_end':'timestamp'})
    )
    df_no_907=pd.DataFrame(bars5)
    combined = pd.concat([df_907, df_no_907], ignore_index=True)
    combined = combined.sort_values('timestamp').reset_index(drop=True)
    dff=pd.DataFrame(combined)


    # --------------------------------------------------------------------------- #
    # 2)  PARABOLIC SAR (Wilder / TradingView) ---------------------------------- #
    # --------------------------------------------------------------------------- #
    def calculate_psar_tv(df: pd.DataFrame,
                        max_af: float = 0.02,
                        af: float = 0.20) -> pd.DataFrame:
        """
        Parabolic SAR that matches TradingView’s ta.sar().
        Returns a copy of df with 'psar' and 'psar_trend' (1 up, -1 down).
        """
        data = df.resample('5min' ,on='timestamp').agg({'o':'first', 'h': 'max', 'l': 'min', 'c':'last'}).between_time("9:05", "15:30").dropna().reset_index()

        max_acceleration = max_af
        acceleration = af

        # Prepare arrays
        highs = data['h'].values
        lows = data['l'].values
        n = len(data)

        psar = np.full(n, np.nan)  # Pre-allocate PSAR array
        trend = np.ones(n, dtype=int)  # 1 for uptrend, -1 for downtrend
        extreme_point = np.zeros(n)
        acceleration_factor = np.full(n, acceleration)

        # Initial conditions
        psar[0] = highs[0]  # Start with the high as the initial PSAR
        extreme_point[0] = highs[0]

        # Iterative logic using a vectorized approach
        for i in range(1, n):
            # Calculate PSAR
            psar[i] = psar[i - 1] + acceleration_factor[i - 1] * (extreme_point[i - 1] - psar[i - 1])

            if trend[i - 1] == 1:  # Uptrend
                # Update extreme point for uptrend
                extreme_point[i] = max(extreme_point[i - 1], highs[i])
                # Check for trend reversal
                if lows[i] < psar[i]:
                    trend[i] = -1
                    psar[i] = extreme_point[i - 1]
                    extreme_point[i] = lows[i]
                    acceleration_factor[i] = acceleration
                else:
                    trend[i] = 1
                    acceleration_factor[i] = min(acceleration_factor[i - 1] + acceleration, max_acceleration)
            else:  # Downtrend
                # Update extreme point for downtrend
                extreme_point[i] = min(extreme_point[i - 1], lows[i])
                # Check for trend reversal
                if highs[i] > psar[i]:
                    trend[i] = 1
                    psar[i] = extreme_point[i - 1]
                    extreme_point[i] = highs[i]
                    acceleration_factor[i] = acceleration
                else:
                    trend[i] = -1
                    acceleration_factor[i] = min(acceleration_factor[i - 1] + acceleration, max_acceleration)

        # Convert PSAR to DataFrame and return the last value
        psar_df_opt = pd.DataFrame(psar, index=data.index)
        return psar_df_opt

    psar_systems = [
        {"name":"custom",  "af": 0.001,  "max_af":0.001},
        {"name": "psar1",  "af": 0.001,  "max_af": 0.001},
        {"name": "psar2",  "af": 0.0015, "max_af": 0.0015},
        {"name": "psar3",  "af": 0.002,  "max_af": 0.002},
        {"name": "psar4",  "af": 0.0025, "max_af": 0.0025},
        {"name": "psar5",  "af": 0.003,  "max_af": 0.003},
        {"name": "psar6",  "af": 0.0035, "max_af": 0.0035},
        {"name": "psar7",  "af": 0.004,  "max_af": 0.004},
        {"name": "psar8",  "af": 0.0045, "max_af": 0.0045},
        {"name": "psar9",  "af": 0.005,  "max_af": 0.005},
        {"name": "psar10", "af": 0.01,   "max_af": 0.01},
        {"name": "psar11", "af": 0.015,  "max_af": 0.015},
        {"name": "psar12", "af": 0.02,   "max_af": 0.02},
        {"name": "psar13", "af": 0.025,  "max_af": 0.025},
        {"name":"custom",'af':custom_psar_af,"max_af":custom_psar_max_af}
    ]


    bars5 = dff


    for psarSystem in psar_systems:
        calculatedSystemPsarValues=calculate_psar_tv(bars5, max_af=psarSystem['af'], af=psarSystem['max_af'])
        bars5[psarSystem['name']]=calculatedSystemPsarValues
    bars5.drop(columns=['v', 'oi'], errors='ignore', inplace=True)
    # 1️⃣ remove tz and add the offset
    bars5['timestamp'] = (
        bars5['timestamp']
        .dt.tz_localize(None)
        + pd.Timedelta(hours=5, minutes=30)
    )

    # 2️⃣ now format that Series
    bars5['timestamp'] = bars5['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return {'Data':bars5.to_dict(orient="records"),'table':None}

def give_long_chart(dff,index,long_options_settings):
    bars5 = dff.tail(500).copy()
    type='o'
    time_str = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 15)).strftime('%Y-%m-%d %H:%M:%S')
    percentage=0.005
    verticalLineTime=f'{datetime.datetime.today().date()} 09:15:00'

    if long_options_settings['system']=='custom':
        type='o' if long_options_settings['custom']["priceType"]=='open' else 'c'
        dt = datetime.datetime.strptime(long_options_settings['custom']["dateTime"], "%Y-%m-%dT%H:%M")
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        percentage=float(long_options_settings['custom']["percentage"])*0.01
        
        
    else:
        if index=="NIFTY" or index=='SENSEX':
            systems_data=long_options_system['NIFTYSENSEX']
        else:
            systems_data=long_options_system['BANKNIFTYFINNIFTY']
        selected_system=systems_data[long_options_settings['system']]
        today=datetime.datetime.today().date()
        time_str=f"{today} {selected_system['time']}"  
        type= selected_system['type']
        percentage=float(selected_system["percentage"])*0.01
        verticalLineTime=f'{datetime.datetime.today().date()} {selected_system["check"]}'

    
    spot_that_time=bars5[bars5['timestamp'] == time_str][type].values[0] 
    spot_down_side=spot_that_time-(spot_that_time*percentage)
    spot_up_side=spot_that_time+(spot_that_time*percentage)
    bars5['longoptionsdownSide']=spot_down_side
    bars5['longoptionsupSide']=spot_up_side


    bars5.drop(columns=['v', 'oi'], errors='ignore', inplace=True)
    # 1️⃣ remove tz and add the offset
    bars5['timestamp'] = (
        bars5['timestamp']
        .dt.tz_localize(None)
        + pd.Timedelta(hours=5, minutes=30)
    )

    # 2️⃣ now format that Series
    bars5['timestamp'] = bars5['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return {'Data':bars5.to_dict(orient="records"),'table':None , "verticalLineTime":verticalLineTime,"title":long_options_settings['system']}


def make_broker_position_mismatch_new_data():
        data, nonimp = give_pos_mismatch()

        # Collect all unique symbols
        symbols = set()
        for key, trades in data.items():
            for trade in trades:
                symbols.add(trade['Symbol'])
        
        # Build a mapping: each symbol maps to a dictionary of key: quantity, initialized to 0
        mapping = {}
        for sym in symbols:
            mapping[sym] = {key: 0 for key in data.keys()}
            for key, trades in data.items():
                for trade in trades:
                    if trade['Symbol'] == sym:
                        mapping[sym][key] = trade['Quantity']

        # Create a DataFrame using the mapping. The order of columns is 'Symbol' followed by the account keys.
        keys = ['Symbol'] + list(data.keys())
        df = pd.DataFrame(
            [{'Symbol': sym, **values} for sym, values in mapping.items()],
            columns=keys
        )

        # Debug: print the shape of the DataFrame
        print("DataFrame shape:", df.shape)
        
        # If df is empty, force it to only have the 'Symbol' column.
        if df.empty:
            print("DataFrame is empty!")
            df = pd.DataFrame(columns=['Symbol'])

        # Convert the DataFrame into a dictionary suitable for JSON response
        df_data = df.to_dict('records')
            
        return {
            "message": "Margin updated for all accounts successfully",
            "dataframe": {
                "data": df_data,
                "columns": df.columns.tolist()
            }
        }