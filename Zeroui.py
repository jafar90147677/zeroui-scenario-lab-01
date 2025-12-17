import os, asyncio
from UnleashClient import UnleashClient

client = UnleashClient(
    url="http://localhost:42420/api",
    app_name="zeroui-lab",
    custom_headers={"Authorization": os.environ["UNLEASH_TOKEN"]},
)
client.initialize_client()

async def main():
    while True:
        print(client.is_enabled("ZeroUI-Technology"))
        await asyncio.sleep(1)

asyncio.run(main())
