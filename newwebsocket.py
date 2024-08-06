from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import glob
import numpy as np
import direct_redis
import pandas as pd
import datetime
import pytz
import logging

app = FastAPI()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


r = direct_redis.DirectRedis()

clients = r.hgetall('live_clients')

def get_time():
    return datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')
def get_index_ltp():
    ltp_dict = {}
    for i in ['NIFTYSPOT', 'BANKNIFTYSPOT', 'FINNIFTYSPOT', 'MIDCPNIFTYSPOT', 'SENSEXSPOT']:
        ltp = r.get(f'ltp.{i}')
        if ltp is not None:
            ltp_dict[i] = ltp
    return ltp_dict
def get_client_margin(client):
    margin = r.hget('curr_client_margin', client)
    return round(float(margin)) if margin is not None else 0
def get_client_var(client):
    var = r.hget('curr_client_var', client)
    return abs(float(var)) if var is not None else 0
def get_client_rms_df(client):
    return r.hget('live_client_rms_df', client)

def get_client_pos(client, exchangeTOsymbol):
    pos = r.hget('live_user_positions', client)
    return {exchangeTOsymbol.get(k,0):v for k, v in pos.items()}

def get_net_qty(client):
    pos = r.hget('live_user_positions', client)
    return sum([x for x in pos.values()])

def get_open_qty(client):
    pos = r.hget('live_user_positions', client)
    return sum([abs(x) for x in pos.values()])

def get_idealMTM(client):
    return float(r.hgetall('curr_client_ideal_mtm')[client])

def get_actual_client_MTM(client):
    mtm_list = r.hgetall(f'live_client_mtm.{client}')
    if len(mtm_list) == 0:
        return 0
    last_key, last_value = list(mtm_list.items())[-1]
    return float(last_value)

def getRejectedOrders(client):
    rejected_orders = r.hget('rejected_orders', client)
    return int(rejected_orders) if rejected_orders is not None else 0

def getPendingOrders(client):
    pending_orders = r.hget('pending_orders', client)
    return int(pending_orders) if pending_orders is not None else 0

def change_chart_data_to_epoch(chart_data):
    df = pd.DataFrame(list(chart_data.items()), columns=['datetime', 'value'])
    df['datetime'] = pd.to_datetime(df['datetime'], format="%Y-%m-%d %H:%M:%S", utc=True)
    df['value'] = df['value'].astype(float)
    df['time'] = df['datetime'].astype(int) // 10**9
    arr = df[['time', 'value']].to_dict(orient='records')
    return arr



def change_chart_data(client):
    ltp_dict = r.hgetall(f'live_client_mtm.{client}')
    ltp_dict = pd.Series(ltp_dict)
    ltp_dict = ltp_dict[ltp_dict != 0]
    ltp_dict = ltp_dict.sort_index()
    arr=change_chart_data_to_epoch(ltp_dict)
    # arr = []
    # for key, value in ltp_dict.items():
    #     dt_obj = datetime.datetime.strptime(key, "%Y-%m-%d %H:%M:%S")
    #     utc = pytz.UTC
    #     dt_obj_utc = datetime.datetime.strptime(str(dt_obj), "%Y-%m-%d %H:%M:%S")
    #     dt_obj_utc = utc.localize(dt_obj_utc)
    #     epoch_time = int(dt_obj_utc.timestamp())
    #     arr.append({"time": epoch_time, "value": float(value)})
    return {"client": arr}

def get_basketData(live_weights):
    strategy_arr = {}
    for strat in live_weights.keys():
        ltp_dict = r.hgetall(f'live_mtm.{strat}')
        ltp_dict = pd.Series(ltp_dict)
        ltp_dict = ltp_dict[ltp_dict != 0]
        ltp_dict = ltp_dict.sort_index()
        arr=change_chart_data_to_epoch(ltp_dict)
        # arr = []
        # for key, value in ltp_dict.items():
        #     dt_obj = datetime.datetime.strptime(key, "%Y-%m-%d %H:%M:%S")
        #     utc = pytz.UTC
        #     dt_obj_utc = datetime.datetime.strptime(str(dt_obj), "%Y-%m-%d %H:%M:%S")
        #     dt_obj_utc = utc.localize(dt_obj_utc)
        #     epoch_time = int(dt_obj_utc.timestamp())
        #     arr.append({"time": epoch_time, "value": float(value)})
        strategy_arr[strat] = arr
    return strategy_arr

