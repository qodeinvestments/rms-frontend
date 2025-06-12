


import os
import direct_redis
import time
import datetime
import helperFunctions

from pathlib import Path
import pandas as pd
import re
# Initialize the Redis connection
r = direct_redis.DirectRedis()

# Function to get the current timestamp

# def empty_key():
#     heartbeat = r.get('rms_heartbeat')
#     heartbeat['my_program']=r.get('my_program_status')
        
#     for key, value in heartbeat.items():
#         # Convert the string 'True'/'False' to boolean
#         if key.startswith('pulse_web_socket'):
#             shutdown_key = "websocket"
#         if key.startswith('pulse_trader_xts:'):
#             shutdown_key = "trader_xts_shut_down"
#         if key.startswith('pulse_trader_zerodha:'):
#             shutdown_key = "trader_zerodha_shut_down"
#         # Update the shutdown times hashmap
#         else :
#             shutdown_key = f'shut_down_{key}'
        
        
#         r.ltrim(shutdown_key, 1, 0)



def save_var():

    # 1) Define your output folder relative to cwd
    base_dir = Path.cwd()                        # e.g. /root/algo/dashboard
    out_dir  = base_dir / "varfiles"
    out_dir.mkdir(exist_ok=True)

    # 2) Date prefix
    today = datetime.date.today().isoformat()    # '2025-05-02'

    # 3) Loop periods and save
    for period in (10, 20):
        data, _ = helperFunctions.get_uservarcalculations(period)
        df = pd.DataFrame(data)

        fname    = f"{today}_{period}_var.xlsx"
        file_path = out_dir / fname

        # Using ExcelWriter to be explicit about engine
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        print(f"✔️  Saved {file_path}")

    # 4) List what’s in varfiles/
    print("\nContents of varfiles/:")
    for p in sorted(out_dir.iterdir()):
        print(" ", p.name)



def extract_expiration(option_code):
    match = re.search(r'[A-Za-z]+(\d{6})', option_code)
    if not match:
        return None
    date_str = match.group(1)  # e.g. "250313" -> year=25, month=03, day=13
    expiration_date = datetime.datetime.strptime(date_str, '%y%m%d').date()
    today = datetime.datetime.today().date()
    return expiration_date > today

def give_unique_map(arr):

    sym_map = {}
    for item in arr:
        # Only aggregate if not expired
        # if extract_expiration(item['Symbol']) is True:
        sym_map[item['Symbol']] = int(sym_map.get(item['Symbol'], 0)) + int(item['Quantity'])
    
    # Convert to a list of dicts
    return [
        {'Symbol': symbol, 'Quantity': qty}
        for symbol, qty in sym_map.items()
        if qty != 0
    ]

# def get_open_trades(client):
#     # Hypothetical: trades_list is a list of dicts from Redis
#     trades_list = r.lrange('open_trades')  # or however you retrieve it
#     open_trade = pd.DataFrame(trades_list)
#     open_trade = open_trade.sort_values(by='timestamp', ascending=False)
#     open_trade = open_trade.fillna('').infer_objects()

#     client_map = {}
#     for _, row in open_trade.iterrows():
#         # Suppose row["quantity"] is a dict like {"client1": 50, "client2": 20}
#         for client_key, value in row["quantity"].items():
#             client_map.setdefault(client_key, []).append({"Symbol": row['symbol'], "Quantity": value})

#     return client_map.get(client, [])

def get_open_trades(client_id,client,manual_orders):
    # Hypothetical: trades_list is a list of dicts from Redis
    trades_list = r.lrange('open_trades')  # or however you retrieve it
    open_trade = pd.DataFrame(trades_list)
    open_trade = open_trade.sort_values(by='timestamp', ascending=False)
    open_trade = open_trade.fillna('').infer_objects()

    client_map = {}
    for _, row in open_trade.iterrows():
        # Suppose row["quantity"] is a dict like {"client1": 50, "client2": 20}
        for client_key, value in row["quantity"].items():
            client_map.setdefault(client_key, []).append({"Symbol": row['symbol'], "Quantity": value})
    
    if client_id not in client_map:
        client_map[client_id]=[]
    if client in manual_orders :        
        for index, row in manual_orders.iterrows():
            client_map[client_id].append({'Symbol':row['Symbol'], 'Quantity': row[client]})

    return client_map.get(client_id, [])

