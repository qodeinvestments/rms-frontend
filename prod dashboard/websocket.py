from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body, Depends , UploadFile, File,status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import json
import time
import glob
import numpy as np
import direct_redis
import datetime
import logging
import sys
from starlette.websockets import WebSocketState
from typing import List, Dict, Optional , Union
import pandas as pd
import helperFunctions
from jose import JWTError, jwt
import helperFunctions
from datetime import  timedelta, timezone
import copy
from functools import partial
from concurrent.futures import ThreadPoolExecutor
import pickle
import threading
import io
import ast 
import re
import copy
from pathlib import Path

from xxx.daily_tasks.position_sizing_updates import generate_pos_sizing_csv
from xxx.margin_inputs import margin_input

from xxx.utility import get_next_trading_day_ts

# JWT Configuration
SECRET_KEY = "SWANCAPITAL"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600
MARGIN_CHANGE_PASSWORD = 'SWAN'
TRADING_HOURS = (datetime.time(9, 0), datetime.time(15, 30))




app = FastAPI()
security = HTTPBearer()



# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# JWT Token functions
def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
      
        if username is None:
            raise credentials_exception
    except JWTError as e:
        print("JWT decoding error:", str(e))  # Log decoding error
        raise credentials_exception

    user = r.hgetall(f"user:{username}")
    if not user:
        raise credentials_exception
    return user


def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "Admin" and  current_user.get("role") != "Super Admin":
        raise HTTPException(status_code=403, detail="Not authorized to view users")
    return current_user


def super_admin_required(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "Super Admin":
        raise HTTPException(status_code=403, detail="Not authorized to view users")
    return current_user


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Only allow your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

r = direct_redis.DirectRedis()
try:
    r = direct_redis.DirectRedis()
    logger.info("Redis connection established")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    sys.exit(1)





latency_metrics = {}
Features_Map={
    'Signal Book':'signalbook',
    'Server Data':'serverData',
    'KeyDB Logs':'keydblogs',
    'Data Lags Details':'lagsData',
    'Errors':'errorLogs',
    # 'Margin Update':'marginupdate',
    'Broker Position Mismatch':'brokerpositionmismatch',
    'Daily Logs':'dailylogs'
}
Feature_Reverse_Map={
    
    'signalbook':'Signal Book',
    'serverData':'Server Data',
    'keydblogs':'KeyDB Logs',
    'lagsData':'Data Lags Details',
    'errorLogs':'Errors',
    # 'marginupdate':'Margin Update',
    'brokerpositionmismatch':'Broker Position Mismatch',
    'dailylogs':'Daily Logs'

}

ROLE_SOCKET_ALLOWLIST = {
    # Only these sockets are legal for each role
    "Client": {"clientData"},
    # add other constrained roles here if you ever need to
}
def socket_access_allowed(role: str, key: str) -> bool:
    """
    True  -> role may connect to this socket
    False -> block
    """
    allowed = ROLE_SOCKET_ALLOWLIST.get(role)
    # • If the role is in the table, enforce the allow-list
    # • If the role is absent (Admin, Super Admin, Monitor, …) allow everything
    return (key in allowed) if allowed is not None else True



#internal load balancer
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "main": [],
            "errorLogs":[],
            "keydblogs":[],
            "clientdetails": [],
            "basket": [],
            "strategy": [],
            "signalbook":[],
            "serverData":[],
            "clientData":[],
            
        }
        self.last_data: Dict[str, Dict] = {
            "main": {},
            "errorLogs":{},
            "keydblogs":{},
            "clientdetails": {},
            "basket": {},
            "strategy": {},
            "signalbook":{},
            "serverData":{},
            "clientData":{},
        }
        self.client_cache: Dict[WebSocket, Dict] = {}
    

    async def connect(self, websocket: WebSocket, connection_type: str):
        await websocket.accept()
        self.active_connections[connection_type].append(websocket)
        if connection_type == "clientdetails":
            self.client_cache[websocket] = {"name": "", "type": "", "last_data": None}

      

    async def disconnect(self, websocket: WebSocket, connection_type: str):
        
        try:
            self.active_connections[connection_type].remove(websocket)
        except ValueError as e:
            logger.error(f"Failed to remove websocket: {str(e)}")
        except KeyError as e:
            logger.error(f"Invalid connection type: {str(e)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
        if connection_type == "clientdetails":
            self.client_cache.pop(websocket, None)

    async def broadcast(self, message: str, connection_type: str):
        disconnected = []
        for connection in self.active_connections[connection_type]:
            try:
                if connection.client_state == WebSocketState.DISCONNECTED:
                    disconnected.append(connection)
                    continue
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error sending message to {connection_type} connection: {str(e)}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections[connection_type].remove(connection)

manager = ConnectionManager()



# async def update_data_task(key, get_data_function, sleep_interval):
#     global latency_metrics
#     while True:
#         try:
#             start_time = time.time()
#             manager.last_data[key] = get_data_function()
#             await manager.broadcast(json.dumps(manager.last_data[key]), key)
#             end_time = time.time()

#             latency = (end_time - start_time)
#             if key not in latency_metrics:
#                 latency_metrics[key] = []
#             latency_metrics[key]=latency

#             #logger.info(f"Latency for {key} WebSocket: {latency:.2f} s")

#         except Exception as e:
#             logger.error(f"Error in update_{key}_data: {str(e)}")

#         await asyncio.sleep(sleep_interval)

async def update_data_task(key, get_data_function, sleep_interval):
    global latency_metrics
    while True:
        try:
            start_time = time.time()
            # Fetch data and update the manager's shared state
            manager.last_data[key] = get_data_function()
            end_time = time.time()

            latency = (end_time - start_time)
            if key not in latency_metrics:
                latency_metrics[key] = []
            latency_metrics[key]=latency

            #logger.info(f"Latency for {key} WebSocket: {latency:.2f} s")

        except Exception as e:
            logger.error(f"Error in update_{key}_data: {str(e)}")

        await asyncio.sleep(sleep_interval)


@app.on_event("startup")
async def startup_event():
    tasks = [
        {"key": "main", "function": helperFunctions.get_main_data, "interval": 0.5},
        {"key": "serverData", "function": helperFunctions.get_serverData_data, "interval": 2},
        {"key": "signalbook", "function": helperFunctions.get_signalbook_data, "interval": 1},
        {"key": "keydblogs", "function": helperFunctions.get_keydblogs_data, "interval": 0.5},
        {"key": "errorLogs", "function": helperFunctions.get_errorLogs_data, "interval": 1},
        {"key": "clientData", "function": helperFunctions.get_clientData, "interval": 0.5},
      
    ]

    for task in tasks:
        asyncio.create_task(update_data_task(task["key"], task["function"], task["interval"]))

    
    



async def authenticate_user(websocket: WebSocket):
    """
    Authenticate the user using the token sent over the WebSocket connection.

    Args:
        websocket (WebSocket): The WebSocket connection.

    Returns:
        dict: User data if authentication is successful, None otherwise.
    """
    try:
        raw_token = await websocket.receive_text()
        user_token = parse_user_token(raw_token)  # Parse and validate token
        user_data = await get_current_user(user_token)  # JWT validation logic

        if not user_data:
            logger.warning("Authentication failed: Invalid token")
            await websocket.close(code=1008, reason="Invalid token")
            return None

        # logger.info(f"User authenticated: {user_data}")
        return user_data
    except ValueError as ve:
        logger.error(f"Token parsing error: {ve}")
        await websocket.close(code=1008, reason="Invalid token format")
        return None
    except Exception as auth_error:
        logger.error(f"Authentication error: {auth_error}")
        await websocket.close(code=1008, reason="Authentication failed")
        return None



# Utility function for token parsing
def parse_user_token(raw_token: str) -> str:
    
    """
    Parses the raw token received from the client.

    Args:
        raw_token (str): The raw token string received via WebSocket.

    Returns:
        str: The parsed token.

    Raises:
        ValueError: If the token format is invalid.
    """
    try:
        
        return raw_token.split(':')[1][1:-2]
    except IndexError:
        raise ValueError("Invalid token format")
    
    
# WebSocket endpoints
async def handle_websocket(websocket: WebSocket, key: str, send_initial: bool = False):
    """
    Generic WebSocket handler that can be configured for different endpoints.

    Args:
        websocket (WebSocket): The WebSocket connection.
        key (str): The data key to handle.
        send_initial (bool): Whether to send initial data to the client.
        auto_send (bool): If True, automatically sends data on interval without waiting for client messages.
    """
    try:
        # Step 1: Connect to WebSocket
        await manager.connect(websocket, key)
        logger.info(f"WebSocket connection established for key: {key}")

        # Step 2: Authenticate user (occurs only once)
        user_data = await authenticate_user(websocket)
        if not user_data:
            return  # Authentication failed, WebSocket already closed
        
        # ✋  ROLE-based socket gating
        role = user_data.get("role")
        if not socket_access_allowed(role, key):
            await websocket.close(code=1008, reason="Access denied")
            logger.info(f"{role=} tried to open {key=} – blocked")
            return
        
        if key in Feature_Reverse_Map:
            feature_val=Feature_Reverse_Map[key]
            if feature_val not in user_data['features']:
                return 

        # Step 3: Send initial data if required
        if send_initial:
            await helperFunctions.send_initial_data(websocket)
            logger.info("Initial data sent to client.")

        # Step 4: Handle WebSocket messages (continuous data transmission)
        while websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                if key == "main" :
                    filtered_data = copy.deepcopy(manager.last_data[key])
                    if user_data['role']!='Admin' or user_data['role']!='Super Admin':
                        filtered_data["client_data"] = [
                            item for item in filtered_data["client_data"] if item.get("name") in user_data["account_access"]
                        ]
                    await websocket.send_text(json.dumps(filtered_data))
                    await asyncio.sleep(0.5)

                elif key=="clientData":
                    perc_map = {
                        acct["name"]: (acct["dateRanges"][-1]["percentage"] or 100)*0.01
                        for acct in user_data.get("account_percentages", [])
                        if acct.get("dateRanges")
                    }
                    
                    # rebuild client_data in one comprehension:
                    filtered_data = {
                        **manager.last_data[key],
                        "client_data": [
                            {
                                k: (v * perc_map.get(item['name'], 1)) if isinstance(v, (int, float)) and k != 'name' else v
                                for k, v in item.items()
                            }
                            for item in manager.last_data[key]['client_data']
                            if item.get('name') in user_data.get('account_access', [])
                        ]
                    }

                    await websocket.send_text(json.dumps(filtered_data))
                    await asyncio.sleep(5)

                else:
                    await websocket.send_text(json.dumps(manager.last_data[key]))
                    await asyncio.sleep(0.5)
             
            except WebSocketDisconnect as e:
                logger.info(f"WebSocket disconnected with code {e.code}")
                break
            except Exception as loop_error:
                logger.error(f"Error in WebSocket loop: {loop_error}")
                break

    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}")
    finally:
        # Step 5: Cleanup
        await manager.disconnect(websocket, key)
        logger.info(f"WebSocket connection closed for key: {key}")


# WebSocket endpoints
@app.websocket("/ws")
async def websocket_main(websocket: WebSocket):
    await handle_websocket(websocket, "main", send_initial=True)

@app.websocket("/clientData")
async def websocket_clientData(websocket: WebSocket):
    await handle_websocket(websocket, "clientData", send_initial=True)

