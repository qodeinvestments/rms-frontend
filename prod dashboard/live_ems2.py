import datetime
import direct_redis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('dark_background')



r = direct_redis.DirectRedis(host='localhost', port=6379, db=0)


lot_size_dict = {
  'BANKNIFTY': 15,
  'NIFTY': 75,
  'FINNIFTY': 25,
  'MIDCPNIFTY': 50,
  'SENSEX': 20
}

lot_size_dict_next = {
  'BANKNIFTY': 15,
  'NIFTY': 75,
  'FINNIFTY': 25,
  'MIDCPNIFTY': 50,
  'SENSEX': 20
}

freeze_qty_dict = {
  'BANKNIFTY': 900,
  'NIFTY': 1800,
  'FINNIFTY': 1800,
  'MIDCPNIFTY': 2800,
  'SENSEX': 1000
}

strike_diff_dict = {
  'BANKNIFTY': 100 ,
  'NIFTY': 50,
  'FINNIFTY': 50,
  'MIDCPNIFTY': 25,
  'SENSEX': 100
}

#########################

class DataInterface:

    def __init__(self):
        pass
    
    def get_lot_size(self, underlying):
        #lot_size = r.hget('lot_size', underlying)
        if underlying in lot_size_dict:
            return lot_size_dict[underlying]
        else:
            raise ValueError(f'Unrecognized Underlying: {underlying}')
        
    def get_next_lot_size(self, underlying):
        #lot_size = r.hget('lot_size', underlying)
        if underlying in lot_size_dict_next:
            return lot_size_dict_next[underlying]
        else:
            raise ValueError(f'Unrecognized Underlying: {underlying}')
        
    def get_freeze_quantity(self, underlying):
        #freeze_quantity = r.hget('freeze_quantity', underlying)
        if underlying in freeze_qty_dict:
            return freeze_qty_dict[underlying]
        else:
            raise ValueError(f'Unrecognized Underlying: {underlying}')

    def get_strike_diff(self, underlying):
        if underlying in strike_diff_dict:
            return strike_diff_dict[underlying]
        else:
            raise ValueError(f'Unrecognized Underlying: {underlying}')
        
    
    def get_expiry_code(self, timestamp, underlying, expiry_idx):
        list_of_expiries = r.hget('list_of_expiries', underlying)
        list_of_expiries.sort()
        list_of_expiries = np.array(list_of_expiries)
        expiry_date = list_of_expiries[list_of_expiries >= timestamp.date()][expiry_idx]
        expiry_code = str(expiry_date).replace('-', '')[2:]
        return expiry_code

    def find_symbol_by_moneyness(self, timestamp, underlying, expiry_idx, opt_type, otm_count):
        # print(otm_count)
        assert otm_count >= -5 # don't go too ITM
        assert otm_count <= 15 # don't go too OTM
        # ...
        expiry_code = self.get_expiry_code(timestamp, underlying, expiry_idx)
        # print('EXP CODE',expiry_code, underlying)
        # ...
        #data = self.get_all_ticks_by_timestamp(timestamp)#r.hget('tick', str(timestamp))
        #spot_price = float(data.loc[f"{underlying}SPOT"]['c'])
        # print(timestamp, underlying, f"{underlying}SPOT")
        spot_price = float(self.get_tick(timestamp,f"{underlying}SPOT")['c'])#float(data.loc[f"{underlying}SPOT"]['c'])
        # print('SPOT PRICE ',spot_price, underlying, timestamp)
        #print('FUT:',fut_price)
        strike_diff = strike_diff_dict[underlying]
        # ...
        if opt_type == 'CE':
            shifter = 1
        else:
            shifter = -1
        # ...
        # print(spot_price, type(spot_price), strike_diff, type(strike_diff), underlying)
        atm_strike = round(spot_price/strike_diff)*strike_diff
        #print('ATM:',atm_strike)
        selected_strike = int(atm_strike + otm_count*shifter*strike_diff)
        #print('SELECTED:',selected_strike)
        # ...
        symbol = f"{underlying}{expiry_code}{selected_strike}{opt_type}"
        return symbol

    def find_symbol_by_dte(self, timestamp, underlying, expiry_idx, opt_type, selector_val, dte_factor,seek_type='lt'):

        atm_ce = self.find_symbol_by_moneyness(timestamp, underlying, expiry_idx, 'CE', 0)
        atm_pe = self.find_symbol_by_moneyness(timestamp, underlying, expiry_idx, 'PE', 0)
        dte = self.get_dte(timestamp, atm_ce)
        atm_ce_price = self.get_tick(timestamp, atm_ce)['c']
        atm_pe_price = self.get_tick(timestamp, atm_pe)['c']
        atm_cp = (atm_ce_price + atm_pe_price)/2
        premium_for_day = (atm_cp/(1+(dte_factor*dte)))*selector_val
        
        return self.find_symbol_by_premium(timestamp, underlying, expiry_idx, opt_type, premium_for_day, seek_type)
        
    
    def find_symbol_by_premium(self, timestamp, underlying, expiry_idx, opt_type, seek_price, seek_type=None, premium_rms_thresh=1, moneyness_rms_thresh=-5, oi_thresh=1000, perform_rms_checks=True, force_atm=True) :
        # ...
        data = self.get_all_ticks_by_timestamp(timestamp)#r.hget('tick', str(timestamp))
        # print('DATA ,', data)
        spot_price = float(self.get_tick(timestamp,f"{underlying}SPOT")['c'])#float(data.loc[f"{underlying}SPOT"]['c'])
        strike_diff = strike_diff_dict[underlying]
        # ...
        if opt_type == 'CE':
            shifter = 1
        else:
            shifter = -1
        # ...
        atm_strike = round(spot_price/strike_diff)*strike_diff
        data = data.reset_index()
        # ...
        expiry_code = self.get_expiry_code(timestamp, underlying, expiry_idx)
        # print(expiry_code, strike_diff, atm_strike, spot_price, underlying, opt_type, seek_price)
        # print(data)
        # ...
        # print(expiry_code, underlying, opt_type)
        
        subset = data[data['index'].apply(lambda x: x.startswith(underlying) and expiry_code in x and x.endswith(opt_type))].copy()
        # print('SUBSET ,',subset)
        # ONLY KEEP > 0 PRICES
        if seek_type == None:
            subset = subset[subset['c']>0]
        elif seek_type == 'gt':
            subset = subset[subset['c']>seek_price]
        elif seek_type == 'lt':
            subset = subset[subset['c']<seek_price]
        if len(subset) > 0:
            idx = (subset['c'].apply(float)-seek_price).abs().sort_values().index[0]
            symbol = subset.loc[idx]['index']
        else:
            symbol = None
        # RMS CHECKS
        if perform_rms_checks:
            if symbol is not None and seek_price > 5:
                temp_symbol = symbol
                tick = self.get_tick(timestamp, symbol)
                prem = tick['c']
                oi = tick['oi']
                curr_strike = int(symbol.replace(underlying, '').replace(expiry_code, '').replace(opt_type, ''))
                moneyness = shifter*(curr_strike-atm_strike)/strike_diff
                if prem > seek_price*(1+premium_rms_thresh) or oi < oi_thresh*self.get_lot_size(underlying) or moneyness < moneyness_rms_thresh:
                    print(seek_price, prem, oi, atm_strike, curr_strike, moneyness, strike_diff)
                    print(f'set {symbol} as None')
                    # time.sleep(1)
                    symbol = None
                if force_atm:
                    if moneyness <= -1:
                        symbol = self.find_symbol_by_moneyness(timestamp, underlying, expiry_idx, opt_type, 0)
                if symbol is None and oi < oi_thresh*self.get_lot_size(underlying):
                    symbol = self.shift_strike_in_symbol(temp_symbol, 1)
                    tick = self.get_tick(timestamp, symbol)
                    prem = tick['c']
                    oi = tick['oi']
                    if prem > seek_price*(1+premium_rms_thresh) or oi < oi_thresh*self.get_lot_size(underlying):
                        symbol = None
        return symbol
    
    # ...
    def get_all_ticks_by_timestamp(self, timestamp):
        #print(f'getting all ticks @ {timestamp}')
        list_of_ticks = r.hgetall('l.tick_'+str(timestamp))
        ticks = pd.DataFrame(list_of_ticks).transpose()
        return ticks


    def get_all_ticks_by_symbol(self, symbol):
        ticks = r.hgetall(f'l.{str(symbol)}')
        if ticks is not None and len(ticks) > 0:
            ticks = pd.DataFrame(ticks).T.sort_index().reset_index().rename(columns={'index':'timestamp'})
            ticks = ticks.drop_duplicates()
            ticks['timestamp'] = pd.to_datetime(ticks['timestamp'])
        return ticks
    #         ticks = ticks.sort_values('timestamp').reset_index(drop=True)
    #     return ticks.drop(columns=['atp', 'system_timestamp'])

    def get_all_ticks_by_symbol(self, symbol):
        ticks = r.hgetall(f'l.{str(symbol)}')
        if ticks is not None and len(ticks) > 0:
            ticks = pd.DataFrame(ticks).T.sort_index().reset_index().rename(columns={'index':'timestamp'})
            ticks = ticks.drop_duplicates()
            ticks['timestamp'] = pd.to_datetime(ticks['timestamp'])
        return ticks

    def get_ticks_of_symbol_between_timestamps(self, symbol, from_timestamp=None, to_timestamp=None):
        if type(from_timestamp) is str:
            from_timestamp = pd.to_datetime(from_timestamp)
        if type(to_timestamp) is str:
            to_timestamp = pd.to_datetime(to_timestamp)
        ticks = self.get_all_ticks_by_symbol(symbol)
        if from_timestamp is not None:
            ticks = ticks[ticks['timestamp'] >= from_timestamp].copy()
        if to_timestamp is not None:
            ticks = ticks[ticks['timestamp'] <= to_timestamp].copy()
        return ticks

    def get_tick(self, timestamp, symbol):
        try:
            #tick = self.get_all_ticks_by_timestamp(timestamp).loc[symbol]#r.hget('tick', str(timestamp)).loc[symbol]
            #print('NEW SEX')
            tick = r.hget(f'l.tick_{timestamp}', symbol)
            tick['timestamp'] = timestamp
        except Exception as e:
            print(f"Couldn't find {symbol} tick in TIME AXIS, trying old tick {timestamp}")
            try:
                all_ticks = self.get_all_ticks_by_symbol(symbol)              
                tick = all_ticks[all_ticks['timestamp'] <= timestamp].iloc[-1]
                #tick['timestamp'] = timestamp
            except Exception as e:
                print(f'GETTICK ERR: {e}')
                tick = {'o': np.nan, 'h': np.nan, 'l': np.nan, 'c': np.nan, 'v': np.nan, 'oi': np.nan, 'timestamp': None}
        return tick

    def get_latest_ltp(self, symbol):

        return r.get(f'ltp.{symbol}')

    def parse_date_from_symbol(self, symbol):
        if symbol.startswith('BANKNIFTY'):
            underlying = 'BANKNIFTY'
        elif symbol.startswith('NIFTY'):
            underlying = 'NIFTY'
        elif symbol.startswith('FINNIFTY'):
            underlying = 'FINNIFTY'
        elif symbol.startswith('MIDCPNIFTY'):
            underlying = 'MIDCPNIFTY'
        elif symbol.startswith('SENSEX'):
            underlying = 'SENSEX'


        return datetime.datetime.strptime(symbol.strip(underlying).strip('CE').strip('PE')[:6], '%y%m%d').date()

    def parse_strike_from_symbol(self, symbol):
        # ...
        if symbol.startswith('BANKNIFTY'):
            underlying = 'BANKNIFTY'
        elif symbol.startswith('NIFTY'):
            underlying = 'NIFTY'
        elif symbol.startswith('FINNIFTY'):
            underlying = 'FINNIFTY'
        elif symbol.startswith('MIDCPNIFTY'):
            underlying = 'MIDCPNIFTY'
        elif symbol.startswith('SENSEX'):
            underlying = 'SENSEX'

        # ...
        #print('KADDU:', symbol)
        return int(float(symbol.strip(underlying).strip('CE').strip('PE')[6:]))

    def replace_strike_in_symbol(self, symbol, strike):
        current_strike = self.parse_strike_from_symbol(symbol)
        new_symbol = symbol.replace(str(current_strike), str(strike))
        return new_symbol

    def shift_strike_in_symbol(self, symbol, shift_otm_count):
        # ...
        strike = self.parse_strike_from_symbol(symbol)
        # ...
        if symbol.startswith('BANKNIFTY'):
            underlying = 'BANKNIFTY'
        elif symbol.startswith('NIFTY'):
            underlying = 'NIFTY'
        elif symbol.startswith('FINNIFTY'):
            underlying = 'FINNIFTY'
        elif symbol.startswith('MIDCPNIFTY'):
            underlying = 'MIDCPNIFTY'
        elif symbol.startswith('SENSEX'):
            underlying = 'SENSEX'

        # ...
        strike_diff = strike_diff_dict[underlying]
        # ...
        opt_type = symbol[-2:]
        if opt_type == 'CE':
            shifter = 1
        else:
            shifter = -1
        # ...
        new_strike = int(float(strike + shift_otm_count*shifter*strike_diff))
        # ...
        new_symbol = symbol.replace(str(strike), str(new_strike))
        return new_symbol
    
    def get_dte(self, timestamp, symbol):

        expiry_date = self.parse_date_from_symbol(symbol)
        dte = (expiry_date-timestamp.date()).days

        if dte < 0:
            print(f'WARNING: {symbol} Expired')
            dte = 69

        return int(dte)