def read_pulse_updates():
    return r.get('rms_heartbeat')

def read_position_mismatch():
    data= r.hgetall('net_positions_verification')
    print("data is :",data)
    return data.to_dict()

def get_client_live_trade_book(client):
    exchangeTOsymbol = r.get('exchangeTOsymbol')
    tb = r.hget('live_user_tb', client)
    if len(tb) > 0:
        tb = pd.DataFrame(tb)
        tb = tb[tb.OrderStatus == 'Filled']
        tb['ExchangeInstrumentID'] = tb['ExchangeInstrumentID'].apply(lambda x: exchangeTOsymbol.get(x, None))
        temp_tb = tb[['OrderGeneratedDateTime', 'ExchangeTransactTime', 'ExchangeInstrumentID', 'OrderAverageTradedPrice', 'OrderSide', 'OrderQuantity']]
        return temp_tb.to_dict('records')
    return []

def get_client_combined_df(client):
    exchangeTOsymbol = r.get('exchangeTOsymbol')
    tb = r.hgetall('Ob_SG_combined')[client]
    if len(tb) > 0:
        tb = pd.DataFrame(tb)
        tb = tb.fillna('')
        tb['ExchangeInstrumentID'] = tb['ExchangeInstrumentID'].apply(lambda x: exchangeTOsymbol.get(x, None))
        timestamp_columns = tb.select_dtypes(include=['datetime64[ns]']).columns

        # Convert each timestamp column to string
        for column in timestamp_columns:
         tb[column] = tb[column].astype(str)   

        
        temp_tb = tb[[
                "uid", "timestamp", "system_tag","action", 
                "qty", "symbol", "price", "value", "system_timestamp",
                "note", "basket", "effective_qty", "AppOrderID",  
                "ExchangeSegment","ExchangeInstrumentID", "OrderType", "ProductType",
                "OrderPrice", "OrderQuantity",
                "OrderStatus", "OrderAverageTradedPrice",
                "OrderGeneratedDateTime", "ExchangeTransactTime", "TradingSymbol",
                "OrderUniqueIdentifier","system_tags"
                ]]

        return temp_tb.to_dict('records')
    return []
    


def get_client_live_order_book(client):
    exchangeTOsymbol = r.get('exchangeTOsymbol')
    tb = r.hget('live_user_ob', client)
    if len(tb) > 0:
        tb = pd.DataFrame(tb)
        tb['ExchangeInstrumentID'] = tb['ExchangeInstrumentID'].apply(lambda x: exchangeTOsymbol.get(x, None))
        temp_tb = tb[['OrderGeneratedDateTime', 'ExchangeTransactTime', 'ExchangeInstrumentID', 'OrderAverageTradedPrice', 'OrderSide', 'LeavesQuantity', 'OrderQuantity', 'OrderStatus', 'CancelRejectReason']]
        return temp_tb.to_dict('records')
    return []