@app.websocket("/serverData")
async def websocket_server_data(websocket: WebSocket):
    await handle_websocket(websocket, "serverData", send_initial=True)

@app.websocket("/keydblogs")
async def websocket_keydblogs(websocket: WebSocket):
    await handle_websocket(websocket, "keydblogs")

@app.websocket("/errorLogs")
async def websocket_error_logs(websocket: WebSocket):
    await handle_websocket(websocket, "errorLogs")

@app.websocket("/signalbook")
async def websocket_signalbook(websocket: WebSocket):
    await handle_websocket(websocket, "signalbook")

    
@app.websocket("/clientdetails")
async def clientdetails_websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "clientdetails")
    global latency_metrics
    key="clientdetails"
    user_data = await authenticate_user(websocket)
    if not user_data:
        return  # Authentication failed, WebSocket already closed
    allowed_accounts=user_data['account_access']
 
    if not socket_access_allowed(user_data.get("role"), "clientData"):
        await websocket.close(code=1008, reason="Access denied")
        return   
    
    try:
        while True:
            start_time = time.time()
            if websocket.client_state == WebSocketState.DISCONNECTED:
                break
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1)
                received_client = json.loads(data).get('client_data', {})
                manager.client_cache[websocket]["name"] = received_client.get('name', manager.client_cache[websocket]["name"])
                manager.client_cache[websocket]["type"] = received_client.get('type', manager.client_cache[websocket]["type"])
            except asyncio.TimeoutError:
                pass
            
            name = manager.client_cache[websocket]["name"]
            type = manager.client_cache[websocket]["type"]
            
            # ✋ Access check
            if name not in allowed_accounts:
                await websocket.send_text(json.dumps({"error": "Access denied"}))
                break
            
            book = None
            if type == "Positions":  
                book = helperFunctions.get_client_rms_df(name)
            elif type == "Order":
                book = helperFunctions.get_client_live_order_book(name)
            elif type == "TradeBook":
                book = helperFunctions.get_client_live_trade_book(name)
            elif type == "Combined DF":
                book = helperFunctions.get_client_combined_df(name)
            elif type == "Combined Orders":
                book = helperFunctions.get_client_combined_orders(name)
            elif type=='Combined Trades':   
                book = helperFunctions.get_client_combined_trades(name)
            elif type=='Fund Summary':
                book = helperFunctions.get_client_fund_summary(name)
            elif type=='Zerodha Order Book' or type=='XTS Order Book':
                book=helperFunctions.get_zerodha_order_book(name)
            elif type=='Zerodha Position Book' or type=='XTS Position Book':
                book=helperFunctions.get_zerodha_position_book(name)
            elif type=='Holdings':
                book=helperFunctions.get_client_holding(name)
            elif type == 'EOD':
                book=helperFunctions.get_rms_prev_day(name)
                
            

            manager.client_cache[websocket]["last_data"] = {"time": helperFunctions.get_time(), "table_data": book}
            manager.client_cache[websocket]["last_update"] = time.time()
            end_time = time.time()

            latency = (end_time - start_time) 
            if key not in latency_metrics:
                latency_metrics[key] = []
                latency_metrics[key].append(latency)

            #logger.info(f"Latency for {key} WebSocket: {latency:.2f} s")

            await websocket.send_text(json.dumps(manager.client_cache[websocket]["last_data"]))
            await asyncio.sleep(0.5)
    except Exception as e:
        logger.error(f"ClientDetailsWebSocket error: {str(e)}")
    finally:
        await manager.disconnect(websocket, "clientdetails")


@app.websocket("/chart/strategy")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "strategy")
    client_name = None
    global latency_metrics
    key="strategy"
    try:
        # Send initial data and get the client name
        client_name = await send_strategy_initial_data(websocket)

        # Continue the loop to send data periodically
        while True:
            # Ensure the WebSocket is connected
            if websocket.client_state != WebSocketState.CONNECTED:
                break
            try:
                start_time=time.time()
                # If client_name is available, send data without receiving new input
                if client_name:
                    client_data = await helperFunctions.get_last_strategy_data(client_name)
                    end_time = time.time()

                    latency = (end_time - start_time) 
                    if key not in latency_metrics:
                        latency_metrics[key] = []
                        latency_metrics[key].append(latency)

                    #logger.info(f"Latency for {key} WebSocket: {latency:.2f} s")
                    await websocket.send_text(json.dumps(client_data))
                    await asyncio.sleep(10)
                else:
                    await websocket.send_text(json.dumps({"error": "No client name provided"}))
                    await asyncio.sleep(10)
                # Optional: wait for a new message with a timeout to check for updates or break conditions
                try:
                    val = await asyncio.wait_for(websocket.receive_text(), timeout=1)
                    data = json.loads(val)
                    if data:
                        client_name = data.get('name')  # Update client name if received
                except asyncio.TimeoutError:
                    # No new message received within 1 second, continue sending data
                    continue
            except WebSocketDisconnect as e:
                if e.code == 1001:
                    logger.info(f"WebSocket closed normally with code {e.code}")
                else:
                    logger.warning(f"WebSocket disconnected with code {e.code}")
                break
            except Exception as e:
                logger.error(f"Unexpected error in WebSocket: {str(e)}")
                break
    except Exception as e:
        logger.error(f"Strategy WebSocket error: {str(e)}")
    finally:
        await manager.disconnect(websocket, "strategy")


async def send_strategy_initial_data(websocket: WebSocket):
    try:
        # Attempt to receive initial data with a timeout
        val = await asyncio.wait_for(websocket.receive_text(), timeout=1)
        data = json.loads(val)
        client_name = data.get('name') if data else None
        
        
        
        user_data = await get_current_user(data['token'])  # JWT validation logic
        if not user_data:
            return  # Authentication failed, WebSocket already closed
        allowed_accounts=user_data['account_access']

        # ✋ Access check
        if data:
            client_name = data.get('name')  # Update client name if received
        if client_name not in allowed_accounts:
            await websocket.send_text(json.dumps({"error": "Access denied"}))
            return None

        # Get and send strategy data if client name is available
        if client_name:
            initial_data = await helperFunctions.get_strategy_data(client_name)
            await websocket.send_text(json.dumps(initial_data))
            await asyncio.sleep(10)
            return client_name  # Return the client name to be used in the while loop
        else:
            await websocket.send_text(json.dumps({"error": "No client name provided"}))
            await asyncio.sleep(10)
            return None
    except asyncio.TimeoutError:
        # Handle timeout during initial data receiving
        await websocket.send_text(json.dumps({"error": "Timeout waiting for initial data"}))
        await asyncio.sleep(10)
        return None
    except Exception as e:
        # Handle other potential errors
        logger.error(f"Error in sending initial strategy data: {str(e)}")
        return None



@app.websocket("/chart/basket")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "basket")
    client_name = None
    global latency_metrics
    key="basket"
   
    
 
    try:
        while True:
            if websocket.client_state == WebSocketState.DISCONNECTED:
                break
            try:
                start_time=time.time()
                val = await asyncio.wait_for(websocket.receive_text(), timeout=1)
                data = json.loads(val)

                user_data = await get_current_user(data['token'])  # JWT validation logic
                if not user_data:
                        return  # Authentication failed, WebSocket already closed
                allowed_accounts=user_data['account_access']
                            
                            
                # ✋ Access check
                if data:
                    client_name = data.get('name')  # Update client name if received
                if client_name not in allowed_accounts:
                    await websocket.send_text(json.dumps({"error": "Access denied"}))
                    break
                if client_name:
                    client_data = await helperFunctions.get_basketData_swan(client_name)
                    end_time = time.time()

                    latency = (end_time - start_time) 
                    if key not in latency_metrics:
                        latency_metrics[key] = []
                        latency_metrics[key].append(latency)

                    #logger.info(f"Latency for {key} WebSocket: {latency:.2f} s")
                    await websocket.send_text(json.dumps(client_data))
                    await asyncio.sleep(10)
                else:
                    await websocket.send_text(json.dumps({"error": "No client name provided"}))
                    await asyncio.sleep(10)
            except asyncio.TimeoutError:
                # No message received within 1 second, continue the loop
                if client_name:
                    # Optionally send updated data even if no new message was received
                    client_data = await helperFunctions.get_basketData_swan(client_name)
                    await websocket.send_text(json.dumps(client_data))
                    await asyncio.sleep(10)
                continue
            except WebSocketDisconnect as e:
                if e.code == 1001:
                    logger.info(f"WebSocket closed normally with code {e.code}")
                else:
                    logger.warning(f"WebSocket disconnected with code {e.code}")
                break
            except Exception as e:
                logger.error(f"Unexpected error in WebSocket: {str(e)}")
                break
    except Exception as e:
        logger.error(f"Basket WebSocket error: {str(e)}")
    finally:
        await manager.disconnect(websocket, "basket")

        
@app.get('/latency')
async def getlatency():
    
    global latency_metrics
    return latency_metrics

@app.get("/lagsData")
async def get_lag_data():
    val = helperFunctions.get_lagsData_data()  # Assuming this returns a dictionary
    return val  # Return the dictionary directly



# Protected routes using JWT authentication
@app.get("/users")
async def get_users_data(current_user: dict = Depends(admin_required)):

    data = []
    user_keys = r.lrange('user:accounts', 0, -1)
    for key in user_keys:
        user = r.hgetall(key) 
        data.append(user)
    return data

