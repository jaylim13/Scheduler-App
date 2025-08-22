import pandas as pd
import re
from datetime import datetime, timedelta

# Load your CSV
df = pd.read_csv("unavailability_raw.csv")

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

all_rows = []

def time_to_24h(time_str):
    return datetime.strptime(time_str.strip(), "%I:%M%p").strftime("%H:%M")

for idx, row in df.iterrows():
    # Skip rows with no Name, we'll fill it from previous
    if pd.notna(row['Name']):
        employee = row['Name']

    for day in days:
        val = row[day]
        if pd.isna(val) or val.strip() == "":
            continue

        # Extract all time ranges from the cell
        ranges = re.findall(r'(\d{1,2}:\d{2}[ap]m)\s*–\s*(\d{1,2}:\d{2}[ap]m)', str(val))
        for start, end in ranges:
            all_rows.append({
                "employee": employee,
                "day": day,
                "start_time": time_to_24h(start),
                "end_time": time_to_24h(end)
            })

# Create final DataFrame
unavailability_df = pd.DataFrame(all_rows)
unavailability_df.to_csv("unavailability_flat.csv", index=False)

print("Saved unavailability_flat.csv with", len(unavailability_df), "entries")
