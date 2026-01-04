import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from argparse import ArgumentParser
from sys import exit
from os import chdir, path

# Convert American date string to date object
def string_to_date(date_string):
  return datetime.strptime(date_string, '%m/%d/%y')

# Guess the season and episode name from full title
def extract_details(title: str):
  parts = title.split(":", 2)
  parts = [s.strip() for s in parts]

  if len(parts) == 1:
    return {
      "type": "movie",
      "title": title,
      "season": "",
      "episode": "",
    }
  
  if len(parts) == 2:
    return {
      "type": "series",
      "title": parts[0],
      "season": "",
      "episode": parts[1]
    }
  
  return {
    "type": "series",
    "title": parts[0],
    "season": parts[1],
    "episode": parts[2],
  }

# Parse arguments
parser = ArgumentParser()
parser.add_argument("-f", "--file", default="./NetflixViewingHistory.csv", required=False)
parser.add_argument("-o", "--output", required=False)
parser.add_argument("-y", "--year", required=False, type=int)
args, unknown = parser.parse_known_args()

csv_path = args.file
output_path = args.output
bar_height = 0.6
year = args.year

# Read csv file
try:
  viewing_data = pd.read_csv(csv_path)
except FileNotFoundError:
  exit("Could not open viewing history! '" + csv_path + "' does not exist")

# Validate csv file
if not "Title" in viewing_data.columns or not "Date" in viewing_data.columns:
  exit("Invalid .csv format. There should be a 'Title' column and a 'Date' column")

# Extract data
show_data = viewing_data["Title"].apply(extract_details)
viewing_data["Type"] = show_data.apply(lambda x: x["type"])
viewing_data["Title"] = show_data.apply(lambda x: x["title"])
viewing_data["Season"] = show_data.apply(lambda x: x["season"])
viewing_data["Episode"] = show_data.apply(lambda x: x["episode"])
viewing_data["Date"] = viewing_data["Date"].apply(string_to_date)

# Remove movies
viewing_data = viewing_data[viewing_data["Type"] == "series"]

# Only include shows watched the specified year
if year is not None:
  start_date = datetime(year, 1, 1)
  end_date = datetime(year + 1, 1, 1)
  viewing_data = viewing_data[(viewing_data["Date"] >= start_date) & (viewing_data["Date"] <= end_date)]

if viewing_data.empty and year is not None:
  exit("You didn't watch anything the specified year. Try another year")

# Export csv with extracted data
if output_path:
  print("Writing extracted data to " + output_path)
  viewing_data.to_csv(output_path, sep=',', encoding='utf-8', index=False, header=True)

# Group by show title
shows = viewing_data.groupby("Title")["Date"].apply(list).reset_index(name='Dates')
shows.sort_values(by="Dates", key=lambda dates: dates.str[-1], inplace=True)

# Remove series where only one episode was watched
# as it was probably unintentional
shows = shows[shows.apply(lambda row: len(row["Dates"]) > 1, axis=1)]

# Fix index
shows = shows.reset_index(drop=True)

# Set default save directory to the directory of
# this file
chdir(path.dirname(__file__))
mpl.rcParams["savefig.directory"] = "./"

# Plot
fig, ax = plt.subplots()

# Render horizontal bars for each show
for index, row in shows.iterrows():
  dates = row["Dates"]
  dates.sort()

  if len(dates) == 1:
    ax.scatter(dates, dates * 0 + -0.2 + index, s=100)
  else:
    seqs = []
    start_date = dates[0]
    current_date = start_date
    days = 0

    min_duration_days = 1

    # Merge consecutive watching days into
    # one long span
    for i in range(1, len(dates)):
      diff = (dates[i] - current_date).days
      if diff <= min_duration_days:
        days += diff
        current_date = dates[i]
      else:
        days += min_duration_days
        seqs.append((start_date, timedelta(days=days)))
        start_date = dates[i]
        current_date = dates[i]
        days = 0

    seqs.append((start_date, timedelta(days=max(5, days))))

    full_range = [(dates[0], dates[-1] - dates[0])]

    # Random color based on the title
    seed = row["Title"]
    seed = seed.encode()
    seed = int.from_bytes(seed) % (2**32)
    np.random.seed(seed)

    color = np.random.rand(3,)
    translucent = np.append(color, 0.2)

    ax.broken_barh(full_range, (-bar_height / 2 + index, bar_height), color=translucent)
    ax.broken_barh(seqs, (-bar_height / 2 + index, bar_height), color=color)

    ax.annotate(
      row["Title"],
      (dates[0], index),
      ha="right", va="center",
      xytext=(-10, 0),
      textcoords='offset pixels',
    )

# Manually specify the x limits if a year is specified
# to get better labels
if year is not None:
  start_date = datetime(year, 1, 1)
  end_date = datetime(year + 1, 1, 1)
  ax.set_xlim(start_date, end_date)

# Remove frame
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

ax.invert_yaxis()
ax.set_title("Netflix viewing history")

# Label start of each year and add a tick for each month
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

plt.show()