import asyncio
import json
import os
import pprint
import time
import birdbuddy.queries.me
import requests
import random
from birdbuddy.feeder import FeederState
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from birdbuddy.client import BirdBuddy
from birdbuddy_queries_me_FEED import birdbuddy_queries_me_FEED

"""Overwrite the Queries"""
birdbuddy.queries.me.FEED = birdbuddy_queries_me_FEED


async def main():
    print(">> Start")

    bb = BirdBuddy(os.getenv('BIRD_BUDDY_EMAIL'), os.getenv('BIRD_BUDDY_PASSWORD'))
    slack_client = WebClient(token=os.getenv('SLACK_TOKEN'))
    slogans = json.load(open('slogans.json'))

    print(">> Call BirdBuddy.refresh_feed() to clear")
    await bb.refresh_feed()

    while True:
        sleep_time = await get_sleep_time(bb)
        print(">> Sleep time in seconds:", sleep_time)
        time.sleep(sleep_time)

        print(">> Call BirdBuddy.refresh_feed()")
        feeds = await bb.refresh_feed()
        # pprint.pprint(feed)
        # return

        print(">> Found items in feed:", len(feeds))

        for feed in feeds:
            if 'media' not in feed or 'contentUrl' not in feed['media']:
                continue

            url = feed['media']['contentUrl']

            print(">> Upload Bird to slack:", url)
            # https://www.tutorialspoint.com/downloading-files-from-web-using-python
            r = requests.get(url, allow_redirects=True)
            open('bird.jpg', 'wb').write(r.content)

            # https://plazagonzalo.medium.com/send-messages-to-slack-using-python-4b986586cb6e
            # https://stackoverflow.com/questions/62229535/uploading-image-to-slack-channel-with-python-script
            response = slack_client.files_upload(
                file='bird.jpg',
                initial_comment=random.choice(slogans),
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
