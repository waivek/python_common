# import argparse
import sys
from common import Timestamp
# parser = argparse.ArgumentParser()
# parser.add_argument('video_duration_timestamp')
# parser.add_argument('duration_remaining_timestamp')
# args = parser.parse_args()
# video_duration = Timestamp(args.video_duration_timestamp)
# duration_remaining = Timestamp(args.duration_remaining_timestamp)
# difference = video_duration - duration_remaining
# print(difference.timestamp)
#
offset = Timestamp("3:04:05") - Timestamp("13:10")

youtube_time = Timestamp(sys.argv[1])
twitch_time = youtube_time + offset
print(twitch_time.timestamp)