# def get_rms_prev_day(client):
#     result = []
#     trades = r.hget('live_user_rms_prev_day', client)
#     if not trades:
#         return result

#     for trade in trades:
#         sym = trade.get('symbol', trade.get('tradingsymbol'))
#         # helperFunctions.zerodhasymbolTOsymbol might map "NIFTY" -> "NIFTY F/O", etc.
#         symbol_clean = helperFunctions.zerodhasymbolTOsymbol.get(sym, sym)
#         qty_raw = trade.get('filled_quantity', trade.get('CumulativeQuantity'))
#         is_sell = trade.get('transaction_type', trade.get('OrderSide')) == 'SELL'
#         qty = -qty_raw if is_sell else qty_raw
#         result.append({'Symbol': symbol_clean, 'Quantity': qty})
#     return result

def get_rms_prev_day(client,manual_orders):
    result = []
    trades = r.hget('live_user_rms_prev_day', client)
    if not trades:
        if client in manual_orders:
            for index, row in manual_orders.iterrows():
                result.append({'Symbol':row['Symbol'], 'Quantity': row[client]})
        
        return result

    for trade in trades:
        sym = trade.get('symbol', trade.get('tradingsymbol'))
        # helperFunctions.zerodhasymbolTOsymbol might map "NIFTY" -> "NIFTY F/O", etc.
        symbol_clean = helperFunctions.zerodhasymbolTOsymbol.get(sym, sym)
        qty_raw = trade.get('filled_quantity', trade.get('CumulativeQuantity'))
        is_sell = trade.get('transaction_type', trade.get('OrderSide')) == 'SELL'
        qty = -qty_raw if is_sell else qty_raw
        result.append({'Symbol': symbol_clean, 'Quantity': qty})
    
    if client in manual_orders:
        for index, row in manual_orders.iterrows():
         result.append({'Symbol':row['Symbol'], 'Quantity': row[client]})
    return result


def get_client_rms_df(client):
    # result = []
    # positions = r.hget('live_client_rms_df', client)
    # if positions:
    #     for row in positions:
    #         if row['net_qty'] != 0:
    #             result.append({"Symbol": row['symbol'], "Quantity": row['net_qty']})
    # return result
    result=[]
    val=r.hget('client_positions',client)
    if val==None:
        return result
    for obj in val:
        if 'TradingSymbol' in obj :
            num=int(obj['ExchangeInstrumentId'])
            if obj['Quantity']!=0 :
                result.append({"Symbol": helperFunctions.exchangeToSymbol[num] if num in helperFunctions.exchangeToSymbol else num , "Quantity": obj['Quantity']})
        else :
            if obj['quantity']!=0 :
                result.append({"Symbol": helperFunctions.zerodhasymbolTOsymbol[obj['tradingsymbol']] if obj['tradingsymbol'] in helperFunctions.zerodhasymbolTOsymbol else obj['tradingsymbol'] , "Quantity": obj['quantity']})
    return result

def merge_and_get_mismatch(df_left, df_right, join_cols):
    if df_left.empty or df_right.empty:
        return df_left.copy(), df_right.copy()

    merged = pd.merge(df_left, df_right, on=join_cols, how="inner")

    def _not_in_merged(orig_df):
        subset = merged[join_cols].drop_duplicates()
        indicator_df = orig_df.merge(subset, on=join_cols, how="left", indicator=True)
        return indicator_df.query('_merge == "left_only"').drop(columns=['_merge'])

    left_not_in_right = _not_in_merged(df_left)
    right_not_in_left = _not_in_merged(df_right)
    return left_not_in_right, right_not_in_left


