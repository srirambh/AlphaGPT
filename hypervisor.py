from websockets.asyncio.server import serve
import asyncio
async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)


async def main():
    async with serve(handler, "", 8080):
        await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())