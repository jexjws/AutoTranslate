import os
import asyncio
import nats
from nats.errors import TimeoutError


servers = os.environ.get("NATS_URL","nats://localhost:4222").split(",")

async def main():
    nc = await nats.connect(servers=servers)
    await nc.publish("connected.watcher",b"hello")
    sub=await nc.subscribe("connected.*")
    try:
        msg = await sub.next_msg()
    except TimeoutError:
        pass
    await nc.publish("connected.watcher")
    await nc.publish("connected.watcher",b"111")
    msg = await sub.next_msg(timeout=1111)
    print(f"{msg.data} on subject {msg.subject}")
    msg = await sub.next_msg(timeout=1111)
    print(f"{msg.data} on subject {msg.subject}")

    await nc.publish("connected.w",b"111")
    msg = await sub.next_msg(timeout=1111)
    print(f"{msg.data} on subject {msg.subject}")

    # Publish as message with an inbox.
    inbox = nc.new_inbox()
    print(inbox)

    await sub.unsubscribe()
    await nc.drain()

if __name__ == '__main__':
    asyncio.run(main())