def eod_checks():
    columns = ["Symbol", "Quantity"]
    excel_filename = "all_clients_mismatches.xlsx"
    sheet_created = False  # Flag to check if at least one sheet is added
    manual_orders=r.get('broker_position_mismatch')
    # List to accumulate messages
    summary_messages = []

    with pd.ExcelWriter(excel_filename) as writer:
        for client in helperFunctions.clients:
            if not helperFunctions.active_clients[client]:
                continue

            # 1) Build DataFrames for EOD (a), Positions (b), OpenTrades (c)
            a = pd.DataFrame(give_unique_map(get_rms_prev_day(client,manual_orders)))
            b = pd.DataFrame(give_unique_map(get_client_rms_df(client)))
            c = pd.DataFrame(give_unique_map(get_open_trades(helperFunctions.clients[client]['user_id'],client,manual_orders)))

            # 2) Compare mismatches between dataframes
            a_not_in_b, b_not_in_a = merge_and_get_mismatch(a, b, columns)
            b_not_in_c, c_not_in_b = merge_and_get_mismatch(b, c, columns)

            # 3) Build mismatch DataFrame(s) by combining comparisons
            mismatch_parts = []

            # EOD <-> Positions
            if not (a_not_in_b.empty and b_not_in_a.empty):
                mismatch_parts.append(a_not_in_b.assign(Comparison="EOD vs Positions", Source="EOD"))
                mismatch_parts.append(b_not_in_a.assign(Comparison="EOD vs Positions", Source="Positions"))

            # Positions <-> OpenTrades
            if not (b_not_in_c.empty and c_not_in_b.empty):
                mismatch_parts.append(b_not_in_c.assign(Comparison="Positions vs OpenTrades", Source="Positions"))
                mismatch_parts.append(c_not_in_b.assign(Comparison="Positions vs OpenTrades", Source="OpenTrades"))

            # Combine all mismatch parts
            if mismatch_parts:
                all_mismatches = pd.concat(mismatch_parts, ignore_index=True)
            else:
                all_mismatches = pd.DataFrame()

            # 4) Write sheet: if no mismatches, write an empty sheet (or a message)
            if all_mismatches.empty:
                msg = f"No mismatches for client '{client}'"
                summary_messages.append(msg)
                # Write an empty DataFrame to create the sheet
                pd.DataFrame().to_excel(writer, sheet_name=str(client), index=False)
            else:
                msg = f"Found mismatches for client '{client}':"
                summary_messages.append(msg)
                all_mismatches.to_excel(writer, sheet_name=str(client), index=False)
            sheet_created = True

        # If no sheet was created for any client, add a default empty sheet
        if not sheet_created:
            pd.DataFrame().to_excel(writer, sheet_name="NoMismatches", index=False)

    # Sort the summary messages in ascending order
    summary_messages.sort()
    
    # Build the complete summary message
    complete_message = "\n".join(summary_messages)
    helperFunctions.send_telegram_alert(complete_message)
    print(f"\nAll done! Mismatches (if any) are in {excel_filename}.\n")
    save_var()
    return 

def check_ob():
    active_clients = r.hgetall('clients_live_today')
    lines = []
    for client, is_live in active_clients.items():
        if not is_live:
            continue
        val = int(r.hget('system_ob_cnt', client) or 0)
        if val > 0:
            lines.append(f"{client} ob cnt is not zero: {val}")
    if lines:
        lines.sort()
        header = "The Ob Count Status is Not Zero For:"
        message = "\n".join([header, *lines])
    else:
        message = "All Accounts Ob are Zero."
    print(message)
    helperFunctions.send_telegram_alert(message)


def get_time():
    return datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')
# Main function to monitor and update the shutdown times


def checkIfIndexDataIsUpdating(time):
    changedTime=time.replace(second=0, microsecond=0)
    indexList=['NIFTYSPOT','BANKNIFTYSPOT']
    for index in indexList:
        spotPrice=None
        
        spotPrice=r.hget(f'l.tick_{changedTime}',index)
        if spotPrice==None:
            helperFunctions.send_telegram_alert(f'Error in Fetching {index} Data At Time : {time} : {changedTime}')
        
    
