import asyncio
import json
import os
import pprint
import time
import requests
import random
import pytz

from birdbuddy.feed import FeedNodeType
from birdbuddy.feeder import FeederState
from slack_sdk import WebClient
from dotenv import load_dotenv
from birdbuddy.client import BirdBuddy
from datetime import datetime


async def main():
    print(">> Start")

    bb = BirdBuddy(os.getenv('BIRD_BUDDY_EMAIL'), os.getenv('BIRD_BUDDY_PASSWORD'))
    bb.language_code = "de"
    slack_client = WebClient(token=os.getenv('SLACK_TOKEN'))
    slogans = json.load(open('slogans.json'))
    since: datetime = datetime.now(tz=pytz.utc)

    while True:
        sleep_time = await get_sleep_time(bb)
        print(">> Sleep time in seconds:", sleep_time)
        time.sleep(sleep_time)

        print(">> Call BirdBuddy.feed() and filter...")
        feeds = (await bb.feed(50)).filter([FeedNodeType.SpeciesSighting], newer_than=since)
        # pprint.pprint(feeds)
        since = datetime.now(tz=pytz.utc)

        print(">> Found items in feed:", len(feeds))

        for feed in feeds:
            # pprint.pprint(feed)

            name = 'Mystery Visitor'
            if 'species' in feed['collection']:
                name = feed['collection']['species']['name']

            url = feed['media']['contentUrl']

            print(">> Upload Bird to slack:", url)

            # https://www.tutorialspoint.com/downloading-files-from-web-using-python
            r = requests.get(url, allow_redirects=True)
            open('bird.jpg', 'wb').write(r.content)

            # https://plazagonzalo.medium.com/send-messages-to-slack-using-python-4b986586cb6e
            # https://stackoverflow.com/questions/62229535/uploading-image-to-slack-channel-with-python-script
            response = slack_client.files_upload(
                file='bird.jpg',
                initial_comment="{}: {}".format(name, random.choice(slogans)),
                channels=os.getenv('SLACK_CHANNEL_ID')
            )


async def get_sleep_time(bb: BirdBuddy) -> int:
    print(">> Call BirdBuddy.refresh()")
    await bb.refresh()

    if next(iter(bb.feeders.values())).state == FeederState.DEEP_SLEEP:
        # Bird Buddy is deep sleeping.... zzZZzz
        return int(os.getenv('DEEP_SLEEP_TIME'))

    return int(os.getenv('SLEEP_TIME'))


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(main())