def get_last_value_for_strategy_mtm_chart_data(str):
    data = r.hgetall('live.mtm_' + str)
    df = pd.DataFrame(list(data.items()), columns=['Timestamp', 'Value'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)
    df.sort_values(by='Timestamp', inplace=True)
    today = datetime.datetime.now().date()
    df_today = df[df.index.date == today]
    if not df_today.empty:
        last_timestamp = df_today.index[-1].strftime('%Y-%m-%d %H:%M:%S')
        last_value = float(df_today['Value'].iloc[-1])
        return {last_timestamp: last_value}
    return {}

def get_strategy_mtm_chart_data(strategy_uids):
    strategy_arr = {}
    for strat in strategy_uids:
        chart_data=r.hgetall(f'live.mtm_{strat}')
        arr=change_chart_data_to_epoch(chart_data)
        # arr = []
        # df = pd.DataFrame(list(chart_data.items()), columns=['datetime', 'value'])
        # df['datetime'] = pd.to_datetime(df['datetime'], format="%Y-%m-%d %H:%M:%S", utc=True)
        # df['value'] = df['value'].astype(float)
        # df['epoch_time'] = df['datetime'].astype(int) // 10**9
        # arr = df[['epoch_time', 'value']].to_dict(orient='records')
        strategy_arr[strat] = arr 
    return strategy_arr


async def send_initial_data(websocket:WebSocket):
    live_weights = r.hgetall('live_weights')
    obj = {basket: list(val.keys()) for basket, val in live_weights.items()}
    initial_data = {
        "live_weights": obj,
        "time": get_time(),
        # Add any other initial data you want to send
    }
    await websocket.send_text(json.dumps(initial_data))

async def send_data(websocket: WebSocket):
    while True:
        
        start_global_time = get_time()
        s_g_t=time.time()
        exchangeTOsymbol = r.get('exchangeTOsymbol')
        
        clients_obj = [
            {
                'name': client,
                'ideal_MTM': round(get_idealMTM(client), 2),
                'MTM': round(get_actual_client_MTM(client), 2),
                "MTMTable": change_chart_data(client),
                'ideal_MTMTable': r.hgetall(f'live_client_ideal_mtm.{client}'),
                'Rejected_orders': getRejectedOrders(client),
                'Pending_orders': getPendingOrders(client),
                'OpenQuantity': get_open_qty(client),
                "NetQuantity": get_net_qty(client),
                "Live_Trade_Book": get_client_live_trade_book(client),
                "Live_Order_Book": get_client_live_order_book(client),
                "Live_Client_Positions": get_client_pos(client, exchangeTOsymbol),
                "Live_Client_RMS_df": get_client_rms_df(client),
                "Live_Client_Margin": get_client_margin(client),
                "Live_Client_Var": get_client_var(client),
                "Combined_df": get_client_combined_df(client)
            }
            for client in clients if client == 'PAPER TRADING 2'
        ]
        
        #live_weights = r.hgetall('live_weights')
        #strategy_mtm_chart_data = get_strategy_mtm_chart_data(live_weights)
        # Basket_data = get_basketData(live_weights)
        
        data = {
            "client_data": clients_obj,
            #"basket_data": Basket_data,
            "connection_data": {
                'time': get_time(),
                "live_index": get_index_ltp(),
                'pulse': read_pulse_updates(),
                'position_mismatch': read_position_mismatch()
            },
            "time": start_global_time,
            #"strategy_mtm_chart_data": strategy_mtm_chart_data
        }
        await websocket.send_text(json.dumps(data))
        end_time = time.time()
        print(f"client and connection: {end_time - s_g_t}") 
        await asyncio.sleep(0.1)

@app.get("/")
async def root():
    return {"message": "Welcome to Swan Capital API"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await send_initial_data(websocket)
        await send_data(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()




async def send_basket_chart_data(websocket: WebSocket):
    while True:
        s_g_t=time.time()
        live_weights = r.hgetall('live_weights')
        Basket_data = get_basketData(live_weights)
        data = {
            "basket_data": Basket_data,
            "time": get_time()
        }
        await websocket.send_text(json.dumps(data))
        end_time = time.time()
        print(f"basket: {end_time - s_g_t}") 
        await asyncio.sleep(0.1)


@app.websocket("/chart/basket")
async def basket_chart_websocket_endpoint(websocket: WebSocket):
    logger.info(f"Received WebSocket connection request from {websocket.client}")
    try:
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        await send_basket_chart_data(websocket)
    except Exception as e:
        logger.error(f"Basket Chart WebSocket error: {e}", exc_info=True)
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed")


async def send_strategy_chart_data(websocket: WebSocket):
    strategy_uids = []
    while True:
        s_g_t=time.time()
        try:
            # Check for any new messages (non-blocking)
            data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            received_uids = json.loads(data).get('strategy_uids', [])
            if received_uids:
                strategy_uids = received_uids
                
        except asyncio.TimeoutError:
            # No new message, continue with current strategy_uids
            pass
        except Exception as e:
            print(f"Error receiving message: {e}")

        strategy_mtm_chart_data = get_strategy_mtm_chart_data(strategy_uids)
        
        data = {
            "strategy_mtm_chart_data": strategy_mtm_chart_data,
            "time": get_time()
        }
        end_time = time.time()
        print(f"strategy: {end_time - s_g_t}") 
        await websocket.send_text(json.dumps(data))
        await asyncio.sleep(0.1)

@app.websocket("/chart/strategy")
async def strategy_chart_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await send_strategy_chart_data(websocket)
    except Exception as e:
        logger.error(f"Strategy Chart WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")