def monitor_heartbeat():
    last_status = {}

    while True:
        # Retrieve the current heartbeat value

              # Check trading hours
        current_time = datetime.datetime.now().time().replace(microsecond=0)

        
        if current_time in [datetime.time(15,35,00)]:
            df=helperFunctions.make_broker_position_mismatch_new_data()
         
            r.set('broker_position_mismatch',pd.DataFrame(df['dataframe']['data']))
            helperFunctions.send_telegram_alert("The Broker Position Mismatch Csv Updated SuccessFully") 
        
        if current_time in [datetime.time(16, 00,00)]:
            eod_checks()

        if current_time in [datetime.time(8, 45,00),datetime.time(15, 35,00)]:
            check_ob()
           
        
        if current_time in [datetime.time(8, 46,00),datetime.time(15, 47,00)]:
            checkSqaureOffKeys()
            
        if current_time.minute % 5 == 0 and current_time.second==59:         
            if datetime.time(9, 15) <= current_time <= datetime.time(15, 30):
                checkIfIndexDataIsUpdating(datetime.datetime.now())

        

        



        heartbeat = r.get('rms_heartbeat')
        heartbeat['my_program']=r.get('my_program_status')
        
        
        for key, value in heartbeat.items():
            # Convert the string 'True'/'False' to boolean
            current_status = value
            # If this key was previously stored, compare with the current status
            if key in last_status:
                # Check if the status has changed from True to False
                if last_status[key]==True and current_status==False :
                
                    if key.startswith('pulse_web_socket'):
                        shutdown_key = "websocket_shut_down"
                    elif key.startswith('pulse_trader_xts:'):
                        shutdown_key = "trader_xts_shut_down"
                    elif key.startswith('pulse_trader_zerodha:'):
                        shutdown_key = "trader_zerodha_shut_down"
                    # Update the shutdown times hashmap
                    else :
                        shutdown_key = f'shut_down_{key}'
                    
                    print(shutdown_key," ",get_time())
                    shutdown_entry = {"time":  get_time(), "message": "Service shutdown detected in " + key}
                    # Add the shutdown entry to the list
                    r.rpush(shutdown_key, shutdown_entry)
            # Update the last known status
            last_status[key] = current_status
        
        # Sleep for a short period before checking again
        time.sleep(1)


def checkSqaureOffKeys():
    squareOffFlagError = []
    squareOffModeError = []

    # Step 1: Check for individual client errors
    for client, details in helperFunctions.clients.items():
        if helperFunctions.active_clients[client]:
            squareOffFlag = r.hget('sq_off_flag', client)
            squareOffMode = r.hget('sq_off_mode', client)

            if squareOffFlag == 1:
                squareOffFlagError.append(f'{client}')

            if squareOffMode == True:
                squareOffModeError.append(f'{client}')

    # Step 2: Compose error messages
    squareOffFlagErrors = []
    squareOffModeErrors = []

    if len(squareOffFlagError) > 0:
        squareOffFlagErrors.append("⚠️ Squared Off Flag of Some Users is 1:")
        squareOffFlagErrors.extend(squareOffFlagError)
    else:
        squareOffFlagErrors.append("✅ Squared Off Flag: All Users Are Correct.")

    if len(squareOffModeError) > 0:
        squareOffModeErrors.append("⚠️ Squared Off Mode of Some Users is True:")
        squareOffModeErrors.extend(squareOffModeError)
    else:
        squareOffModeErrors.append("✅ Squared Off Mode: All Users Are Correct.")

    # Step 3: Final output messages
    main_message = "\n".join(squareOffFlagErrors)
    client_multiplier_message = "\n".join(squareOffModeErrors)

    helperFunctions.send_telegram_alert(main_message)
    helperFunctions.send_telegram_alert(client_multiplier_message)
    return



if __name__ == '__main__':
    monitor_heartbeat()





# #shutdowns = r.lrange('my_program_shut_down', 0, -1)
# #shutdowns