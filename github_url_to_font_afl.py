import sys
sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path
from common import make_string_green
import argparse
import os.path
import os
from bs4 import BeautifulSoup
import requests
import subprocess
import re
from urllib.parse import unquote



def rename_font_weight_portion(font_str):
    # "proxima nova extra bold"
    # "proxima nova extrabold"
    # "proxima_nova_extra_bold"
    # "proxima_nova_extrabold"
    weights_D = {
        "thin" : 100, "hairline" : 100, 

        "extra light" : 200, "ultra light" : 200, 
        "light" : 300, 

        "normal" : 400, "regular" : 400, "roman": 400,
        "medium" : 500, 

        "semi bold" : 600, "demi bold" : 600, "extra bold" : 800, "ultra bold" : 800, 
        "bold" : 700, 

        "heavy" : 900, 

        "extra black" : 950, "ultra black" : 950,
        "black" : 900, 
    }

    for weight_name, weight_int in weights_D.items():
        weight_pattern = weight_name.replace(" ", "[ _-]?") # extra bold -> extra[ _-]?bold
        pattern = weight_pattern
        replacement = str(weight_int)
        string = font_str
        font_str = re.sub(pattern, replacement, string, flags=re.IGNORECASE)
    return font_str


def extract_font_weight(font_str):
    font_str = rename_font_weight_portion(font_str)
    m = re.search(r'\D(?P<weight_string>[1-9][0-5]0)\D', font_str)
    if m:
        weight_string = m.group("weight_string")
        return int(weight_string)
    else:
        return 1000


parser = argparse.ArgumentParser(description="Take a github repository and extract ttf to an AFL file")
parser.add_argument("url")
parser.add_argument("-d", "--download", action='store_true')
args = parser.parse_args()
# "https://github.com/waivek/style/tree/master/fonts"
url = args.url
r = requests.get(url)
html_contents = r.text
soup = BeautifulSoup(html_contents, "html.parser")
ttf_anchors = soup.select("a.js-navigation-open.link-gray-dark[href$=ttf]")
relative_links = [ a["href"] for a in ttf_anchors ] 
input_link = r'/waivek/style/blob/master/fonts/confluence_c2_bold.ttf'
output_link = r'https://github.com/waivek/style/raw/master/fonts/confluence_c2_bold.ttf'

output_directory = os.path.expanduser(r'~\Downloads\fonts')
class DownloadSegment:
    def __init__(self, segment_string, weight):
        self.segment = segment_string
        self.weight = weight

download_segments = []
for l in relative_links:
    empty, username, repository, _, *remainder, filename = l.split("/")
    download_link = r'https://github.com/{username}/{repository}/raw/{remainder}/{filename}'.format(username=username, repository=repository, remainder="/".join(remainder), filename=filename)
    processed_filename = rename_font_weight_portion(unquote(filename))
    extracted_weight= extract_font_weight(unquote(filename))
    download_segment = r"""
{download_link}
  out={filename}
  dir={output_directory}
    """.strip().format(download_link=download_link, output_directory=output_directory, filename=processed_filename)
    download_segments.append(DownloadSegment(download_segment, extracted_weight))

download_segments.sort(key=lambda segment: int(segment.weight))
download_lines = [ download_segment.segment for download_segment in download_segments ]

if args.download:
    filename = "temp.afl"
    with open(filename, "wb") as f:
        f.write("\n".join(download_lines).encode("utf-8"))
    subprocess.run("aria2c -i {filename} --auto-file-renaming=false --allow-overwrite=true".format(filename=filename))
    os.remove(filename)
else:
    colored_lines = []
    for download_line in download_lines:
        filename = re.search(r"out=(.*)", download_line).group(1)
        green_filename = make_string_green(filename)
        colored_line = re.sub(r"out=(.*)", r"out={green_filename}".format(green_filename=green_filename), download_line)
        colored_lines.append(colored_line)
    print("\n".join(colored_lines))
    print("# Pass --download or -d flag to download")

