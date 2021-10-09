
import os
output_directory =  "C:/Users/vivek/Downloads/Gudia/The.Office/The Office S08 BluRay 720p x264 [Pahe.in]"
file_containting_urls = "list_of_urls.txt"

os.chdir(output_directory)
with open("hello.txt", "wb") as f:
    f.write("hello, world!".encode("utf-8"))

