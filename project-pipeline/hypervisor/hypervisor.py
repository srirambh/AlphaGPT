from websockets.asyncio.server import serve
import asyncio
import os
import aio_pika

experts = []

async def callback(message, websocket):
    async with message.process():
        decoded = message.body.decode("utf-8")
        await websocket.send(decoded)


async def handler(websocket, q, exchange):
    while True:
        message = await websocket.recv()
        if(message.rstrip() == "END"):
            break
        if(message.rstrip() == "INFO"):
            await ",".join([" ".join(i)  for i in experts])
        if(message.rstrip() == "QUERY" and len(experts) > 0):
            await exchange.publish(aio_pika.Message(body=f"{experts[0][0]}{experts[0][1]}".encode()), routing_key="expert1")
        if(message.split(",")[0].rstrip() == "META"):
            experts.append(message.split(",")[1:])
        await q.consume(callback=lambda x: callback(x,websocket))
        


async def main():
    connection = await aio_pika.connect(host="rabbitmq")
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange("requests", type="direct")
        q = await channel.declare_queue('',exclusive=True)
        await q.bind(exchange=exchange, routing_key="hypervisor")
        async with serve(lambda x: handler(x,q,exchange), "", os.environ.get("SOCKETPORT")):
            await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())


