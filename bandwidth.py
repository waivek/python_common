
import argparse
from common import Timestamp

parser = argparse.ArgumentParser(description='')
parser.add_argument('speed_string')
args = parser.parse_args()

KB = 1024
MB = 1024 * 1024
GB = 1024 * 1024 * 1024

input_KB_per_second = int(args.speed_string)
input_B_per_second = input_KB_per_second * KB

download_time = Timestamp((GB) / (input_B_per_second))
print("download_time: %s" % (download_time))
