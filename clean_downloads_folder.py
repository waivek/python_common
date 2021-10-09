import sys
sys.path = [ "C:/users/vivek/Documents/Python/" ] + sys.path
from common import print_green_line, print_red_line, truncate, make_string_green
import os
import os.path
from glob import glob
def make_downloads_directory(folder_name):
    path = os.path.join(global_downloads_directory, folder_name)
    if os.path.exists(path):
        return
    os.mkdir(path)
    print_green_line("[MKDIR] {path}".format(path=path))

def find_one(items, f):
    matching_items = [ item for item in items if f(item) ]
    if len(matching_items) > 1:
        print_red_line("[ERROR] More than one match in the list (function: find_one)")
        return 
    if len(matching_items) == 0:
        return None
    return matching_items[0]

def move_extension(extension, folder_name):
    glob_pattern = "{downloads_directory}/*.{extension}".format(downloads_directory=global_downloads_directory, extension=extension)
    input_paths = glob(glob_pattern)
    if input_paths == []:
        return
    basenames = [ os.path.basename(absolute_path) for absolute_path in input_paths ]
    output_paths = [ os.path.join(global_downloads_directory, folder_name, basename) for basename in basenames ]
    for input_path, output_path in zip(input_paths, output_paths):
        os.rename(input_path, output_path)
    message = "[MOVE] Moved {count} {extension} files to {folder_name}: {trunc_files}".format(
            count=make_string_green(len(basenames)), extension=make_string_green(extension), folder_name=make_string_green(folder_name), trunc_files=truncate(", ".join(basenames), 80))
    print(message)

def main():
    # D = {
    #     "Compressed" : [ "zip" ],
    # }
    D = {
        "Compressed" : [ "zip", "rar" ],
        "Executables" : [ "exe", "msi" ],
        "Torrents" : [ "torrent" ],
        "PDFs" : [ "pdf" ],
        "Images" : [ "svg", "png", "jpg" ]
    }
    for directory_name in D.keys():
        make_downloads_directory(directory_name)

    # move extensions
    for folder_name, extension_list in D.items():
        for extension in extension_list:
            move_extension(extension, folder_name)


if __name__ == "__main__":
    global_downloads_directory = os.path.normpath(os.path.expanduser(r'~\Downloads'))
    main()
