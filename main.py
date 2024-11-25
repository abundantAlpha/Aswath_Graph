import pandas as pd
import requests
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import json

#######################################################################################################################
# https://www.youtube.com/watch?v=ouxmdkMWWmI&ab_channel=AswathDamodaran
# 9:49
#######################################################################################################################

# user defined variables
ticker = input('Enter the ticker you want to chart:  ')
quarters = int(input('Enter the number of quarters you want to chart for this ticker:  '))
currency_denominator = 1000000

#######################################################################################################################
# Pandas Data Xformations
#######################################################################################################################

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    api_key = config["api_key"]
    config_file.close()

# base variables
url = f'https://financialmodelingprep.com/api/v3/income-statement/{ticker.upper()}?period=quarter&limit=400&apikey={api_key}'
response = requests.get(url).json()

# construct the dataframe
df = pd.DataFrame(response)

# data for horizontal lines
# 4 quarters
prior_four_quarter_df = df[1:5]
avg_rev_prior_four_quarters = prior_four_quarter_df['revenue'].mean() / currency_denominator
avg_op_income_prior_four_quarters = prior_four_quarter_df['operatingIncome'].mean() / currency_denominator

# 4 years
prior_four_year_df = df[1:17]
avg_rev_prior_four_years = prior_four_year_df['revenue'].mean() / currency_denominator
avg_op_income_prior_four_years = prior_four_year_df['operatingIncome'].mean() / currency_denominator

# data for bar plots
df['Date'] = pd.to_datetime(df['date']).dt.strftime('%Y/%m/%d')
df['year'] = df['calendarYear'].str[-2:]
df['Period'] = df['period'] + "." + df['year'].astype(str)
df['Revenue'] = df['revenue'] / currency_denominator
df['Operating Income'] = df['operatingIncome'] / currency_denominator


# data for line plots
df['Revenue Growth'] = (round(df['Revenue'].pct_change(periods=-4), 2) * 100).dropna(axis=0).astype(float)
df['Operating Margin'] = (round(df['Operating Income'] / df['Revenue'], 2) * 100).astype(float)
keep_columns = ['Date', 'Period', 'Revenue', 'Operating Income', 'Revenue Growth', 'Operating Margin']

df = df[keep_columns][:quarters].sort_values('Date', ascending=True)
df.reset_index(inplace=True, drop=True)


#######################################################################################################################
# plotting
#######################################################################################################################
x_periods = list(df['Period'])
fig, ax = plt.subplots()
bar_width = .35


# x axis
plt.xticks(ticks=range(quarters), labels=x_periods)

# left axis / bar charts
ax.bar(df.index - bar_width/2,
       df['Revenue'],
       width=bar_width,
       align='center',
       label='Revenue',
       color='purple',
       )

ax.bar(df.index + bar_width/2,
       df['Operating Income'],
       width=bar_width,
       align='center',
       label='Operating Income',
       color='orange',
       )

plt.ylim(ax.get_ylim()[1] * -.1, ax.get_ylim()[1])
fmt = '${x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
ax.yaxis.set_major_formatter(tick)
ax.set_ylabel('quarterly revenue and operating income (in $ millions)')

# horizontal lines for prior 4 quarter averages
ax.axhline(int(avg_rev_prior_four_quarters),
           label='Average Revenue (prior 4 qrtrs)',
           color='grey'
           )
ax.axhline(int(avg_op_income_prior_four_quarters),
           label='Average Op. Income (prior 4 qrtrs)',
           color='green'
           )

ax.axhline(int(avg_rev_prior_four_years),
           label='Average Revenue (past 4 years)',
           color='purple'
           )
ax.axhline(int(avg_op_income_prior_four_years),
           label='Average Op. Income (past 4 years)',
           color='magenta'
           )


# right axis / operating margin and revenue growth line graphs
axb = plt.gca().twinx()
axb.plot(range(quarters),
         df['Operating Margin'],
         'r',
         label='Operating Margin')
axb.plot(range(quarters),
         df['Revenue Growth'],
         '--b',
         label='Revenue Growth (% y/y)')

axb.yaxis.set_major_formatter(mtick.PercentFormatter())
axb.set_ylabel('operating margin and revenue growth (%)')
plt.ylim(-10, 100)


# Add a table at the bottom of the axes
messy_data = df[['Revenue', 'Operating Income', 'Operating Margin', 'Revenue Growth']].transpose().values
clean_data = [[date for date in df['Date']]]

for ea_list in messy_data:
    rounded_list = [int(x) for x in ea_list]
    clean_data.append(rounded_list)

the_table = plt.table(cellText=clean_data[1:],
                      rowLabels=['Revenue', 'Operating Income', 'Operating Margin (%)', 'Revenue Growth (%)'],
                      colLabels=df['Period'],
                      loc='bottom',
                      )
the_table.auto_set_font_size(False)
the_table.set_fontsize(8)
fig.legend(loc='upper left')

plt.tight_layout()
plt.title(f'{ticker.upper()} Trends in Revenue and Profitability - Last {quarters} Quarters')

plt.show()

