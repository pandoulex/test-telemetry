import asyncio
import logging
import signal
import struct
from asyncio import StreamReader, StreamWriter

logging.basicConfig(
    filename="/var/mylog/frontend.log",
    filemode='w',
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger('service')


class ServerHandler:
    def __init__(self):
        self._queue = asyncio.Queue()

    async def handle_client(self, reader: StreamReader, writer: StreamWriter):
        logger.info("New client connected")
        try:
            while True:
                data = await reader.read(1)
                logger.debug("data=%s", data)
                if not data:
                    logger.debug("EOD")
                    break
                packet_type = struct.unpack('<c', data)[0]
                data = await reader.read(4)
                logger.debug("data=%s", data)
                if not data:
                    logger.debug("EOD")
                    break
                packet_len = struct.unpack('<L', data)[0]
                data = await reader.read(packet_len)
                logger.debug("data=%s", data)
                if not data:
                    logger.debug("EOD")
                    break
                if packet_type == b'M':
                    metrics = data
                    logger.debug('got new metrics: %b', metrics)
                    self._queue.put_nowait(metrics)
                elif packet_type == b'L':
                    level = struct.unpack('<i', data[:4])[0]
                    logline = data[4:].decode(encoding='utf-8').splitlines()
                    for line in logline:
                        logger.log(level, line)
        except Exception as err:
            logger.exception("error in client handler:")
        finally:
            writer.close()
        logger.info("Client disconnected")

    async def metric_job(self):
        reader, writer = await asyncio.open_connection('graphite', 9109)

        while True:
            metrics = await self._queue.get()
            writer.write(metrics)
            await writer.drain()
            logger.info("metric sent to graphite")
            self._queue.task_done()


async def run_server():
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
    loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())

    handlers = ServerHandler()

    asyncio.create_task(handlers.metric_job())

    server = await asyncio.start_server(handlers.handle_client, '', 8000)
    async with server:
        logger.info("serving server")
        await server.serve_forever()


asyncio.run(run_server())