# Modified login endpoint to return JWT token
@app.post("/login")
async def login(request: dict):
    username = request.get("username").casefold()
    password = request.get("password")
    print(request)
    user = r.hgetall(f"user:{username}")
   
    if len(user.keys()) == 0:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )
    
    if user.get("password") != password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    
    user_info = {
        'username': user.get("username"),
        'role': user.get("role"),
        'email': user.get("email"), 
        'account_access': user.get("account_access")
    }

    return {
        "success": True,
        "message": "Login successful",
        "user": user_info,
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get('/getAccounts')
async def getAccounts(current_user: dict = Depends(get_current_user)):

    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")

    return {key: value for key, value in helperFunctions.active_clients.items() if value}

@app.get('/getRoles')
async def getRoles(current_user: dict = Depends(admin_required)):
    return ['Admin', 'Monitor', 'Client','Super Admin']


@app.get('/getFeatures')
async def getFeatures(current_user: dict = Depends(admin_required)):
    return list(Features_Map.keys())


@app.post("/addUser")
async def add_user(request: dict):
    username = request.get("username").casefold()
    password = request.get("password")
    email = request.get("email")
    role = "Monitor"

    user_key = f"user:{username}"


    if r.exists(user_key):
        return {"status": "error", "message": "Username already exists"}

    user_data = {
        'username': username,
        'password': password,
        'role': role,
        'email': email,
        'account_access': [],
        'features':[]
    }

    try:
        # Add the user to Redis
        r.hmset(user_key, user_data)
        r.rpush('user:accounts', user_key)
        return {"status": "success", "message": "User added successfully"}
    except Exception as e:
        logger.error(f"Error storing user data in Redis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    
@app.post("/deleteUser")
async def deleteUser(request: dict, current_user: dict = Depends(admin_required)):


    if request['totpCode'] != MARGIN_CHANGE_PASSWORD:
        raise HTTPException(status_code=400, detail="Password Incorrect!")
    

    try:
        username = request['user'].get('username')
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")

        username = username.casefold()
        user_key = f"user:{username}"
        user = r.hgetall(user_key)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        deleted_count = r.delete(user_key)
        if deleted_count == 1:
            r.lrem("user:accounts", 0, user_key)
            return {"success": True, "message": f"User '{username}' successfully deleted"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete user '{username}'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/editUser")
async def edit_user(request: dict, current_user: dict = Depends(admin_required)):

    try:
        username = request.get("username")
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")

        username = username.casefold()
        user_key = f"user:{username}"
        
        existing_user = r.hgetall(user_key)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        updateable_fields = ["password", "email", "role", "account_access",'features']
        if request.get('role') == 'Admin' or request.get('role')=='Super Admin':
            request['account_access'] = list(helperFunctions.active_clients.keys())
            request['features']=list(Features_Map.keys())
        
        updates = {
            field: request[field]
            for field in updateable_fields
            if field in request and field != 'username'
        }
        print("updates is ",updates)
        if updates.get('role') != 'Client':
            r.hdel(user_key, 'account_percentages')

        if 'account_percentages' in request and updates['role']=='Client':
            updates['account_percentages']=request['account_percentages']
        
        print("updates sss:",updates)
        if not updates:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")
        
        r.hmset(user_key, updates)
        
        return {
            "success": True,
            "message": f"User '{username}' successfully updated",
            "updated_fields": list(updates.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validate-token")  # Changed to GET
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # Get token from Authorization header
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        
        user = r.hgetall(f"user:{username}")
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token: user not found")
        
        return {"valid": True, "detail": "Token is valid", "username": username}
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

#MarginUpdate Page



def smart_depickle(redis_data):
    """
    Automatically detects data type and unpickles accordingly
    """
    try:
        # If empty data
        if not redis_data:
            return redis_data
        
        # For dictionaries (hgetall results)
        if isinstance(redis_data, dict):
            return {
                key.decode('utf-8') if isinstance(key, bytes) else key: 
                pickle.loads(value) if value else None 
                for key, value in redis_data.items()
            }
        
        # For lists (lrange results)
        elif isinstance(redis_data, list):
            return [
                item.decode('utf-8') if isinstance(item, bytes) else item 
                for item in redis_data
            ]
        
        # For single values
        else:
            return pickle.loads(redis_data) if redis_data else None
            
    except Exception as e:
        print(f"Debug - Data type: {type(redis_data)}")
        return redis_data  # Return original data if unpickling fails



@app.get("/getBasket")
async def get_basket_data(current_user: dict = Depends(admin_required)):

    # Use Redis command directly without await
    return r.lrange('all_baskets', 0, -1)


@app.get('/getPositionSizingClients')
async def get_position_sizing_clients(current_user: dict = Depends(admin_required)):

    # Pre-filter clients dictionary
    return {
        key: value 
        for key, value in helperFunctions.clients.items() 
        if value.get('user_id') and helperFunctions.active_clients[key]==True
    }


@app.get('/MarginData')
async def get_margin_data(current_user: dict = Depends(admin_required)):

 
    pos_size_params=r.hgetall('pos_size_params')
    pf_values=r.hgetall('user_pf_value')
    baskets=r.lrange('all_baskets', 0, -1)
    swan_baskets=r.lrange('swan_baskets', 0, -1)
    margininfo = r.hgetall('margininfo')
    putProtection=r.hgetall('put_protection_inputs')
    limits=r.hgetall('equity_limits')
    cashalertinputs=r.hgetall('cash_alert_input')
    portfoliochangepercentage=r.hgetall('portfolio_change_percentage')

 
    
    # Process strategy data efficiently
    result = {}
    for account_name, strategies in pos_size_params.items():
        try:
            result[account_name] = [
                {"strategy": strategy, **details}
                for strategy, details in strategies.items()
            ]
        except AttributeError:
            # Handle case where strategies might not be a dict
            continue
    
    # Filter portfolio values in one pass
    filtered_pf = {
        key: value 
        for key, value in pf_values.items()  
    }
   
    
    return {
        'live_clients': r.hgetall('live_clients'),
        'params': result,
        'pf': filtered_pf,
        'margininfo':margininfo,
        'putProtection': putProtection,
        'limits': limits,
        'baskets': baskets,
        'swan_baskets':swan_baskets,
        'cashalertinputs':cashalertinputs,
        'portfoliochangepercentage':portfoliochangepercentage,
        'margin_update_check':r.hgetall('margin_update_check'),
        'id_to_name_map':helperFunctions.userIdToUserNameMap,
        'next_trading_day':get_next_trading_day_ts(datetime.datetime.now()).date().strftime('%Y-%m-%d'),
        'market_holiday':r.get('market_holiday'),
        'userNameToUserIdDict':helperFunctions.userIdToUserNameMap
    }


@app.post("/UpdatePortfolioValue")
async def update_portfolio_value(request: dict, current_user: dict = Depends(admin_required)):

    current_time = datetime.datetime.now().time()
    start_time = datetime.time(9, 0)
    end_time = datetime.time(15, 30)
    
    if start_time <= current_time <= end_time:
        raise HTTPException(
            status_code=400,
            detail="Function cannot be called during trading hours (9:00 AM to 3:30 PM)"
        )

    if request['totp_code'] != MARGIN_CHANGE_PASSWORD:
        raise HTTPException(status_code=400, detail="Password Incorrect!")
    
    print(request)
    strategy_map = {
        item.pop('strategy'): item 
        for item in request['params']
    }
    print("strategy map is the :" , request)
    margininfoupdate={
            'drawdownMargin': request['ddMarginPercent'],
            'excessMargin': request['excessMargin'],
            'minimumMargin': request['minMargin'],
    }
    
    if len(strategy_map)>0:
        r.hset('pos_size_params', request['account'], strategy_map)
    r.hset('user_pf_value', request['account'], request['portfolioValue'])
    r.hset(
        'margininfo',
        request['account'],
        margininfoupdate
    )
    if 'account' in request and 'putProtection' in request:
        r.hset('put_protection_inputs', request['account'], request['putProtection'])
    if 'account' in request and 'limits' in request:
        r.hset('equity_limits', request['account'], request['limits'])
    if 'account' in request and 'cashalertpercentage' in request:
        r.hset('cash_alert_input',request['account'],request['cashalertpercentage'])
    if 'account' in request and 'portfoliochangepercentage' in request:
        r.hset('portfolio_change_percentage',request['account'],request['portfoliochangepercentage'])
    





@app.post("/fetchClientMultiplier")
async def fetchClientMultiplier(request: dict, current_user: dict = Depends(admin_required)):

    # Get the current time
    current_time = datetime.datetime.now().time()
    
    #Define time range
    start_time = datetime.time(9, 0)  # 9:00 AM
    end_time = datetime.time(15, 30)  # 3:30 PM
    
    # Check if the current time is between 9:00 AM and 3:30 PM
    if start_time <= current_time <= end_time:
        raise HTTPException(
            status_code=400,
            detail="Function cannot be called during trading hours (9:00 AM to 3:30 PM)"
        )
    

    pos_size_params=r.hgetall('pos_size_params')
    pf_values=r.hgetall('user_pf_value')
    baskets=r.lrange('all_baskets', 0, -1)
    margininfo = r.hgetall('margininfo')



    # Process request data
    data = request
    if data['totp_code']!=MARGIN_CHANGE_PASSWORD:
         raise HTTPException(
            status_code=400,
            detail="Password Incorrect!"
        )

    get_data=margin_input({
        "Account": request['account'],
        # "Date": request['date'],
        "drawdownMargin":  margininfo[request['account']]['drawdownMargin'],
        "excessMargin" : margininfo[request['account']]['excessMargin'],
        "minimumMargin": margininfo[request['account']]['minimumMargin'],
        "portfolioValue":pf_values[request['account']]
    },
    {"params" : pos_size_params[request['account']] if request['account'] in pos_size_params else {}}
    )
    
    return get_data



@app.post("/UpdateClientMultiplier")
async def update_client_multiplier(request: dict, current_user: dict = Depends(admin_required)):


    if request['totp_code'] != MARGIN_CHANGE_PASSWORD:
        raise HTTPException(status_code=400, detail="Password Incorrect!")

    target_account = request.get('account')
    new_multiplier = request.get('client_multiplier')
    clients=r.hgetall('live_clients')
    for key, value in clients.items():
        if value.get('user_id') == target_account:
            value['client_multiplier'] = new_multiplier
            # Remove await from hset
            r.hset('live_clients', key, value)
            return {"message": "Client multiplier updated successfully"}
    
    return {"message": "Client not found"}



def tell_how_many_days_to_come(day_to_run):
    # Iterate for 7 days as an example
    holidays = [item['date'] for item in r.get('market_holiday')]
    c=1
    today = datetime.date.today() 
    for i in range(1,7):
        next_day = today + datetime.timedelta(days=i)
        day_name = next_day.strftime("%A")  # Full day name
        date_str = next_day.strftime("%Y-%m-%d")
        if day_name=='Saturday' or day_name=='Sunday' or date_str in holidays:
            continue 
        if day_name in day_to_run:
            break
        c+=1
    return c

def fill_the_message(strat_running,strat_to_run,baskets):
    message=[]
    for check_strat in strat_running:
        ##should not be present 
        if check_strat not in strat_to_run:
            message.append(f'{check_strat} should not be present')

    for strat,details in strat_to_run.items():
        if details['type']=='all':
            ## should be present
            if strat not in strat_running and strat in baskets:
                message.append(f'{strat}  should be present')

        elif details['type']=='specific_days':
             day_to_run=details['value']
             c=tell_how_many_days_to_come(day_to_run)
             #should  be present 
             if c==1:
                if strat not in strat_running and strat in baskets:
                    message.append(f'{strat} should be present')
             #should not be present
             else:
                if strat in strat_running :
                  message.append(f'{strat} should not be present')
    return message

def send_margin_update_telegram_alert(params):
    margin_update_check=r.hgetall('margin_update_check')


   

    main_table_message=[]
    main_table_message.append("📋 Main Table")
    swan_baskets=r.lrange('swan_baskets', 0, -1)
    for user,value in params.items():
        username=helperFunctions.userIdToUserNameMap[user]
        strat_running=value.keys()
        strat_to_run=margin_update_check[username]  
        new_arr=fill_the_message(strat_running,strat_to_run,swan_baskets)
        if len(new_arr)>0:
            main_table_message.append(f'{user}:')
            main_table_message.extend(new_arr)



    baskets=r.lrange('all_baskets', 0, -1)
    client_multiplier_table_message=[]
    client_multiplier_table_message.append("📋 Client Multiplier Table")
    print("in Client Multiplier")         
    for client,detail in r.hgetall('live_clients').items():
        if helperFunctions.active_clients[client]==True:
            strat_running=detail['client_multiplier'].keys()
            strat_to_run=margin_update_check[client]  
            new_arr=fill_the_message(strat_running,strat_to_run,baskets)
            if len(new_arr)>0:
                client_multiplier_table_message.append(f'{client}:')
                client_multiplier_table_message.extend(new_arr)
    
    if len(main_table_message)==1:
        main_table_message.append("Everything Is Perfect.")
    if len(client_multiplier_table_message)==1:
        client_multiplier_table_message.append("Everything Is Perfect.")

    main_message = "\n".join(main_table_message)
    client_multiplier_message="\n".join(client_multiplier_table_message)

    helperFunctions.send_telegram_alert(main_message)
    helperFunctions.send_telegram_alert(client_multiplier_message)
    return




@app.post("/UpdateMarginForAllAccounts")
async def update_margin_for_all_accounts(request: dict, current_user: dict = Depends(admin_required)):

    # Check trading hours
    current_time = datetime.datetime.now().time()
    start_time = datetime.time(9, 0)
    end_time = datetime.time(15, 30)
    
    if start_time <= current_time <= end_time:
        raise HTTPException(
            status_code=400,
            detail="Function cannot be called during trading hours (9:00 AM to 3:30 PM)"
        )

    if request['totp_code'] != MARGIN_CHANGE_PASSWORD:
        raise HTTPException(status_code=400, detail="Password Incorrect!")
    try:
            inputs=r.hgetall('user_pf_value')
            params=r.hgetall('pos_size_params')
            putProtection=r.hgetall('put_protection_inputs')
            limits=r.hgetall('equity_limits')

            params_map={}

            for client,details in helperFunctions.clients.items():
                if helperFunctions.active_clients[client]:
                    user_id=details['user_id']
                    params_map[user_id]=params[user_id]
                    # params_map[user_id]=params[user_id]

            params=params_map

            inputmap={}
            putprotectionmap={}
            equitylimitsmap={}
        
            for client,value in putProtection.items():
                if client in params:
                    putprotectionmap[client]=value

            for client,value in inputs.items():
                if client in params:
                    inputmap[client]=value

            for client,value in limits.items():
                if client in params:
                    equitylimitsmap[client]=value

            
            print(inputs)
            print(params)
            print(limits)
            print(putprotectionmap)
            send_margin_update_telegram_alert(params)
          

            # Execute and get DataFrame result
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                df_result = await loop.run_in_executor(
                    pool, 
                    partial(generate_pos_sizing_csv, inputmap, params, equitylimitsmap,putprotectionmap)
                )
                
            # Convert DataFrame to records format
            df_data = df_result.to_dict('records')
                
            return {
                "message": "Margin updated for all accounts successfully",
                "dataframe": {
                    "data": df_data,
                    "columns": df_result.columns.tolist()
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update margins: {str(e)}"
        )
    


@app.get('/activeConnections')
async def get_active_connection():
    return { key: len(connections) for key, connections in manager.active_connections.items() }


@app.get('/getmismatchpdf')
async def getmismatchpdf(current_user: dict = Depends(get_current_user)):
    
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")

    try:
        # Read all sheets from the excel file
        sheets = pd.read_excel('./all_clients_mismatches.xlsx', sheet_name=None)
        # Create an in-memory output file for the new Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment; filename=mismatches.xlsx"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Excel file: {str(e)}"
        )





@app.get("/live_strats")
async def get_live_strategies(current_user: dict = Depends(get_current_user)):
    # Ensure the user is valid (as you already do)
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    return helperFunctions.compute_live_strategies()


# @app.post("/Psar")
# async def update_margin_for_all_accounts(request: dict, current_user: dict = Depends(get_current_user)):
   
#     def calculate_psar(timeframe, futprice, max_af, af, ma_period=20):
#         data = futprice.copy()
#         if timeframe in ['D', '2D', 'M', 'MONTH']:
#             # Filter market hours using boolean masking
#             mask = (data['timestamp'].dt.time >= pd.to_datetime('9:05').time()) & \
#                 (data['timestamp'].dt.time <= pd.to_datetime('15:30').time())
#             data = data[mask]
            
#             # Then resample
#             data = data.resample(timeframe, on='timestamp').agg({
#                 'o': 'first',
#                 'h': 'max',
#                 'l': 'min',
#                 'c': 'last'
#             }).dropna().reset_index()
#         else:
#             # For minute-based timeframes
#             resample_tf = timeframe
#             data = data.resample(resample_tf, on='timestamp').agg({
#                 'o': 'first',
#                 'h': 'max',
#                 'l': 'min',
#                 'c': 'last'
#             }).between_time("9:05", "15:30").dropna().reset_index()
    
#         # data = data.resample(timeframe ,on='timestamp').agg({'o':'first', 'h': 'max', 'l': 'min', 'c':'last'}).between_time("9:05", "15:30").dropna().reset_index()

#         if max_af==-1 and af==-1:
#             return pd.DataFrame({
#                 'timestamp': data['timestamp'], 
#                 'close': data['c'], 
#                 'open': data['o'],
#                 'high': data['h'],
#                 'low': data['l'],
#             })
#          # Calculate moving average
#         if ma_period!=-1:
#             data['ma'] = data['c'].rolling(window=ma_period).mean()
#         max_acceleration = max_af
#         acceleration = af

#             # Prepare arrays
#         highs = data['h'].values
#         lows = data['l'].values
#         n = len(data)

#         psar = np.full(n, np.nan) 
#         trend = np.ones(n, dtype=int) 
#         extreme_point = np.zeros(n)
#         acceleration_factor = np.full(n, acceleration)
#         psar[0] = highs[0] 
#         extreme_point[0] = highs[0]



#         for i in range(1, n):
#             psar[i] = psar[i - 1] + acceleration_factor[i - 1] * (extreme_point[i - 1] - psar[i - 1])
#             if trend[i - 1] == 1:
#                 extreme_point[i] = max(extreme_point[i - 1], highs[i])
#                 if lows[i] < psar[i]:
#                     trend[i] = -1
#                     psar[i] = extreme_point[i - 1]
#                     extreme_point[i] = lows[i]
#                     acceleration_factor[i] = acceleration
#                 else:
#                     trend[i] = 1
#                     acceleration_factor[i] = min(acceleration_factor[i - 1] + acceleration, max_acceleration)
#             else:  
#                 extreme_point[i] = min(extreme_point[i - 1], lows[i])
#                 if highs[i] > psar[i]:
#                     trend[i] = 1
#                     psar[i] = extreme_point[i - 1]
#                     extreme_point[i] = highs[i]
#                     acceleration_factor[i] = acceleration
#                 else:
#                     trend[i] = -1
#                     acceleration_factor[i] = min(acceleration_factor[i - 1] + acceleration, max_acceleration)

#         psar_df = pd.DataFrame(psar, index=data.index)
        
#         psar_df = pd.DataFrame({
#             'timestamp': data['timestamp'], 
#             'close': data['c'], 
#             'open': data['o'],
#             'high': data['h'],
#             'low': data['l'],
#             'psar': psar
#         })

#         if ma_period!=-1:
#             psar_df['ma'] = data['ma']


#         psar_df = psar_df.dropna()


#         return psar_df

#     # Usage example:
#     index=request['symbol']
#     time_map={
#         '1m':'1min',
#         '5m':'5min',
#         '10m':'10min',
#         '15m':'15min',
#         '30m':'30min',
#         '1h':'60min',
#         '1d':'D',

#     }
#     timeframe=time_map[request['timeframe']]

    
#     indicators=request['indicators']
#     psar_setting=None
#     ma_setting=None
#     for indicator in indicators:
#         if indicator['name']=='Psar':
#             psar_setting=indicator['setting']
#         if indicator['name']=='MA':
#             ma_setting=indicator['setting']

#     dff=helperFunctions.ei.get_all_ticks_by_symbol(f'{index}SPOT')


#     result = calculate_psar(timeframe, dff, psar_setting['af'] if psar_setting else -1 , psar_setting['max-af'] if psar_setting else -1, ma_setting['period'] if ma_setting else -1)
#     df=pd.DataFrame(result)

#     # Convert the timestamp column to datetime
#     df["timestamp"] = pd.to_datetime(df["timestamp"])

#     # Define the start and end times as datetime objects
#     start_time = pd.to_datetime('2025-01-21 09:00:00')
#     end_time = pd.to_datetime('2025-01-24 15:29:59')

#     # Filter the DataFrame within the range
#     # df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)].reset_index(drop=True)
#     df['timestamp'] = df['timestamp'] + pd.Timedelta(hours=5, minutes=30)

#     return df



@app.post("/Psar")
async def update_margin_for_all_accounts(request: dict, current_user: dict = Depends(get_current_user)):

    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
  

    index = request["symbol"]
    timeframe=request['timeframe']
    indicators=request['indicators']
    psar_settings = next((item for item in indicators if item["name"] == "Psar"), None)
    custom_psar_af = psar_settings['setting'].get('af', 0.001) if psar_settings else 0.001
    custom_psar_max_af = psar_settings['setting'].get('max-af', 0.001) if psar_settings else 0.001
    long_options_settings=next((item for item in indicators if item["name"] == "Long"), None)

    dff = helperFunctions.ei.get_all_ticks_by_symbol(f'{index}SPOT')
    
    if psar_settings is not None:
        return helperFunctions.give_psar_chart(dff, custom_psar_af, custom_psar_max_af)
    elif long_options_settings is not None:
        return helperFunctions.give_long_chart(dff, index,long_options_settings["setting"])
    
    if timeframe == '5m':
        dff = dff.resample('5min' ,on='timestamp').agg({'o':'first', 'h': 'max', 'l': 'min', 'c':'last'}).between_time("9:05", "15:30").dropna().reset_index()
    
    dff.drop(columns=['v', 'oi'], errors='ignore', inplace=True)
    # 1️⃣ remove tz and add the offset
    dff['timestamp'] = (
        dff['timestamp']
        .dt.tz_localize(None)
        + pd.Timedelta(hours=5, minutes=30)
    )

    # 2️⃣ now format that Series
    dff['timestamp'] = dff['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return {'Data':dff.to_dict(orient="records"),'table':None}

# @app.post("/Psar")
# async def update_margin_for_all_accounts(request: dict, current_user: dict = Depends(get_current_user)):

#     if not current_user or "role" not in current_user:
#         raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
  
#     index = request["symbol"]
#     indicators=request['indicators']
#     psar_settings = next((item for item in indicators if item["name"] == "Psar"), None)
#     custom_psar_af = psar_settings['setting'].get('af', 0.001) if psar_settings else 0.001
#     custom_psar_max_af = psar_settings['setting'].get('max-af', 0.001) if psar_settings else 0.001

#     today_9am = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 0))
#     dff = helperFunctions.ei.get_all_ticks_by_symbol(f'{index}SPOT')
#     last30kBefore9am = dff[dff['timestamp'] <= today_9am].tail(30000)
#     after9amToday=dff[dff['timestamp'] > today_9am]
#     combined_df = pd.concat([last30kBefore9am, after9amToday]).reset_index(drop=True)
#     combined_df = combined_df.sort_values(by='timestamp').reset_index(drop=True)
#     dff=combined_df

#     dff['timestamp'] = pd.to_datetime(dff['timestamp'])
#     mask_907 = (dff['timestamp'].dt.hour == 9) & (dff['timestamp'].dt.minute == 7)
#     df_907 =dff[mask_907].copy()
#     df_907['timestamp'] = df_907['timestamp'] + pd.Timedelta(minutes=3)
#     df_907=pd.DataFrame(df_907)
#     df_no_907 = dff[~mask_907].copy()
#     df_no_907['timestamp'] = pd.to_datetime(df_no_907['timestamp'])
#     df_no_907['group_end'] = df_no_907['timestamp'].dt.floor('5T') + pd.Timedelta(minutes=4)
#     bars5 = (
#         df_no_907
#         .groupby('group_end', as_index=False)
#         .agg(
#             o   = ('o',  'first'),
#             h   = ('h',  'max'),
#             l   = ('l',  'min'),
#             c   = ('c',  'last'),
#             v   = ('v',  'sum'),
#             oi  = ('oi', 'last'),
#         )
#         .rename(columns={'group_end':'timestamp'})
#     )
#     df_no_907=pd.DataFrame(bars5)
#     combined = pd.concat([df_907, df_no_907], ignore_index=True)
#     combined = combined.sort_values('timestamp').reset_index(drop=True)
#     dff=pd.DataFrame(combined)


#     # --------------------------------------------------------------------------- #
#     # 2)  PARABOLIC SAR (Wilder / TradingView) ---------------------------------- #
#     # --------------------------------------------------------------------------- #
#     def calculate_psar_tv(df: pd.DataFrame,
#                         max_af: float = 0.02,
#                         af: float = 0.20) -> pd.DataFrame:
#         """
#         Parabolic SAR that matches TradingView’s ta.sar().
#         Returns a copy of df with 'psar' and 'psar_trend' (1 up, -1 down).
#         """
#         data = df.resample('5min' ,on='timestamp').agg({'o':'first', 'h': 'max', 'l': 'min', 'c':'last'}).between_time("9:05", "15:30").dropna().reset_index()

#         max_acceleration = max_af
#         acceleration = af

#         # Prepare arrays
#         highs = data['h'].values
#         lows = data['l'].values
#         n = len(data)

#         psar = np.full(n, np.nan)  # Pre-allocate PSAR array
#         trend = np.ones(n, dtype=int)  # 1 for uptrend, -1 for downtrend
#         extreme_point = np.zeros(n)
#         acceleration_factor = np.full(n, acceleration)

#         # Initial conditions
#         psar[0] = highs[0]  # Start with the high as the initial PSAR
#         extreme_point[0] = highs[0]

#         # Iterative logic using a vectorized approach
#         for i in range(1, n):
#             # Calculate PSAR
#             psar[i] = psar[i - 1] + acceleration_factor[i - 1] * (extreme_point[i - 1] - psar[i - 1])

#             if trend[i - 1] == 1:  # Uptrend
#                 # Update extreme point for uptrend
#                 extreme_point[i] = max(extreme_point[i - 1], highs[i])
#                 # Check for trend reversal
#                 if lows[i] < psar[i]:
#                     trend[i] = -1
#                     psar[i] = extreme_point[i - 1]
#                     extreme_point[i] = lows[i]
#                     acceleration_factor[i] = acceleration
#                 else:
#                     trend[i] = 1
#                     acceleration_factor[i] = min(acceleration_factor[i - 1] + acceleration, max_acceleration)
#             else:  # Downtrend
#                 # Update extreme point for downtrend
#                 extreme_point[i] = min(extreme_point[i - 1], lows[i])
#                 # Check for trend reversal
#                 if highs[i] > psar[i]:
#                     trend[i] = 1
#                     psar[i] = extreme_point[i - 1]
#                     extreme_point[i] = highs[i]
#                     acceleration_factor[i] = acceleration
#                 else:
#                     trend[i] = -1
#                     acceleration_factor[i] = min(acceleration_factor[i - 1] + acceleration, max_acceleration)

#         # Convert PSAR to DataFrame and return the last value
#         psar_df_opt = pd.DataFrame(psar, index=data.index)
#         return psar_df_opt

#     psar_systems = [
#         {"name":"custom",  "af": 0.001,  "max_af":0.001},
#         {"name": "psar1",  "af": 0.001,  "max_af": 0.001},
#         {"name": "psar2",  "af": 0.0015, "max_af": 0.0015},
#         {"name": "psar3",  "af": 0.002,  "max_af": 0.002},
#         {"name": "psar4",  "af": 0.0025, "max_af": 0.0025},
#         {"name": "psar5",  "af": 0.003,  "max_af": 0.003},
#         {"name": "psar6",  "af": 0.0035, "max_af": 0.0035},
#         {"name": "psar7",  "af": 0.004,  "max_af": 0.004},
#         {"name": "psar8",  "af": 0.0045, "max_af": 0.0045},
#         {"name": "psar9",  "af": 0.005,  "max_af": 0.005},
#         {"name": "psar10", "af": 0.01,   "max_af": 0.01},
#         {"name": "psar11", "af": 0.015,  "max_af": 0.015},
#         {"name": "psar12", "af": 0.02,   "max_af": 0.02},
#         {"name": "psar13", "af": 0.025,  "max_af": 0.025},
#         {"name":"custom",'af':custom_psar_af,"max_af":custom_psar_max_af}
#     ]


#     bars5 = dff


#     for psarSystem in psar_systems:
#         calculatedSystemPsarValues=calculate_psar_tv(bars5, max_af=psarSystem['af'], af=psarSystem['max_af'])
#         bars5[psarSystem['name']]=calculatedSystemPsarValues
#     bars5.drop(columns=['v', 'oi'], errors='ignore', inplace=True)
#     # 1️⃣ remove tz and add the offset
#     bars5['timestamp'] = (
#         bars5['timestamp']
#         .dt.tz_localize(None)
#         + pd.Timedelta(hours=5, minutes=30)
#     )

#     # 2️⃣ now format that Series
#     bars5['timestamp'] = bars5['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
#     return {'Data':bars5.to_dict(orient="records"),'table':None}


    # # 1) Helper function to resample data just once
    # def resample_data(timeframe, futprice):
    #     """
    #     Returns a resampled DataFrame using the specified timeframe, 
    #     filtering for market hours (9:05 - 15:30).
    #     """
    #     data = futprice.copy()

    #     # If daily or multi-day timeframe, do a different approach
    #     if timeframe in ['D', '2D', 'M', 'MONTH']:
    #         mask = (
    #             (data['timestamp'].dt.time >= pd.to_datetime('9:05').time()) &
    #             (data['timestamp'].dt.time <= pd.to_datetime('15:30').time())
    #         )
    #         data = data[mask]

    #         data = data.resample(timeframe, on='timestamp').agg({
    #             'o': 'first',
    #             'h': 'max',
    #             'l': 'min',
    #             'c': 'last'
    #         }).dropna().reset_index()
    #     else:
    #         # For minute-based timeframes
    #         data = data.resample(timeframe, on='timestamp').agg({
    #             'o': 'first',
    #             'h': 'max',
    #             'l': 'min',
    #             'c': 'last'
    #         }).between_time("9:05", "15:30").dropna().reset_index()

    #     return data

    # # 2) PSAR calculation on an *already-resampled* DataFrame
    # def calculate_psar(df, af, max_af):
    #     """
    #     Expects `df` to have columns: ['timestamp', 'o', 'h', 'l', 'c'].
    #     Returns a NumPy array (or pd.Series) of PSAR values.
    #     """
    #     highs = df['h'].values
    #     lows = df['l'].values
    #     n = len(df)

    #     # Arrays to hold intermediate and final results
    #     psar = np.full(n, np.nan)
    #     trend = np.ones(n, dtype=int)
    #     extreme_point = np.zeros(n)
    #     acceleration_factor = np.full(n, af)

    #     # Initialize first row
    #     psar[0] = highs[0]
    #     extreme_point[0] = highs[0]

    #     for i in range(1, n):
    #         # The generic PSAR update
    #         psar[i] = psar[i - 1] + acceleration_factor[i - 1] * (extreme_point[i - 1] - psar[i - 1])

    #         if trend[i - 1] == 1:
    #             # Uptrend
    #             extreme_point[i] = max(extreme_point[i - 1], highs[i])
    #             if lows[i] < psar[i]:
    #                 # Switch to downtrend
    #                 trend[i] = -1
    #                 psar[i] = extreme_point[i - 1]
    #                 extreme_point[i] = lows[i]
    #                 acceleration_factor[i] = af
    #             else:
    #                 trend[i] = 1
    #                 acceleration_factor[i] = min(acceleration_factor[i - 1] + af, max_af)
    #         else:
    #             # Downtrend
    #             extreme_point[i] = min(extreme_point[i - 1], lows[i])
    #             if highs[i] > psar[i]:
    #                 # Switch to uptrend
    #                 trend[i] = 1
    #                 psar[i] = extreme_point[i - 1]
    #                 extreme_point[i] = highs[i]
    #                 acceleration_factor[i] = af
    #             else:
    #                 trend[i] = -1
    #                 acceleration_factor[i] = min(acceleration_factor[i - 1] + af, max_af)

    #     return psar

    # # 3) Parse the request
    # index = request["symbol"]
    # time_map = {
    #     '1m': '1min',
    #     '5m': '5min',
    #     '10m': '10min',
    #     '15m': '15min',
    #     '30m': '30min',
    #     '1h': '60min',
    #     '1d': 'D',
    # }
    # timeframe = time_map[request["timeframe"]]

    # # This is your provided PSAR systems list (you could define it here or outside)
    # psar_systems = [
    #     {"name":"custom",  "af": 0.001,  "max_af":0.0001},
    #     {"name": "psar1",  "af": 0.001,  "max_af": 0.001},
    #     {"name": "psar2",  "af": 0.0015, "max_af": 0.0015},
    #     {"name": "psar3",  "af": 0.002,  "max_af": 0.002},
    #     {"name": "psar4",  "af": 0.0025, "max_af": 0.0025},
    #     {"name": "psar5",  "af": 0.003,  "max_af": 0.003},
    #     {"name": "psar6",  "af": 0.0035, "max_af": 0.0035},
    #     {"name": "psar7",  "af": 0.004,  "max_af": 0.004},
    #     {"name": "psar8",  "af": 0.0045, "max_af": 0.0045},
    #     {"name": "psar9",  "af": 0.005,  "max_af": 0.005},
    #     {"name": "psar10", "af": 0.01,   "max_af": 0.01},
    #     {"name": "psar11", "af": 0.015,  "max_af": 0.015},
    #     {"name": "psar12", "af": 0.02,   "max_af": 0.02},
    #     {"name": "psar13", "af": 0.025,  "max_af": 0.025},
    # ]

    # indicators = request['indicators']
    # psar_setting = None
    # ma_setting = None
    # for indicator in indicators:
    #     if indicator['name'] == 'Psar':
    #         psar_setting = indicator['setting']
    #     if indicator['name'] == 'MA':
    #         ma_setting = indicator['setting']

    # # 4) Get the raw ticks from your helper
    # today_9am = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 0))
    # dff = helperFunctions.ei.get_all_ticks_by_symbol(f'{index}SPOT')
    # last30kBefore9am = dff[dff['timestamp'] <= today_9am].tail(30000)
    # after9amToday=dff[dff['timestamp'] > today_9am]
    # combined_df = pd.concat([last30kBefore9am, after9amToday]).reset_index(drop=True)
    # combined_df = combined_df.sort_values(by='timestamp').reset_index(drop=True)
    # dff=combined_df

    # # 5) Resample the data once
    # df_resampled = resample_data(timeframe, dff)

    # # If we need a moving average, do it now.
    # if ma_setting is not None:
    #     ma_period = ma_setting.get("period", -1)
    #     if ma_period != -1:
    #         df_resampled["ma"] = df_resampled["c"].rolling(window=ma_period).mean()

    # # 6) For each system, compute the psar array and store in a new column
    # for system in psar_systems:
    #     col_name = system["name"]  # e.g. "psar1", "psar2", ...
    #     af = system["af"]
    #     max_af = system["max_af"]

    #     # If "af" == -1 or "max_af" == -1, skip or handle default logic:
    #     if af == -1 and max_af == -1:
    #         # user asked to skip PSAR calculation
    #         df_resampled[col_name] = np.nan
    #     else:
    #         psar_values = calculate_psar(df_resampled, af, max_af)
    #         df_resampled[col_name] = psar_values

    # # Drop any row with all-NaN columns (if that happens after resampling)
    # df_resampled = df_resampled.dropna(subset=['o', 'h', 'l', 'c'])

    # # 7) Convert 'timestamp' to datetime if not already
    # df_resampled["timestamp"] = pd.to_datetime(df_resampled["timestamp"])

    # # SHIFT TIMEZONE if needed
    # df_resampled['timestamp'] = df_resampled['timestamp'] + pd.Timedelta(hours=5, minutes=30)

    # # 8) Return the entire DataFrame (with all psar columns) as JSON
    # df_resampled.replace([np.inf, -np.inf], np.nan, inplace=True)
    # df_resampled.dropna(axis=0, how="any", inplace=True)  # Removes rows containing NaN

    # psarmap={}
    # for psarsystem in psar_systems:
    #     psarmap[psarsystem['name']]={}
    
    # for index, row in df_resampled.iterrows():
    #     for psarsystem,a in psarmap.items():
    #         status=0 if (row[psarsystem]>row['c']) else 1
    #         if len(a.keys())==0:
    #             psarmap[psarsystem]={'status':status,'last':row['timestamp']}
    #         else:
    #             prev_status=psarmap[psarsystem]['status']
    #             if status!=prev_status:
    #                 psarmap[psarsystem]={'status':status,'last':row['timestamp']}
    # psarmap
    # psartable=[]
    # for key,value in psarmap.items():
    #     psartable.append({'System':key,'Direction':value['status'],'DateTime':value['last'].strftime('%Y-%m-%d %H:%M:%S')})          


    # return {'Data':df_resampled.to_dict(orient="records"),'table':psartable}




@app.get('/getclientDetails')
async def get_margin_data(current_user: dict = Depends(admin_required)):

    return {'clients': list(helperFunctions.clients.keys())}

@app.get('/DownloadBrokerPositionMismatch')
async def DownloadBrokerPositionMismatch(current_user: dict = Depends(admin_required)):

    feature_val=Feature_Reverse_Map['brokerpositionmismatch']
    if feature_val not in current_user['features'] :
       raise HTTPException(status_code=403, detail="Not authorized to view users")

    try:
        df_result=r.get('broker_position_mismatch')
        df_data = df_result.to_dict('records')
            
        return {
            "message": "Margin updated for all accounts successfully",
            "dataframe": {
                "data": df_data,
                "columns": df_result.columns.tolist()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update margins: {str(e)}"
        )


# def get_signalbook_data():
#     today = pd.Timestamp.today().date()
#     trades_list = r.lrange('all_trades', 0, -1)
#     signal_tradebook = pd.DataFrame(trades_list)
#     # signal_tradebook = signal_tradebook[signal_tradebook['timestamp'].dt.date == today]
#     signal_tradebook = signal_tradebook.sort_values(by='timestamp', ascending=False)
#     signal_tradebook = signal_tradebook.fillna('').infer_objects(copy=False)
#     signal_tradebook['time_diff'] = signal_tradebook['system_timestamp'] - signal_tradebook['timestamp']

#     # Format time_diff as total seconds with milliseconds
#     # Subtract 60 seconds if time_diff is above 60 seconds
#     signal_tradebook['time_diff'] = signal_tradebook['time_diff'].apply(
#         lambda x: f"{(x.total_seconds() - 60):.3f}" if x.total_seconds() > 60 else f"{x.total_seconds():.3f}"
#     )
#     # timestamp_column_names = signal_tradebook.select_dtypes(include=['datetime64[ns]']).columns
#     timestamp_column_names = signal_tradebook.columns
#     # Convert each timestamp column to string
#     for column in timestamp_column_names:
#         signal_tradebook[column] = signal_tradebook[column].astype(str)   

#     # signal_tradebook['quantity']=signal_tradebook['quantity'].astype(str)   
#     return {
#        "table_data" :signal_tradebook.to_dict(orient='records'),
#        "time":get_time()
#     }



@app.get('/get_open_trades')
async def get_open_trades(current_user: dict = Depends(admin_required)):

    try:
        trades_list = r.lrange( 'open_trades')
        open_trade = pd.DataFrame(trades_list)
        open_trade = open_trade.sort_values(by='timestamp', ascending=False)
        open_trade = open_trade.fillna('').infer_objects(copy=False)
        open_trade['time_diff'] = open_trade['system_timestamp'] - open_trade['timestamp']
        timestamp_column_names = open_trade.select_dtypes(include=['datetime64[ns]']).columns
        timestamp_column_names = open_trade.columns
        for column in timestamp_column_names:
            open_trade[column] = open_trade[column].astype(str)   
        open_trade['quantity']=open_trade['quantity'].astype(str)     
        return open_trade.to_dict(orient='records')
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update margins: {str(e)}"
        )
    



@app.get('/getuserSlippage')
async def get_UserSlippage(current_user: dict = Depends(get_current_user)):

    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")

    try:
        folder_path = Path("/root/algo/testing/fund summary/23-04-2025/")
        map = {}

        for file_path in folder_path.glob("*.xlsx"):  # Iterate only Excel files
            df = pd.read_excel(file_path)
            name = file_path.name.split('.')[0]  # Extract filename without extension
            for index, row in df.iterrows():
                date_1=row['Date'].date()
                if date_1 not in map:
                    map[date_1] = {}
                # map[date_1][name] = row['Weighted Avg Slippage']  # Store value
                map[date_1][f'{name}weight'] = row['Weighted Avg Slippage']  # Store value
                map[date_1][name] = row['Slippage Percentage']

        df_result = pd.DataFrame(map).T 
        df_result = df_result.reset_index().rename(columns={'index': 'Date'})
        df_result = df_result.fillna(0)
        return df_result.to_dict(orient='records')
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update margins: {str(e)}"
        )





@app.get('/DownloadALLBrokerPositionMismatch')
async def DownloadALLBrokerPositionMismatch(current_user: dict = Depends(admin_required)):

    feature_val=Feature_Reverse_Map['brokerpositionmismatch']
    if feature_val not in current_user['features'] :
       raise HTTPException(status_code=403, detail="Not authorized to view users")
    
    try:
       return helperFunctions.make_broker_position_mismatch_new_data() 
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update margins: {str(e)}"
        )


    

@app.post("/UpdateBrokerPositionMismatch")
async def UpdateBrokerPositionMismatch(
    file: UploadFile = File(...), 
    current_user: dict = Depends(admin_required)
):

    feature_val=Feature_Reverse_Map['brokerpositionmismatch']
    if feature_val not in current_user['features'] :
       raise HTTPException(status_code=403, detail="Not authorized to view users")

    try:
        # Read the content of the uploaded file
        contents = await file.read()
        df_result = pd.read_excel(io.BytesIO(contents))
        # Print the columns for debugging
        print("Columns in uploaded file:", df_result.columns.tolist())

        # Validate that 'Symbol' column exists
        if 'Symbol' not in df_result.columns:
            raise HTTPException(
                status_code=400,
                detail="Missing required 'Symbol' column. Please ensure your file has this column."
            )

        try:
            r.set('broker_position_mismatch', df_result)
            return {
                "message": "Broker position mismatch data updated successfully",
               
            }
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing data: {str(e)}"
            )
            
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty"
        )
    except pd.errors.ParserError:
        raise HTTPException(
            status_code=400,
            detail="Error parsing the file. Please ensure it's a valid CSV or Excel file"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update broker position mismatch: {str(e)}"
        )





@app.post("/uservartable")
async def user_var_table(request: dict, current_user: dict = Depends(get_current_user)):

    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")

    compute_live_strategies=helperFunctions.compute_live_strategies()
    return helperFunctions.give_var_table(request,compute_live_strategies,10)







@app.post("/payoffchart")
async def user_var_table(request: dict, current_user: dict = Depends(get_current_user)):

    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    percentage=request['percentage']
    compute_live_strategies=helperFunctions.compute_live_strategies()
    combined_accounts=[]
    strategies=request['strategies']
    for client in request['clients']:
        combined_accounts.append(helperFunctions.give_var_table({"client":client},compute_live_strategies,percentage))
    
    combined = helperFunctions.combine_by_user(combined_accounts)
    changed_combined=[]
    for var in combined:
        upside_obj={'Percentage':var['User'],'Value':0}
        downside_obj={'Percentage':('-'+var['User']),'Value':0}
        for key,value in var.items():
            if key[-1] != '%':
                down=False
                strat_name=helperFunctions.strip_side(key,"Upside")
                if strat_name==None:
                    down=True
                    strat_name=helperFunctions.strip_side(key,"Downside")
                if strat_name in strategies:
                    if not down:
                        upside_obj['Value']+=value
                    else :
                        downside_obj['Value']+=value
                elif strat_name=="" and "Normal" in strategies:
                    if key=='Upside':
                        upside_obj['Value']+=value
                    else :
                        downside_obj['Value']+=value
        changed_combined.append(upside_obj)
        changed_combined.append(downside_obj)
                
    changed_combined.sort(key=lambda d: float(d['Percentage'].rstrip('%')))
    return changed_combined


@app.post('/uservarcalculations')
async def uservalcalculations(payload: dict, current_user: dict = Depends(get_current_user)):
    percentage = payload.get("percentage")
    print("percentage is:",percentage)
    if percentage is None:
        raise HTTPException(status_code=400, detail="Percentage not provided")
    # Ensure the user is valid (as you already do)
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    a,_=helperFunctions.get_uservarcalculations(percentage)
    return a

    



@app.post('/elmcalculator')
async def elmcalculator(payload: dict, current_user: dict = Depends(get_current_user)):

    percentage = payload.get("percentage")
    if percentage is None:
        raise HTTPException(status_code=400, detail="Percentage not provided")
    # Ensure the user is valid (as you already do)
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")

    usermap = {}
    valid_index=['BANKNIFTY' , 'NIFTY' , 'FINNIFTY' , 'BANKNIFTY' , 'SENSEX']
    for client,value in helperFunctions.clients.items():
        if helperFunctions.active_clients[client]:
            usermap[client]={}
            for basket in valid_index:
                usermap[client][f'{basket} ELM']=0

    arr=[]
    for key,value in helperFunctions.compute_live_strategies().items():
        for symbol,positions in value['positions'].items():
            action=value['action'][symbol]
            for user,qt in positions.items():
                if user not in usermap:
                    continue
                    # usermap[user]={}
                    # for basket in valid_index:
                    #     usermap[user][f'{basket} ELM']=0
            
                index,strike,tradetype=helperFunctions.give_strike(symbol)
                if index not in helperFunctions.valid_index:
                    continue
                if action == 'SELL':
                    usermap[user][f'{index} ELM']+=(strike*(percentage/100))*abs(qt)
            

    pf_values=r.hgetall('user_pf_value')
    arr = []
    for key, value in usermap.items():
        new_record = {'User': key}
        usernewmap={}
        for side,pnl in value.items():
            usernewmap[side]=value[side]
            usernewmap[f'{side}%']=round(((pnl*100)/pf_values[helperFunctions.userNameToUserIdMap[key]]),2)
        new_record.update(usernewmap)
        arr.append(new_record)

    return arr


@app.get('/getdailylogs')
async def getdailylogs(current_user: dict = Depends(admin_required)):
    # Validate user
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    

    feature_val=Feature_Reverse_Map['dailylogs']
    if feature_val not in current_user['features'] :
       raise HTTPException(status_code=403, detail="Not authorized to view users")
    
    df2 = pd.read_excel('Dashboard_Logs.xlsx')
    # Reset the index and rename the new index column to 'id'
    df2 = df2.reset_index().rename(columns={'index': 'id'})
    records = df2.to_dict('records')
    
    # Convert the "Message" field to a dict if it is a string
    for record in records:
        message_value = record.get("Message")
        if isinstance(message_value, str):
            try:
                record["Message"] = ast.literal_eval(message_value)
            except Exception as e:
                # Optionally log the error and leave Message as string if conversion fails
                print(f"Error parsing Message field: {e}")
    
    return records

@app.get('/getdailylogsdetails')
async def getdailylogsdetails(current_user: dict = Depends(admin_required)):
    # Validate user
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    

    feature_val=Feature_Reverse_Map['dailylogs']
    if feature_val not in current_user['features'] :
       raise HTTPException(status_code=403, detail="Not authorized to view users")
    
    return r.hgetall('dashboardlogdetails')
    


    
@app.post('/getspecificlog')
async def getSpecificLog(payload: dict, current_user: dict = Depends(admin_required)):
    
    feature_val=Feature_Reverse_Map['dailylogs']
    if feature_val not in current_user['features']:
       raise HTTPException(status_code=403, detail="Not authorized to view users")
    
    raw_index = payload.get("index")
    if raw_index is None:
        raise HTTPException(status_code=400, detail="Index not provided")
    
    try:
        index = int(raw_index)
    except Exception:
        raise HTTPException(status_code=400, detail="Index must be an integer")

    # Ensure the user is valid
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    
    df2 = pd.read_excel('Dashboard_Logs.xlsx')
    
    try:
        row = df2.iloc[index].to_dict()  # Convert the Series to a dict (object)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching log at index {index}: {e}")
    
    # Convert the Message field from string to an object if it's a string
    if "Message" in row and isinstance(row["Message"], str):
        try:
            row["Message"] = ast.literal_eval(row["Message"])
        except Exception as e:
            # Optionally log the error and keep the Message as is
            print("Error parsing Message field:", e)

    return row



@app.post('/appendlog')
async def append_log(payload: dict, current_user: dict = Depends(admin_required)):
    # Validate user
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    
    feature_val=Feature_Reverse_Map['dailylogs']
    if feature_val not in current_user['features'] :
       raise HTTPException(status_code=403, detail="Not authorized to view users")
    



    # Extract and format date correctly
    date_value = payload.get("Date")
    if date_value:
        try:
            # Parse the date string (ISO format) and reformat it
            date_obj = datetime.datetime.fromisoformat(date_value)
            date_value = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Date format provided: {e}")
    else:
        # Use current datetime if no date provided
        date_value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Extract other payload details
    category = payload.get("Category")
    subcategory = payload.get("SubCategory")
    message = payload.get("Message")

    if category is None or subcategory is None or message is None:
        raise HTTPException(status_code=400, detail=" 'Category' , 'SubCategory' and 'Message' must be provided")
    
    database_category=r.hget('dashboardlogdetails','Category')
    database_subcategory=r.hget('dashboardlogdetails','Sub Category')
    if category not in database_category:
        database_category.append(category)
    if subcategory not in database_subcategory:
        database_subcategory.append(subcategory)

    r.hset('dashboardlogdetails','Sub Category',database_subcategory)
    r.hset('dashboardlogdetails','Category',database_category)

    # Create a new row
    new_row = {
        "Date": date_value,
        "Category": category,
        "SubCategory":subcategory,
        "Message": message,
        "Created By":current_user['username'],
        "Created Time":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    }
    print(new_row)
    print(current_user['username'])

    # Read or create Excel file
    try:
        df = pd.read_excel('Dashboard_Logs.xlsx')
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Date", "Category","SubCategory" "Message","Created By","Created Time"])

    # Append and save
    new_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_excel('Dashboard_Logs.xlsx', index=False)

    return {"detail": "Log appended successfully", "log": new_row}

@app.post('/updatelog')
async def updateLog(payload: dict, current_user: dict = Depends(admin_required)):
    # Validate user
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    
    feature_val=Feature_Reverse_Map['dailylogs']
    if feature_val not in current_user['features'] :
       raise HTTPException(status_code=403, detail="Not authorized to view users")


    if payload['totp_code'] != MARGIN_CHANGE_PASSWORD:
        raise HTTPException(status_code=400, detail="Password Incorrect!")
    
    # Extract and validate the index from the payload
    raw_index = payload.get("index")
    if raw_index is None:
        raise HTTPException(status_code=400, detail="Index not provided")
    try:
        index = int(raw_index)
    except Exception:
        raise HTTPException(status_code=400, detail="Index must be an integer")
    
    # Read the Excel file
    try:
        df = pd.read_excel('Dashboard_Logs.xlsx')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")
    
    # Validate index range
    if index < 0 or index >= len(df):
        raise HTTPException(status_code=400, detail=f"Invalid index. Must be between 0 and {len(df) - 1}")
    
    # Extract and format Date if provided; otherwise use current datetime
    date_value = payload.get("Date")
    if date_value:
        try:
            date_obj = datetime.datetime.fromisoformat(date_value)
            date_value = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Date format provided: {e}")
    else:
        date_value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Extract updated Category and Message
    category_value = payload.get("Category")
    sub_category_value=payload.get("SubCategory")
    message_value = payload.get("Message")
    if category_value is None or sub_category_value is None or message_value is None:
        raise HTTPException(status_code=400, detail="Both 'Category' and 'Message' must be provided")
    
    database_category=r.hget('dashboardlogdetails','Category')
    database_subcategory=r.hget('dashboardlogdetails','Sub Category')
    if category_value not in database_category:
        database_category.append(category_value)
    if sub_category_value not in database_subcategory:
        database_subcategory.append(sub_category_value)

    r.hset('dashboardlogdetails','Sub Category',database_subcategory)
    r.hset('dashboardlogdetails','Category',database_category)
    
    # Use .at for scalar assignment to update the row
    df.at[index, 'Date'] = date_value
    df.at[index, 'Category'] = category_value
    df.at[index,'SubCategory'] = sub_category_value
    df.at[index, 'Message'] = message_value
    df.at[index,'Created By']= current_user['username']
    df.at[index,'Created Time'] =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save the updated DataFrame back to the Excel file
    try:
        df.to_excel('Dashboard_Logs.xlsx', index=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving log file: {e}")
    
    # Retrieve the updated row and convert to dict
    updated_row = df.loc[index].to_dict()
    # Convert Message field to object if it's a string
    if isinstance(updated_row.get("Message"), str):
        try:
            updated_row["Message"] = ast.literal_eval(updated_row["Message"])
        except Exception as e:
            print(f"Error parsing Message field: {e}")
    
    return {"detail": "Log updated successfully", "log": updated_row}




@app.post('/deletelog')
async def deleteLog(payload: dict, current_user: dict = Depends(admin_required)):

    
    # Ensure the user is valid
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
        
    feature_val=Feature_Reverse_Map['dailylogs']
    if feature_val not in current_user['features']:
       raise HTTPException(status_code=403, detail="Not authorized to view users")

    
    raw_index = payload.get("index")

    if payload['totp_code'] != MARGIN_CHANGE_PASSWORD:
        raise HTTPException(status_code=400, detail="Password Incorrect!")
    
    # Validate index
    if raw_index is None:
        raise HTTPException(status_code=400, detail="Index not provided")
    
    try:
        index = int(raw_index)
    except Exception:
        raise HTTPException(status_code=400, detail="Index must be an integer")


    
    # Read the Excel file
    try:
        df2 = pd.read_excel('Dashboard_Logs.xlsx')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")



    # Validate index range
    if index < 0 or index >= len(df2):
        raise HTTPException(status_code=400, detail=f"Invalid index. Must be between 0 and {len(df2) - 1}")

    try:
        # Drop the specific row
        df2 = df2.drop(index)
        
        # Reset index to maintain continuity
        df2 = df2.reset_index(drop=True)
        
        # Save back to Excel
        df2.to_excel('Dashboard_Logs.xlsx', index=False)

            
        unique_categories = list(df2['Category'].unique())
        unique_subcategories = list(df2['SubCategory'].unique())

        r.hset('dashboardlogdetails','Sub Category',unique_subcategories)
        r.hset('dashboardlogdetails','Category', unique_categories)
        
        return {
            "status": "success", 
            "message": f"Log at index {index} deleted successfully",
            "remaining_logs": len(df2)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting log: {e}")


@app.post('/varsimulator')
async def varSimulator(payload: dict, current_user: dict = Depends(get_current_user)):

    
    # Ensure the user is valid
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    

    #Before 
    Upside=0
    Downside=0
    BrokerUpside = 0
    BrokerDownside = 0
    Upsideper = 0
    Downsideper = 0
    BrokerUpsideper = 0
    BrokerDownsideper = 0
    pf_sum=0
    index_quantities={}
    users_to_consider=[]

    for user_details in payload['users']:
        percentage = user_details['percentage']
        user=user_details['userId']
        baskets_want=user_details['baskets']

        user_id=helperFunctions.clients[user]['user_id']
        users_to_consider.append(user)
        data,index_quantities=helperFunctions.get_uservarcalculations(percentage)
        found_element = next((item for item in data if item["User"] == user), None)

        pf_value = r.hget('user_pf_value',user_id)
        temp_Upside,temp_Downside=helperFunctions.give_columns_sum(baskets_want,found_element)
        Upside+=temp_Upside
        Downside+=temp_Downside
        Manual_Upside=found_element['BrokerUpside']-found_element['Upside']
        Manual_Downside=found_element['BrokerDownside']-found_element['Downside']
        BrokerUpside+= temp_Upside+Manual_Upside
        BrokerDownside+= temp_Downside+Manual_Downside
        pf_sum+=pf_value


    Upsideper = round(((Upside * 100) / pf_sum), 2)
    Downsideper = round(((Downside * 100) / pf_sum), 2)
    BrokerUpsideper = round((( BrokerUpside * 100) /  pf_sum), 2)
    BrokerDownsideper = round(((BrokerDownside * 100) /  pf_sum), 2)


    trades=payload['trades']
    found_element_quantity=helperFunctions.give_quantity_map(payload['users'],index_quantities)
    new_found_element_quantity = copy.deepcopy(found_element_quantity)

    #For Calculating Custom Trades
    upcustomtrade=0
    downcustomtrade=0
    premium = 0

    upcustomtrade,downcustomtrade,premium = helperFunctions.give_trade_calc(trades,percentage,new_found_element_quantity)


    #After Adding New Trades
    newUpside = 0
    newDownside = 0
    newBrokerUpside = 0
    newBrokerDownside = 0
    newUpsideper = 0
    newDownsideper = 0
    newBrokerUpsideper = 0
    newBrokerDownsideper = 0

    newUpside=Upside +  upcustomtrade
    newDownside =  Downside +  downcustomtrade
    newBrokerUpside = BrokerUpside +   upcustomtrade
    newBrokerDownside= BrokerDownside +  downcustomtrade
    newUpsideper= round(((newUpside * 100) / pf_sum), 2)
    newDownsideper= round(((newDownside * 100) / pf_sum), 2)
    newBrokerUpsideper= round((( newBrokerUpside * 100) / pf_sum), 2)
    newBrokerDownsideper= round(((newBrokerDownside * 100) / pf_sum), 2)


    return{
        "TableOld":{
            "Upside": Upside,
            "Downside": Downside,
            "BrokerUpside": BrokerUpside,
            "BrokerDownside": BrokerDownside,
            "Upside%": Upsideper,
            "Downside%": Downsideper,
            "BrokerUpside%": BrokerUpsideper,
            "BrokerDownside%": BrokerDownsideper,
            
        },
        "TableNew": {
            "New_Upside": newUpside,
            "New_Downside": newDownside,
            "New_BrokerUpside": newBrokerUpside,
            "New_BrokerDownside": newBrokerDownside,
            "New_Upside%": newUpsideper,
            "New_Downside%": newDownsideper,
            "New_BrokerUpside%": newBrokerUpsideper,
            "New_BrokerDownside%": newBrokerDownsideper,
        },
        "Old Quantity" :found_element_quantity,
        'New_Quantity':new_found_element_quantity,
        'Price':premium
    }
    




def tell_type(atm, cur, opt_type):
    if cur == atm:
        return 'ATM'
    return 'ITM' if (opt_type == 'CE' and cur < atm) or (opt_type == 'PE' and cur > atm) else 'OTM'

def extract_strike(obj):
    _, strike, _ = helperFunctions.give_strike(obj["symbol"])
    return strike if strike is not None else 0


@app.get('/optionexpirydetails')
async def getdailylogsdetails(current_user: dict = Depends(get_current_user)):
    # Ensure the user is valid
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    
    def give_date(symbol):
        if symbol is None:
            return None 
        for i, char in enumerate(symbol):
            if char.isdigit():
                if symbol[:i] not in helperFunctions.valid_index:
                    return None
                return symbol[i:i+6]
        return None
    
    def parse_date(date_str):
        try:
            # Expecting date_str format: "YY-MM-DD"
            year, month, day = date_str.split('-')
            # Basic validation for month
            if int(month) > 12:
                return None
            return datetime.datetime(2000 + int(year), int(month), int(day))
        except Exception as e:
            print("Error parsing date:", e)
            return None

    def get_expiry_date(index, symbolTOexchange):
        filtered_keys = [k for k in symbolTOexchange if (k.endswith('CE') or k.endswith('PE')) and (k.startswith(index))]
        pattern = rf'^{re.escape(index)}\d{{6}}'
        filtered = [s for s in filtered_keys if re.match(pattern, s)]
        date_strings = set()
        for symbol in filtered:
            date = give_date(symbol)
            # Skip if give_date returns None
            if date is None:
                continue
            # Ensure we have exactly 6 digits
            if len(date) != 6:
                continue
            date_str = f'{date[:2]}-{date[2:4]}-{date[4:6]}'
            date_strings.add(date_str)
        return list(date_strings)

    # Assuming helperFunctions.symbolTOexchange exists
    symbolTOexchange = helperFunctions.symbolTOexchange

    # Filter out invalid dates by using a list comprehension
    nifty_dates = [d for d in get_expiry_date("NIFTY", symbolTOexchange) if parse_date(d) is not None]
    banknifty_dates = [d for d in get_expiry_date("BANKNIFTY", symbolTOexchange) if parse_date(d) is not None]
    sensex_dates = [d for d in get_expiry_date("SENSEX", symbolTOexchange) if parse_date(d) is not None]
    finnifty_dates = [d for d in get_expiry_date("FINNIFTY", symbolTOexchange) if parse_date(d) is not None]

    nifty = sorted(nifty_dates, key=parse_date)
    banknifty = sorted(banknifty_dates, key=parse_date)
    sensex = sorted(sensex_dates, key=parse_date)
    finnifty = sorted(finnifty_dates, key=parse_date)

    result_map = {
        "NIFTY": nifty,
        "BANKNIFTY": banknifty,
        "SENSEX": sensex,
        "FINNIFTY": finnifty,
        "BASKETS":r.lrange('all_baskets', 0, -1),
    }
    return result_map

    
    


@app.post('/optionchain')
async def optionchain(payload: dict, current_user: dict = Depends(get_current_user)):

    # Ensure the user is valid
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")

    atm_symbol_CE=helperFunctions.ei.find_symbol_by_moneyness(datetime.datetime.now().replace(second=0,microsecond=0),payload["index"],0,'CE',0)
    atm_symbol_PE=helperFunctions.ei.find_symbol_by_moneyness(datetime.datetime.now().replace(second=0,microsecond=0),payload["index"],0,'PE',0)
    date_str = payload["date"].replace("-", "")
    search_for=f'{payload["index"]}{date_str}'
    filtered_keys = [k for k in helperFunctions.symbolTOexchange if (k.endswith('CE') or k.endswith('PE')) and (k.startswith(search_for))]
    
    arr_CE=[]
    arr_PE=[]
    _,atm_strike_CE,_=helperFunctions.give_strike(atm_symbol_CE)
    _,atm_strike_PE,_=helperFunctions.give_strike(atm_symbol_PE)

    for symbol in filtered_keys:
        index_sym,current_strike,curr_type=helperFunctions.give_strike(symbol)
        if curr_type =='CE':
            arr_CE.append({
                'symbol':symbol,
                'ltp':r.get(f'ltp.{symbol}'),
                'moneyness':tell_type(atm_strike_CE ,current_strike,curr_type)})
        else:
            arr_PE.append({
            'symbol':symbol,
            'ltp':r.get(f'ltp.{symbol}'),
            'moneyness':tell_type(atm_strike_PE ,current_strike,curr_type)})


    sorted_data_CE = sorted(arr_CE, key=extract_strike)
    sorted_data_PE = sorted(arr_PE, key=extract_strike)

    return {'CE':sorted_data_CE,'PE':sorted_data_PE}



@app.post("/ivchart")
async def give_iv_underlying_chart(request: dict, current_user: dict = Depends(admin_required)):
    # Check authorization
   

    return helperFunctions.give_iv_underlying_chart(request['index'],request['year'],request['month'],request['day'])


@app.post('/fundsummary')
async def give_fund_summary(request:dict , current_user:dict = Depends(get_current_user)):
    # Ensure the user is valid
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    
    name=request['name']

    if  'account_percentages' in current_user:
        elem = next((item for item in current_user['account_percentages'] if item['name'] == name), None)
        print(elem['dateRanges'])
        return helperFunctions.get_client_fund_summary(name,['Date','Actual MTM','portfolio_value'],elem['dateRanges'])
    else:
        return helperFunctions.get_client_fund_summary(name,['Date','Actual MTM','portfolio_value'])


# Define your sidebar features with access levels
@app.get("/sidebar-features")
async def sidebar_features(current_user: dict = Depends(get_current_user)):
        # Ensure the user is valid
    if not current_user or "role" not in current_user:
        raise HTTPException(status_code=403, detail="Invalid user or authentication failed")
    role = current_user["role"]
    return {
        "role": role,
        "pages":r.hget("role_pages", role)
    }





@app.get("/getUsers")
async def sidebar_features(current_user: dict = Depends(admin_required)):

    clients_obj = [] 
    for client in helperFunctions.active_clients.keys():
        if helperFunctions.active_clients[client] == True:
            clients_obj.append({'username':client})
    
    return clients_obj
    

@app.post('/squareOffPositions')
async def squareOffPositions(request:dict , current_user:dict = Depends(super_admin_required)):
    
    #{'username': 'Deepti Parikh', 'first_password': 'h1', 'second_password': 'g2'}
    first_password=request['first_password']
    second_password =request['second_password']
    username=request['username']
    
    if first_password != "kill1" or second_password!= "kill2":
        raise HTTPException(status_code=400, detail="Password Incorrect!")

    #r.hset('sq_off_mode', username, True)
    return {
                "message": "Sqaure Off Successfully",

            }


@app.post('/marginUpdateCheckDetails')
async def marginUpdateCheckDetails(request:dict , current_user:dict = Depends(super_admin_required)):

    client=request['username']
    return r.hget('margin_update_check',client)


@app.post('/updateMarginSettings')
async def updateMarginSettings(request:dict , current_user:dict = Depends(super_admin_required)):

    client=request['username']
    strategies=request['strategies']
    return r.hset('margin_update_check',client,strategies)


@app.get("/userpnl")
async def sidebar_features(current_user: dict = Depends(get_current_user)):

    data=helperFunctions.get_client_fund_summary('Swan Prop Team')
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])

    # Define cutoff date
    cutoff_date = pd.to_datetime('2025-04-30')

    # Filter rows where Date <= cutoff_date
    filtered_df = df[df['Date'] >= cutoff_date].reset_index(drop=True)
    filtered_df

    user_obj=[
        {
            "username":"Abhinav",
            "percentage":0.5,
            "margin":864000
        },
        {
            "username":"Ashwin",
            "percentage":0.5,
            "margin":864000
        },
        {
            "username":"Darshana",
            "percentage":0.2,
            "margin":864000
        },
        {
            "username":"Nilesh",
            "percentage":0.1,
            "margin":864000
        },
        {
            "username":"Prahlad",
            "percentage":0.5,
            "margin":700000
        }
    ]
    # for idx, row in filtered_df.iterrows():
    #     for user in user_obj:
    #         pf=row['portfolio_value']
    #         exposure=user['percentage']*user['margin']*5
    #         per_cal=(exposure/pf)
    #         filtered_df.at[idx, f"{user['username']}"] = round(per_cal * row['Actual MTM'], 2)
    for idx, row in filtered_df.iterrows():
        for user in user_obj:
            pf = row['portfolio_value']
            exposure = user['percentage'] * user['margin'] * 5

            # Use 'Settlement Price' if it's not NA, else fall back to 'Actual MTM'
            mtm_value = row['Settlement Price'] if (pd.notna(row['Settlement Price']) and row['Settlement Price']!=0) else row['Actual MTM']
            
            per_cal = (exposure / pf)
            filtered_df.at[idx, f"{user['username']}"] = round(per_cal * mtm_value, 2)

    return filtered_df.to_dict(orient='records')


@app.get("/market-holidays")
async def market_holidays(current_user: dict = Depends(super_admin_required)):

    return r.get('market_holiday')
    


@app.post('/handle_market-holidays')
async def handleMarketHolidays(request:dict , current_user:dict = Depends(super_admin_required)):

    type=request['type']
    date_str=request['date']
 
    arr=r.get('market_holiday')
    if type=='add':
        dayname=request['dayname']
        arr.append({'date': date_str, 'day name': dayname})
        r.set('market_holiday',arr)
    else:
        arr= [h for h in arr if h['date'] != date_str]
        r.set('market_holiday',arr)
    return 

@app.post('/stratcharts')
async def stratCharts(request:dict , current_user:dict = Depends(get_current_user)):

    client=request['client']
    systemTagNeeded=request['systemTagNeeded']
    if client not in current_user.get('account_access', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Access denied", 
                    "message": f"You do not have access to client '{client}'."}
        )

    chartData,availableSystemTagList,availableSystemTagWithoutNumberList=helperFunctions.get_user_uid_live_data(client,systemTagNeeded)
    return {
        'chartData':chartData,
        'availableSystemTagList':availableSystemTagList,
        'availableSystemTagWithoutNumberList':availableSystemTagWithoutNumberList
    }

@app.post('/stratchartswithoutnumbers')
async def stratchartswithoutnumbers(request:dict , current_user:dict = Depends(get_current_user)):

    client=request['client']
    systemTagNeeded=request['systemTagNeeded']

    chartData=helperFunctions.get_user_systemTag_without_number_live_data(client,systemTagNeeded)
    return {
        'chartData':chartData
    }




if __name__ == "__main__":
    logger.info("Starting the FastAPI application")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")