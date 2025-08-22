import pandas as pd
from collections import defaultdict

# Load CSVs
unavailability = pd.read_csv("unavailability_flat.csv")
hours_csv = pd.read_csv("hours.csv")  # columns: first_name,last_name,Hours

# Build max hours dict and initialize scheduled hours
max_hours = {f"{row['first_name']} {row['last_name']}": row['Hours'] for _, row in hours_csv.iterrows()}
scheduled_hours = {emp: 0 for emp in max_hours}

# Define shift hours
shift_hours = {
    "Monday": list(range(9, 22)),
    "Tuesday": list(range(9, 22)),
    "Wednesday": list(range(9, 22)),
    "Thursday": list(range(9, 22)),
    "Friday": list(range(9, 22)),
    "Sunday": list(range(13, 18))  # 1pm-5pm only
}

# Initialize availability dict
all_employees = list(max_hours.keys())
availability_dict = defaultdict(lambda: defaultdict(list))
for day, hours in shift_hours.items():
    for hour in hours:
        availability_dict[day][hour] = all_employees.copy()

# Remove unavailable hours
for _, row in unavailability.iterrows():
    emp = row['employee']
    day = row['day']
    start_hour, start_min = map(int, row['start_time'].split(":"))
    end_hour, end_min = map(int, row['end_time'].split(":"))
    if end_min > 0:
        end_hour += 1
    for hour in range(start_hour, end_hour):
        if emp in availability_dict[day].get(hour, []):
            availability_dict[day][hour].remove(emp)

MIN_EMP = 3
MAX_EMP = 6
schedule = defaultdict(list)

# ------------------ Two-pass balanced scheduling ------------------

# First pass: ensure MIN_EMP while prioritizing employees with fewest hours
for day, hours in shift_hours.items():
    for hour in hours:
        available = [e for e in availability_dict[day][hour] if scheduled_hours[e] < max_hours[e]]
        available.sort(key=lambda x: scheduled_hours[x])  # prioritize lowest scheduled hours
        assigned = []

        while len(assigned) < MIN_EMP and available:
            emp = available.pop(0)
            assigned.append(emp)
            scheduled_hours[emp] += 1

        if len(assigned) < MIN_EMP:
            assigned += ["UNDERSTAFFED"] * (MIN_EMP - len(assigned))

        schedule[(day, hour)] = assigned

# Second pass: fill remaining slots up to MAX_EMP, still balancing hours
for day, hours in shift_hours.items():
    for hour in hours:
        assigned = schedule[(day, hour)]
        if "UNDERSTAFFED" in assigned:
            continue  # can't fill understaffed shifts further
        available = [e for e in availability_dict[day][hour]
                     if scheduled_hours[e] < max_hours[e] and e not in assigned]
        available.sort(key=lambda x: scheduled_hours[x])

        while len(assigned) < MAX_EMP and available:
            emp = available.pop(0)
            assigned.append(emp)
            scheduled_hours[emp] += 1

        schedule[(day, hour)] = assigned

# Convert to DataFrame
output_rows = []
max_columns = 0
for (day, hour), employees in schedule.items():
    shift_time = f"{hour:02d}:00-{hour+1:02d}:00"
    output_rows.append([day, shift_time] + employees)
    max_columns = max(max_columns, len(employees))

columns = ["day", "shift_time"] + [f"employee{i+1}" for i in range(max_columns)]
schedule_df = pd.DataFrame(output_rows, columns=columns)
schedule_df.to_csv("final_schedule_balanced.csv", index=False)

print("Balanced two-pass schedule created: final_schedule_balanced.csv")
