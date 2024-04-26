import asyncio
import random
from datetime import datetime

async def send_keepalive(clients):
    try:
        while True:
            await asyncio.sleep(5)
            for client_id, writer in clients.items():
                response = f"[{RESPONSE_COUNT}] keepalive"
                writer.write(response.encode() + b'\n')
                await writer.drain()
                log_message(datetime.now(), "", response)
    except asyncio.CancelledError:
        print("Keepalive task cancelled.")

async def handle_client(reader, writer, clients):
    client_id = len(clients) + 1
    clients[client_id] = writer
    print(f'Client {client_id} connected.')

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()
            print(f"Received from client {client_id}: {message}")

            if random.random() < 0.1:
                print("Message ignored.")
                log_message(datetime.now(), "", message, "(проигнорировано)")
                continue

            delay = random.randint(100, 1000) / 1000
            await asyncio.sleep(delay)

            response = f"[{RESPONSE_COUNT}] PONG ({message}) ({client_id})"
            log_message(datetime.now(), message, response)
            writer.write(response.encode() + b'\n')
            await writer.drain()

    except asyncio.CancelledError:
        print(f'Client {client_id} connection cancelled.')
    finally:
        print(f'Client {client_id} disconnected.')
        clients.pop(client_id, None)

def log_message(timestamp, request, response=False, timeout=False):
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = f"{timestamp_str}; {request}; {response}\n" if not timeout else f"{timestamp}; {request}; {timeout}\n"
    with open("server_log.txt", "a") as log_file:
        log_file.write(log_entry)

async def main():
    clients = {}
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, clients),
        '127.0.0.1', 8888
    )

    async with server:
        keepalive_task = asyncio.create_task(send_keepalive(clients))

        await asyncio.gather(
            server.serve_forever(),
            keepalive_task
        )

CLIENTS = set()
RESPONSE_COUNT = 0

asyncio.run(main())
