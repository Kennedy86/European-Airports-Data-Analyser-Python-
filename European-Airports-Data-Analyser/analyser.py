

from graphics import * 
import csv             
from collections import Counter, defaultdict

# Predefined valid airport codes with their full city names
VALID_CITY_CODES = {
    "AMS": "Amsterdam", "ARN": "Stockholm", "ATH": "Athens", "BCN": "Barcelona",
    "CDG": "Paris Charles de Gaulle", "CPH": "Copenhagen", "DUB": "Dublin",
    "FCO": "Rome Fiumicino", "FRA": "Frankfurt", "HEL": "Helsinki",
    "IST": "Istanbul", "LHR": "London Heathrow", "LGW": "London Gatwick",
    "LIN": "Milan Linate", "LYS": "Lyon", "MAD": "Madrid", "MAN": "Manchester",
    "MUC": "Munich", "MXP": "Milan Malpensa", "NRT": "Tokyo Narita",
    "ORY": "Paris Orly", "PMI": "Palma de Mallorca", "PRG": "Prague",
    "STR": "Stuttgart", "VIE": "Vienna", "WAW": "Warsaw",
}

# Used to convert destination codes into readable names (where needed)
DEST_LONG = {
    "MAD": "Madrid", "FRA": "Frankfurt", "LIS": "Lisbon", "FCO": "Rome Fiumicino",
    "LHR": "London Heathrow", "MUC": "Munich", "AMS": "Amsterdam",
    "BCN": "Barcelona", "IST": "Istanbul",
}

# Accepted airline codes mapped to their full airline names
VALID_AIRLINES = {
    "AF": "Air France", "BA": "British Airways", "LH": "Lufthansa", "QR": "Qatar Airways",
    "EK": "Emirates", "IB": "Iberia", "U2": "easyJet", "FR": "Ryanair", "SK": "Scandinavian Airlines",
    "SN": "Brussels Airlines", "AY": "Finnair", "TK": "Turkish Airlines", "A3": "Aegean Airlines"
}

data_list = []  # Global list that stores flight records from the CSV file


# Ask the user to enter a valid city code (e.g. LHR)
def get_city_code():
    while True:
        code = input("Enter a three-letter departure city code: ").strip().upper()
        if len(code) != 3:
            print("Wrong code length - please enter a three-letter city code")
        elif code not in VALID_CITY_CODES:
            print("Unavailable city code - please enter a valid city code")
        else:
            return code

# Ask the user to enter a valid year, between 2000–2025
def get_year():
    while True:
        yr = input("Please enter the year required in the format YYYY: ").strip()
        if not yr.isdigit() or len(yr) != 4:
            print("Wrong data type - please enter a four-digit year value")
            continue
        yr_int = int(yr)
        if 2000 <= yr_int <= 2025:
            return yr_int
        print("Out of range - please enter a value from 2000 to 2025")


# Loads the CSV into memory, clearing the old one first
def load_csv(csv_name):
    data_list.clear()
    try:
        with open(csv_name, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header row
            for row in reader:
                data_list.append(row)
    except Exception as e:
        print("Failed to load CSV:", e)


# Core calculations 
def calculate_metrics(rows):
    total = len(rows)
    runway1 = sum(1 for r in rows if r[8].strip() == "1")
    over_500 = sum(1 for r in rows if int(r[5]) > 500)
    ba = sum(1 for r in rows if r[1].startswith("BA"))
    rain = sum(1 for r in rows if "rain" in r[9].lower())
    af = sum(1 for r in rows if r[1].startswith("AF"))
    delayed = sum(1 for r in rows if r[2] != r[3])
    avg_hour = round(total / 12, 2)
    pct_af = round(af / total * 100, 2) if total else 0
    pct_delayed = round(delayed / total * 100, 2) if total else 0
    rain_hours = {r[2][:2] for r in rows if "rain" in r[9].lower()}
    total_rain = len(rain_hours)
    dest_counter = Counter(r[4] for r in rows)
    top_freq = max(dest_counter.values())
    common_dests = [DEST_LONG.get(d, d) for d, c in dest_counter.items() if c == top_freq]

    return {
        "Total number of departure flights recorded in the 12-hour period": total,
        "Total number of flights taking off from runway 1": runway1,
        "Total number of departures of flights that are over 500 miles": over_500,
        "Total number of departure flights by British Airways aircraft": ba,
        "Total number of flights departing in rain": rain,
        "Average number of departures per hour": avg_hour,
        "Percentage of total departures that are Air France aircraft": f"{pct_af}%",
        "Percentage of flights with delayed departures": f"{pct_delayed}%",
        "Total number of hours of rain in the twelve hours": total_rain,
        "Most common destination(s)": ", ".join(common_dests)
    }


# Opens results of this run to a text file
def save_to_file(airport, year, metrics):
    with open("results.txt", "a", encoding="utf-8") as f:
        f.write(f"Airport: {airport}\nYear: {year}\n")
        for k, v in metrics.items():
            f.write(f"{k}: {v}\n")
        f.write("-" * 50 + "\n")


# Ask the user to enter an airline code (e.g. BA)
def get_airline_code():
    while True:
        code = input("Enter a two-character Airline code to plot a histogram: ").strip().upper()
        if code in VALID_AIRLINES:
            return code
        print("Unavailable Airline code please try again:")


# Plots the bar chart for the selected airline’s hourly departures
def plot_histogram(code, airline_name, airport_name, year):
    hour_bins = defaultdict(int)
    for row in data_list:
        if row[1].startswith(code):
            hour = row[2][:2]
            if hour.isdigit():
                hour_bins[int(hour)] += 1

    max_count = max(hour_bins.values(), default=1)

    win = GraphWin("Histogram", 900, 400)
    win.setBackground(color_rgb(245, 235, 245))  # light pastel background

    bar_width = 60
    x_margin = 50
    y_base = 340
    scale = 250 / max_count

    for i in range(12):
        count = hour_bins.get(i, 0)
        x1 = x_margin + i * bar_width
        x2 = x1 + bar_width - 10
        y1 = y_base - count * scale
        y2 = y_base

        bar = Rectangle(Point(x1, y1), Point(x2, y2))
        bar.setFill(color_rgb(180, 235, 200))  # mint green
        bar.setOutline("black")
        bar.draw(win)

        # Flight count label above each bar
        Text(Point((x1 + x2) / 2, y1 - 10), str(count)).draw(win)
        # Hour label below each bar
        Text(Point((x1 + x2) / 2, y_base + 15), f"{i:02}").draw(win)

    # Chart title and x-axis label
    Text(Point(450, 25), f"Departures by hour for {airline_name} from {airport_name} {year}").draw(win)
    Text(Point(450, 370), "Hours 00:00 to 12:00").draw(win)

    win.getMouse()
    win.close()


# Main loop of the program
def main():
    while True:
        city = get_city_code()
        year = get_year()
        csv_file = f"{city}{year}.csv"

        load_csv(csv_file)
        airport_name = VALID_CITY_CODES[city]

        print("*" * 70)
        print(f"File {csv_file} selected - Planes departing {airport_name} {year}.")
        print("*" * 70)

        metrics = calculate_metrics(data_list)
        for k, v in metrics.items():
            print(f"{k}: {v}")

        save_to_file(airport_name, year, metrics)

        airline_code = get_airline_code()
        airline_name = VALID_AIRLINES[airline_code]
        plot_histogram(airline_code, airline_name, airport_name, year)

        again = input("Do you want to select a new data file? Y/N: ").strip().lower()
        if again != 'y':
            print("Thank you. End of run")
            break


if __name__ == "__main__":
    main()
