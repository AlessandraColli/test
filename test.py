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

    url_spy = 'https://query1.finance.yahoo.com/v7/finance/download/SPY?interval=1d&events=history&includeAdjustedClose=true'
    df_spy = pd.read_csv(url_spy)
    df_spy = df_spy.set_index('Date')

    url_ief = 'https://query1.finance.yahoo.com/v7/finance/download/IEF?interval=1d&events=history&includeAdjustedClose=true'
    df_ief = pd.read_csv(url_ief)
    df_ief = df_ief.set_index('Date')

    spy = pd.read_csv('data/SPY.csv')
    spy = spy.set_index('Date')
    spy = pd.concat([spy, df_spy], axis=0)
    spy.to_csv('data/SPY.csv')

    ief = pd.read_csv('data/IEF.csv')
    ief = ief.set_index('Date')
    ief = pd.concat([ief, df_ief], axis=0)
    ief.to_csv('data/IEF.csv')

    danger_spy_vol_thrs = 0.03

    spy_price = spy['Adj Close'].iloc[-12:]
    spy_rets = np.log(spy_price) - np.log(spy_price.shift(1))
    spy_vol = spy_rets.iloc[-10:].std(ddof=0)
    if spy_vol > danger_spy_vol_thrs:
        print("SPY rolling 10d volatility is above threshold.")

    ief_signal_252 = make_trend_signal(ief['Adj Close'])

    print("IEF 252d trend signal is", ief_signal_252.iloc[-1])
 
