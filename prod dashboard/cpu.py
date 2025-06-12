import psutil
import direct_redis
import asyncio
import datetime
import time

# Initialize the Redis connection
r = direct_redis.DirectRedis()

# Redis keys to store usage objects
redis_key_cpu = 'server:cpu_usage_log'
redis_key_ram = 'server:ram_usage_log'
redis_key_redis = 'server:redis_usage_log'

def get_ist_time():
    current_time = datetime.datetime.now()
    offset_time = current_time + datetime.timedelta(hours=5, minutes=30)
    return offset_time

def get_local_time():
    return datetime.datetime.now()

def bytes_to_gb(bytes_value):
    return bytes_value / (1024 ** 3)

def is_time_to_run():
    current_time = get_local_time()
    start_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
    return start_time <= current_time <= end_time

def delete_redis_keys():
    r.delete(redis_key_cpu, redis_key_ram, redis_key_redis)
    print("Deleted existing Redis keys.")

async def get_and_store_cpu_usage():
    while is_time_to_run():
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_usage_object = {
            'time': int(get_ist_time().timestamp()),
            'value': cpu_usage
        }
        r.rpush(redis_key_cpu, cpu_usage_object)
        print(f"CPU usage: {cpu_usage}% (Local time: {get_local_time().strftime('%H:%M:%S')})")
        await asyncio.sleep(1)

async def get_and_store_ram_usage():
    while is_time_to_run():
        ram_usage = psutil.virtual_memory().percent
        ram_usage_object = {
            'time': int(get_ist_time().timestamp()),
            'value': ram_usage
        }
        r.rpush(redis_key_ram, ram_usage_object)
        print(f"RAM usage: {ram_usage}% (Local time: {get_local_time().strftime('%H:%M:%S')})")
        await asyncio.sleep(1)

async def get_and_store_redis_info():
    while is_time_to_run():
        redis_info = r.info()
        
        used_memory_gb = bytes_to_gb(redis_info.get('used_memory', 0))
        used_memory_peak_gb = bytes_to_gb(redis_info.get('used_memory_peak', 0))
        total_system_memory_gb = bytes_to_gb(redis_info.get('total_system_memory', 0))
        
        if total_system_memory_gb > 0:
            redis_memory_percent = (used_memory_gb / total_system_memory_gb) * 100
        else:
            redis_memory_percent = 0
        
        redis_usage_object = {
            'time': int(get_ist_time().timestamp()),
            'used_memory_gb': used_memory_gb,
            'used_memory_peak_gb': used_memory_peak_gb,
            'total_system_memory_gb': total_system_memory_gb,
            'memory_percent': redis_memory_percent,
            "available_memory_gb": (total_system_memory_gb - used_memory_gb)
        }
        
        r.rpush(redis_key_redis, redis_usage_object)
        
        local_time = get_local_time().strftime('%H:%M:%S')
        print(f"Redis info (Local time: {local_time}):")
        print(f"  Memory usage: {redis_memory_percent:.2f}%")
        print(f"  Used memory: {used_memory_gb:.2f} GB")
        print(f"  Peak used memory: {used_memory_peak_gb:.2f} GB")
        print(f"  Total system memory: {total_system_memory_gb:.2f} GB")
        print(f"  Available Redis memory: {(total_system_memory_gb - used_memory_gb):.2f} GB")
        
        await asyncio.sleep(5)

async def main():
    while True:
        current_time = get_local_time()
        if is_time_to_run():
            print(f"Starting monitoring at local time: {current_time}")
            delete_redis_keys()
            await asyncio.gather(
                get_and_store_cpu_usage(),
                get_and_store_ram_usage(),
                get_and_store_redis_info()
            )
        else:
            print(f"Outside operating hours. Waiting until 9:00 AM. Current local time: {current_time}")
            # Calculate time until 9:00 AM
            next_run = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
            if next_run <= current_time:
                next_run += datetime.timedelta(days=1)
            wait_seconds = (next_run - current_time).total_seconds()
            await asyncio.sleep(wait_seconds)

if __name__ == "__main__":
    asyncio.run(main())