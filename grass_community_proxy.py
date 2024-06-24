import argparse
import asyncio
import random
import signal
import ssl
import json
import time
import uuid
from loguru import logger
from websockets_proxy import Proxy, proxy_connect
import os
from dotenv import load_dotenv

load_dotenv()

grass_userid = os.getenv("GRASS_USERID")

# Async function to connect to WebSocket server
async def connect_to_wss(http_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, http_proxy))
    logger.info(device_id)
    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            uri = "wss://proxy.wynd.network:4650/"
            server_hostname = "proxy.wynd.network"
            proxy = Proxy.from_url(http_proxy)
            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                     extra_headers=custom_headers) as websocket:
                async def send_ping():
                    while True:
                        send_message = json.dumps(
                            {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                        logger.debug(send_message)
                        await websocket.send(send_message)
                        await asyncio.sleep(20)

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(message)
                    if message.get("action") == "AUTH":
                        auth_response = {
                            "id": message["id"],
                            "origin_action": "AUTH",
                            "result": {
                                "browser_id": device_id,
                                "user_id": user_id,
                                "user_agent": custom_headers['User-Agent'],
                                "timestamp": int(time.time()),
                                "device_type": "extension",
                                "extension_id": "lkbnfiajjmbhnfledhphioinpickokdi",
                                "version": "4.20.2"
                            }
                        }
                        logger.debug(auth_response)
                        await websocket.send(json.dumps(auth_response))

                    elif message.get("action") == "PONG":
                        pong_response = {"id": message["id"], "origin_action": "PONG"}
                        logger.debug(pong_response)
                        await websocket.send(json.dumps(pong_response))
        except asyncio.CancelledError:
            logger.info(f"Task for proxy {http_proxy} cancelled")
            break
        except Exception as e:
            logger.error(e)
            logger.error(http_proxy)

async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        logger.info(f"Received exit signal {signal.name}...")

    logger.info("Napping for 3 seconds before shutdown...")
    await asyncio.sleep(3)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    [task.cancel() for task in tasks]

    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("All tasks cancelled, stopping loop")
    loop.stop()

async def main():
    try:
        with open('proxy-list.txt', 'r') as file:
            http_proxy = file.readlines()
            # Remove any leading or trailing whitespace from each line
            http_proxy = [proxy.strip() for proxy in http_proxy if proxy.strip()]
            if not http_proxy:
                raise ValueError("No proxies found in proxy-list.txt.txt")

        loop = asyncio.get_running_loop()
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(loop, signal=s)))

        tasks = []
        for proxy in http_proxy:
            task = asyncio.create_task(connect_to_wss(proxy, grass_userid))
            tasks.append(task)

        await asyncio.gather(*tasks)

    except FileNotFoundError:
        logger.error("proxy-list.txt.txt not found. Please make sure the file exists.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program terminated by user.")
