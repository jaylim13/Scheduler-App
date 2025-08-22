import re
import pandas as pd
from datetime import datetime, timedelta

def parse_unavailability(text, employee_name, days=None, slot_minutes=60):
    """
    Parse raw 'Unavailable hh:mmam – hh:mmpm' text into a DataFrame.
    - text: raw multiline string for one employee
    - employee_name: string
    - days: list of weekdays to assign sequentially (e.g., ["Mon","Tue","Wed",...])
    - slot_minutes: granularity (default 60 minutes)
    """
    # Regex to capture time ranges
    pattern = r"Unavailable\s*([\d:]+[ap]m)\s*–\s*([\d:]+[ap]m)"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)

    if days is None:
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    results = []
    day_idx = 0
    for start_str, end_str in matches:
        day = days[day_idx % len(days)]  # cycle through days in order
        day_idx += 1

        # parse start/end into datetime objects
        start = datetime.strptime(start_str.lower(), "%I:%M%p")
        end = datetime.strptime(end_str.lower(), "%I:%M%p")

        # walk through slots
        cur = start.replace(minute=0)  # round down to hour
        while cur < end:
            slot_id = f"{day}_{cur.strftime('%H:%M')}"
            results.append({"employee": employee_name, "slot_id": slot_id})
            cur += timedelta(minutes=slot_minutes)

    return pd.DataFrame(results)

# Example usage:
raw = """
Unavailable 9:30am – 11:30am
Unavailable 10:00am – 12:15pm
Unavailable 3:00pm – 6:00pm
"""
df = parse_unavailability(raw, "Adi More")
print(df)
df.to_csv("unavailability.csv", index=False)
