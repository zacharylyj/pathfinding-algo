"""
Recording link: xxxxxxxxxxxxxxx
Password (if any) :

Scenario 3: Analysis on Dwelling Type Electricity Consumption over years 

You are given AvgHouseholdElectricity.csv file by the interviewer during an
interview for an intern position in a department. 
The dataset contains electricity consumption data collected between the year 
2010 and 2023. You are to conduct analysis based on the dataset given, and 
provide some insights to the marketing director of the company from the output 
of the analysis.

The following are the deliverables of your analysis:
1.  Accept user input for Dwelling Type.

2.  Tabulate the maximum, minimum and average electricity consumption for the 
dwelling type (provided by the user in part 1) by year in the following format 
(note: in the order of the most recent year first):
 ________________________________________________________________________________
 ________________________________________
 Landed Properties consumption summary  
 ________________________________________
|        |Maximumn  |Minimum   |Average   |
 ________________________________________
|2023    |      0.00|      0.00|      0.00|
|2022    |      0.00|      0.00|      0.00|
|2021    |      0.00|      0.00|      0.00|
|2020    |      0.00|      0.00|      0.00|
|2019    |      0.00|      0.00|      0.00|
|2018    |      0.00|      0.00|      0.00|
|2017    |      0.00|      0.00|      0.00|
|2016    |      0.00|      0.00|      0.00|
|2015    |      0.00|      0.00|      0.00|
|2014    |      0.00|      0.00|      0.00|
|2013    |      0.00|      0.00|      0.00|
|2012    |      0.00|      0.00|      0.00|
|2011    |      0.00|      0.00|      0.00|
|2010    |      0.00|      0.00|      0.00|
 ________________________________________

3.	Your program should include capability to provide a summary of the insights 
based on the results of your table in part 2.

4.	Your program should allow for analysis in part 2 to be continued if required. 

5.  To value add to the analysis, you are required to think of one additional 
analysis that the marketing director may be interested to find out after 
part 4 is completed. Present the solution and explain how such analysis 
adds value the insights.

IMPORTANT: You must use the original dataset given, you are not allowed to use 
excel or any other application software to modify the data before importing 
it to your python program.

"""


# func csv to array
def read_data(file_path):
    with open(file_path, "r") as f:
        # Read the file content
        raw_data = f.read()

    # Split the data by lines
    lines = raw_data.splitlines()

    # Split each line by commas to form a 2D array
    array = [line.split(",") for line in lines]

    # Exclude the header
    data = array[1:]

    # Convert year to int and kwh_per_acc to float while appending the tuples to the final list
    processed_data = [(row[0], int(row[1]), float(row[5])) for row in data]

    return processed_data


# func to filter data by dwelling type then calculate statistics by year
def calculate_stats(data, dwelling_type):
    filtered_data = [row for row in data if row[0] == dwelling_type]
    if not filtered_data:
        print(f"No data available for dwelling type: {dwelling_type}")
        return

    # dict to store consumption data by year
    consumption_by_year = {}

    for row in filtered_data:
        year = row[1]
        kwh_per_acc = row[2]

        if year not in consumption_by_year:
            consumption_by_year[year] = []

        consumption_by_year[year].append(kwh_per_acc)

    print("________________________________________")
    print(f" {dwelling_type} consumption summary")
    print("________________________________________")
    print("|        |Maximum   |Minimum   |Average   |")
    print("________________________________________")

    for year in sorted(consumption_by_year.keys(), reverse=True):
        consumption = consumption_by_year[year]
        max_consumption = max(consumption)
        min_consumption = min(consumption)
        avg_consumption = sum(consumption) / len(consumption)

        print(
            f"|{year}    |{max_consumption:>10.2f}|{min_consumption:>10.2f}|{avg_consumption:>10.2f}|"
        )

    print("________________________________________")


# func to provide the insight
def provide_insights(data, dwelling_type):
    filtered_data = [row for row in data if row[0] == dwelling_type]
    if not filtered_data:
        return

    # years
    years = list(set(row[1] for row in filtered_data))

    recent_year = max(years)
    oldest_year = min(years)

    recent_avg = sum(row[2] for row in filtered_data if row[1] == recent_year) / len(
        [row for row in filtered_data if row[1] == recent_year]
    )
    oldest_avg = sum(row[2] for row in filtered_data if row[1] == oldest_year) / len(
        [row for row in filtered_data if row[1] == oldest_year]
    )

    print("\nSummary of Insights:")
    if recent_avg > oldest_avg:
        print(
            f"- Electricity consumption has increased from {oldest_year} to {recent_year}."
        )
    elif recent_avg < oldest_avg:
        print(
            f"- Electricity consumption has decreased from {oldest_year} to {recent_year}."
        )
    else:
        print(
            "- Electricity consumption has remained relatively stable over the years."
        )


# func add % change
def percentage_change_analysis(data, dwelling_type):
    filtered_data = [row for row in data if row[0] == dwelling_type]
    if not filtered_data:
        return

    print("\nAdditional Analysis: Percentage Change in Consumption Over Time")

    years = sorted(set(row[1] for row in filtered_data), reverse=True)

    for i in range(1, len(years)):
        current_year = years[i - 1]
        previous_year = years[i]

        current_year_avg = sum(
            row[2] for row in filtered_data if row[1] == current_year
        ) / len([row for row in filtered_data if row[1] == current_year])
        previous_year_avg = sum(
            row[2] for row in filtered_data if row[1] == previous_year
        ) / len([row for row in filtered_data if row[1] == previous_year])

        percentage_change = (
            (current_year_avg - previous_year_avg) / previous_year_avg
        ) * 100

        print(
            f"- {current_year} vs {previous_year}: {percentage_change:.2f}% change in average consumption"
        )


# read and push to create array
data = read_data("AvgHouseHoldElectricity.csv")

# extract unique dwelling types from the csv
dwelling_types = sorted(set(row[0] for row in data))

# main process loop
while True:
    print("\nSelect the dwelling type for analysis:")
    for index, value in enumerate(dwelling_types, 1):
        print(f"{index}: {value}")

    # input with handling
    user_choice = input(
        "Enter the number corresponding to the dwelling type or type the name exactly: "
    ).strip()

    # check for digit entered or actually dwelling type name
    if user_choice.isdigit() and 1 <= int(user_choice) <= len(dwelling_types):
        dwelling_type = dwelling_types[int(user_choice) - 1]
    elif user_choice in dwelling_types:
        dwelling_type = user_choice
    else:
        print(
            f"\nInvalid choice '{user_choice}'. Please enter a valid number or the dwelling type name."
        )
        continue  # else failed case then reprompt

    # tabulate consumption data
    calculate_stats(data, dwelling_type)

    # insights based on the results
    provide_insights(data, dwelling_type)

    # additional analysis (percentage change over the years)
    percentage_change_analysis(data, dwelling_type)

    # retry another type
    cont = (
        input("\nDo you want to analyze another dwelling type? (yes/no): ")
        .strip()
        .lower()
    )
    if cont != "yes":
        break
