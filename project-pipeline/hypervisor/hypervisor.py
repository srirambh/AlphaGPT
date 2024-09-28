from websockets.asyncio.server import serve
import asyncio
import os
import pika

experts = []
async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)
        if(message.rstrip() == "END"):
            print("hi")
            break


async def main():
    async with serve(handler, "", os.environ.get("SOCKETPORT")):
        await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    print(os.environ.get("SOCKETPORT"))
    asyncio.run(main())


