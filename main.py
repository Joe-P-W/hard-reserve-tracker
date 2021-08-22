import re
import shutil
from collections import defaultdict

import pandas as pd
import os

import pyperclip as pyperclip

from utils.padding import pad
from utils.raid_map import RAID_MAP

dfs = [(pd.read_csv(f"load/{file}"), file) for file in os.listdir("load")]

for df, file in dfs:
    df["Id"] = int("".join(re.findall("[\d]{18}", file)))
    df["From"] = RAID_MAP[df[df["From"] != "Trash"]["From"].iat[0]]

dfs = [df for df, _ in dfs]

hard_reserve_data = pd.concat([pd.read_csv("hard_reserve_data.csv")] + dfs)
hard_reserve_data.sort_values("Date", inplace=True)
hard_reserve_data.drop_duplicates(["Name", "Id"], keep="last", inplace=True)

hard_reserves = defaultdict(list)

for person in hard_reserve_data["Name"].unique():
    for raid in hard_reserve_data["From"].unique():
        sr_items = hard_reserve_data[(hard_reserve_data["Name"] == person) & (hard_reserve_data["From"] == raid)]
        if len(sr_items.index) >= 4 and all(sr_items["ItemId"].iloc[-4:] == sr_items["ItemId"].iat[-1]):
            hard_reserves[raid].append((person, sr_items["Item"].iat[-1]))

hard_reserve_data.to_csv("hard_reserve_data.csv", index=False)

files = [file for file in os.listdir("load")]
for file in files:
    shutil.move(f"load/{file}", f"archive/{file}")

printout = """"""
for raid, raid_reserves in hard_reserves.items():
    raid_reserves = sorted(raid_reserves, key=lambda x: x[1])

    max_item_length = max(len(item) for _, item in raid_reserves + [("", "Item")])
    max_name_length = max(len(name) for name, _ in raid_reserves + [("Names", "")])

    printout += f"**{raid}**\n"
    printout += "```\n"
    printout += f"|{pad('Item', max_item_length)}|{pad('Names', max_name_length)}|\n"
    printout += f"|:{'-' * (max_item_length - 2)}:|:{'-' * (max_name_length - 2)}:|\n"

    for name, item in raid_reserves:
        printout += f"|{pad(item, max_item_length)}|{pad(name, max_name_length)}|\n"

    printout += "```"
    printout += "\n\n"

printout = printout.rstrip("\n")
pyperclip.copy(printout)

print(printout)
