import requests
import pandas as pd

def head(file_contents, preview_lines_count=5):
    lines = file_contents.split("\n")
    preview_lines = lines[0:preview_lines_count]
    return "\n".join(preview_lines)

def normalize_df(df, column_name):
    column_sum = df[column_name].sum()
    df["pct"] = round(df[column_name] / column_sum, 2)
    df.sort_values(by=column_name, ascending=False, inplace=True)
    return df




response = requests.get("https://www.voidtools.com/donate/")
html_contents = response.text
df = pd.read_html(html_contents)[0]
df["Amount"] = df["Amount"].replace('\D', "", regex=True).astype(float)
df = normalize_df(df, "Amount")
print(df)
breakpoint()
