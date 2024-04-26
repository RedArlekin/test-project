import asyncio
import random
from datetime import datetime

async def send_ping(writer):
    global REQUEST_COUNT
    try:
        while True:
            await asyncio.sleep(random.uniform(0.3, 3))
            message = f"[{REQUEST_COUNT}] PING"
            writer.write(message.encode() + b'\n')
            await writer.drain()
            log_message(datetime.now(), message)
            REQUEST_COUNT += 1  # Увеличиваем счетчик запросов
    except asyncio.CancelledError:
        print("Client connection cancelled.")

async def receive_pong(reader):
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()
            log_message(datetime.now(), "", message)
    except asyncio.CancelledError:
        print("Client connection cancelled.")

def log_message(timestamp, request, response=False, timeout=False):
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = f"{timestamp_str}; {request}; {response}\n" if not timeout else f"{timestamp}; {request}; {timeout}\n"
    with open("client1_log.txt", "a") as log_file:
        log_file.write(log_entry)

async def main():
    global REQUEST_COUNT
    REQUEST_COUNT = 0  # Инициализируем счетчик запросов
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    tasks = [
        asyncio.create_task(send_ping(writer)),
        asyncio.create_task(receive_pong(reader))
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())
