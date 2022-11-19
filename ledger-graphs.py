#!/usr/bin/env python3

'''
This script is designed to display ledger-cli data in graphical form. It is
assumed that a user will update the ledger_name global variable to the path
of the ledger instance that they wish to visualize.
Usage:
    * Default (no arguments): Running the script will display the last 12 months
      worth of data
    * -fiscal <year>: Running the script with the fiscal flag followed by the
      provided year will let the user see data for the 12 months of the
      calendar year
'''

import argparse
import datetime
import matplotlib.pyplot as plt
import os
import re

# This script assumes a ledger called "ledger.dat". Change this as you wish
ledger_name = "ledger.dat"

# This function collects the total income and expenses for the given year and
# returns a list of ints representing the net income for each specific month
# and a lit of ints representing the 12 months of data that we collected.
def collect_graph_data(month: int, year: int) -> [[int], [int]]:
    dates = ["/01/01", "/02/01", "/03/01", "/04/01", "/05/01", "/06/01",
             "/07/01", "/08/01", "/09/01", "/10/01", "/11/01", "/12/01"]
    net_incomes = []
    month_index = []

    # Iterate over the previous 12 months
    for m in range(month, month - 12, -1):
        cur_year = datetime.date.today().year if year == 0 else year
        new_month = m
       
        # Handle wrapping months around to previous year
        if (m < 1):
            cur_year = cur_year - 1
            new_month = m + 12            

        month_index.append(new_month)

        # We want to provide a date range in our query to ledger-cli. Since
        # we want monthly data beg_date will be the first of a given month and
        # end_date will be the last of the succeding month.
        beg_date = str(cur_year) + dates[new_month - 1]
        end_date = str(cur_year) + dates[new_month % 12]

        # If new_month is 12 (December) we need to make sure that the end date
        # year is set properly to cur_year + 1
        if (new_month == 12):
            end_date = str(cur_year + 1) + dates[new_month % 12]
        
        net_incomes.append(get_ledger_bal(beg_date, end_date))

    # Print out the income
    return [net_incomes, month_index]

# Helper function that makes the calls to ledger-cli from the command line.
# The return value is the sum of income - expenses for the given date range
def get_ledger_bal(beg_date: str, end_date: str) -> float:
    # Ledger command to get the monthly balance
    stream = os.popen("ledger -f " + ledger_name + " -b " + beg_date + 
                      " -e " + end_date + " balance Income Expenses "
                      "--invert amount")
    stream_str = stream.read()
    # If there is no monthly balance for a given month then the stream_str
    # will be none and we can just return a zero here
    if (len(str(stream_str)) == 0 ):
        return 0.0
    else:
        balance_str = str(re.search(r'(.+)(\$.*)$', stream_str).group(0))
        # Strip the $ and convert to float
        balance_float = float(balance_str.replace('$', ''))
        return balance_float
   
# This function uses matplotlib to create a bar graph of our monthly balances
def plot_balances(balances: [int], months: [int]):
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                   "Sep", "Oct", "Nov", "Dec"]
    months_to_plot = [month_names[i-1] for i in months]
    
    # Configure bar graph
    fig, ax = plt.subplots(figsize = (10, 5))
    plt.bar(months_to_plot, balances, color='blue', width=0.4)
    plt.grid(visible = True, color='grey')
    
    # Add Total Sum of months to bottom right corner
    sum_balances = round(sum(balances), 2)
    fig.text(0.9, 0.15, 'Net: $' + str(sum_balances), fontsize = 12,
             color ='purple', ha ='right', va ='bottom', alpha = 0.7)

    # Add balances for each month\
    for i in ax.patches:
        plt.text(i.get_x() - 0.2, i.get_height() + 0.4,
                 str(round((i.get_height()), 2)), fontsize = 10, color ='grey')

    # Add axis labels and title
    plt.xlabel("Month")
    plt.ylabel("Amount ($)")
    plt.title("Net Income")

    plt.show()

if __name__ == "__main__":
    # Parse the arguments (if there are any)
    parser = argparse.ArgumentParser(description='Graphical displays for '
                                                 'ledger-cli')
    parser.add_argument('-fiscal', action="store", dest="fiscal", type=int,
                        help='Display data for a given fiscal year')
    results = parser.parse_args()

    # Default values for month and year
    month = 0
    year = 0

    if (results.fiscal is not None):
        month = 12
        year = results.fiscal
    else:
        month = datetime.date.today().month

    # Collect and plot the data
    data = collect_graph_data(month, year)
    balances = data[0]
    months = data[1]
    plot_balances(balances, months)
