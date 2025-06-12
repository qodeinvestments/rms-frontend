import time
import direct_redis

# Connect to Redis
redis_client = direct_redis.DirectRedis()

# KeyDB log file path
log_file_path = '/var/log/keydb/keydb-server.log'


# Redis stream key
stream_key = 'keydb_logs'

def parse_log_line(line):
    if ('*' not in line and '#' not in line):
        return None
    parts = line.strip().split(' ', 2)
    if len(parts) < 3:
        return None
    
    split_arr = line.split(" ", 1)
    main_data=split_arr[1].split("*",1)
    if '#' in line:
        main_data=split_arr[1].split("#",1)
    time=main_data[0]
    message=main_data[1]
    
    return {
        "timestamp":time,
        'message': message
    }

def add_to_stream(parsed_line):
    if parsed_line:
        # Add to Redis stream
        redis_client.xadd(stream_key, parsed_line)
        print(f"Added to stream: {parsed_line}")

def read_existing_logs(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            parsed_line = parse_log_line(line)
            if parsed_line is not None:
                add_to_stream(parsed_line)

def tail_file(file_path):
    with open(file_path, 'r') as file:
        file.seek(0, 2)  # Go to the end of the file
        while True:
            line = file.readline()
            if not line:
                time.sleep(1)  # Sleep briefly
            yield line

def main():
    # First, read and add all existing logs
    redis_client.xtrim(stream_key, maxlen=0)
    print("Reading existing logs...")
    read_existing_logs(log_file_path)
    print("Finished reading existing logs. Now tailing the file...")

    # Then start tailing the file for new logs
    for line in tail_file(log_file_path):
        parsed_line = parse_log_line(line)
        if parsed_line is not None:
            add_to_stream(parsed_line)

if __name__ == "__main__":
    
    main()
    print("finished the code")