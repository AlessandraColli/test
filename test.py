import datetime
import time
import pandas as pd
import numpy as np


def mad(data):
    return np.mean(np.absolute(data - np.mean(data)))


def make_trend_signal(signal, length=252):
    indicator = 0
    criterion = pd.Series(index=signal.index)

    for i, d in enumerate(ief.index):
        if i <= 252:
            continue
        mads = mad(signal.iloc[i - (length + 1):i])
        mean = signal.iloc[i - (length + 1):i].sum(skipna=True) / length

        if signal.iloc[i] > mean + mads:
            indicator = 1
            criterion.iloc[i] = indicator
        elif indicator == 1 and signal.iloc[i] > mean:
            criterion.iloc[i] = indicator
        elif signal.iloc[i] < mean - mads:
            indicator = -1
            criterion.iloc[i] = indicator
        elif indicator == -1 and signal.iloc[i] < mean:
            criterion.iloc[i] = indicator
        else:
            indicator = 0
            criterion.iloc[i] = indicator

    return criterion


if __name__ == '__main__':
    
    today = datetime.datetime.today()
    today_ts = int(time.mktime(today.timetuple()))

    url_spy = f'https://query1.finance.yahoo.com/v7/finance/download/SPY?period1=1650428990&period2={today_ts}&interval=1d&events=history&includeAdjustedClose=true'
    df_spy = pd.read_csv(url_spy)

    url_ief = f'https://query1.finance.yahoo.com/v7/finance/download/IEF?period1=1650428990&period2={today_ts}&interval=1d&events=history&includeAdjustedClose=true'
    df_ief = pd.read_csv(url_ief)

    spy = df_spy.set_index('Date')
    ief = df_ief.set_index('Date')

    danger_spy_vol_thrs = 0.03

    spy_price = spy['Adj Close'].iloc[-12:]
    spy_rets = np.log(spy_price) - np.log(spy_price.shift(1))
    spy_vol = spy_rets.iloc[-10:].std(ddof=0)
    if spy_vol > danger_spy_vol_thrs:
        print("SPY rolling 10d volatility is above threshold.")

    ief_signal_252 = make_trend_signal(ief['Adj Close'])

    print("IEF 252d trend signal is", ief_signal_252.iloc[-1])
 
