from matplotlib.pyplot import colorbar
import streamlit as st
import pandas as pd
import os
from utils import pull_ticker
from datetime import datetime as dt
from datetime import timedelta as td
from matplotlib import pyplot as plt
import seaborn as sns

# first thing always
st.beta_set_page_config(
    layout="wide",
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    page_title='FTSE 350 Insider',
    page_icon='📈'  # String, anything supported by st.image, or None.
)

st.title('FTSE 350 Insider')
FTSE_FILE = '../../data/ftse350.csv'

# pull FTSE 350 list
if os.path.exists(FTSE_FILE):
    ftse = pd.read_csv(FTSE_FILE)
else:
    ftse = pd.read_html('https://www.fidelity.co.uk/shares/ftse-350/')[0]
    ftse.columns = ftse.columns.str.lower()
    ftse.to_csv(FTSE_FILE, index=False)

# Select sector
selected_sector = st.sidebar.selectbox(
    'Select Sector', ftse.sector.unique())

# filter companies by sector
comps = ftse[ftse.sector == selected_sector]


# combine company names with tickers
comps_map = dict(zip(comps.name.values,
                     comps.epic.values))

# comopanies selector
names = st.sidebar.multiselect(
    'Select Ticker', list(comps_map.keys()))

# if at least one companies selected
if len(names) > 0:
    # get the tickers by name
    tickers = [comps_map[x] for x in names]

    # get today timestamp
    today = dt.now()
    # we use this to get the start date
    history_days = st.number_input(
        'Select number of hostorical days (current_year - number of days)', min_value=30)
    # stocks dict
    stocks = dict()

    # make a df with dates to be merged with
    stks = pd.DataFrame({'date': pd.date_range(
        today - td(days=history_days), today)})

    # make date to string
    stks.date = stks.date.dt.date.astype(str)

    # for each selected ticker pull the data and merge with dates df
    for tick in tickers:
        stocks[tick] = pull_ticker(
            tick=tick, start=today - td(days=history_days), end=today)
        stks = stks.merge(stocks[tick], on='date', how='left')

    #  make dates back to datetime for nice plotting
    stks.date = pd.to_datetime(stks.date)
    # set index to date for nice plotting
    stks = stks.set_index('date')
    # fill missing values back and forth for nice plotting
    stks = stks.fillna(method='ffill').fillna(method='bfill')
    # print dataframe
    st.write(stks)
    # plot open and close prices side by side
    col1, col2 = st.beta_columns(2)
    close_cols = stks.columns[stks.columns.str.contains('_close')].tolist()
    open_cols = stks.columns[stks.columns.str.contains('_open')].tolist()
    vol_cols = stks.columns[stks.columns.str.contains('_volume')].tolist()

    col1.subheader('Open Prices')
    col1.line_chart(stks[open_cols].rename(
        columns=dict(zip(open_cols, names))))

    col2.subheader('Closed Prices')
    col2.line_chart(stks[close_cols].rename(
        columns=dict(zip(close_cols, names))))

    st.subheader('Volume')
    st.area_chart(stks[vol_cols].rename(
        columns=dict(zip(vol_cols, names))))
    # correlation on percentage change
    st.subheader('Percentage change correlation')
    fig, ax = plt.subplots(1, 2, figsize=(15, 7), sharey=True)
    sns.heatmap(stks[open_cols].pct_change()[
        2:].corr(method='spearman'), annot=True, fmt='.2f', ax=ax[0])
    ax[0].set_title('Open Prices')
    ax[0].set_yticklabels(names, rotation=0)
    ax[0].set_xticklabels(names, rotation=90)

    sns.heatmap(stks[close_cols].pct_change()[
                2:].corr(method='spearman'), annot=True, fmt='.2f', ax=ax[1])
    ax[1].set_title('Close Prices')
    ax[1].set_yticklabels(names, rotation=0)
    ax[1].set_xticklabels(names, rotation=90)
    st.pyplot(fig)
