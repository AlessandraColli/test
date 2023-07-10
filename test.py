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
        if i <= length:
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

    today_str = today.strftime('%Y-%m-%d')

    start_date = today - datetime.timedelta(days=400)
    start_ts = int(time.mktime(start_date.timetuple()))

    url_spy = f'https://query1.finance.yahoo.com/v7/finance/download/SPY?period1={start_ts}&period2={today_ts}&interval=1d&events=history&includeAdjustedClose=true'
    df_spy = pd.read_csv(url_spy)

    url_ief = f'https://query1.finance.yahoo.com/v7/finance/download/IEF?period1={start_ts}&period2={today_ts}&interval=1d&events=history&includeAdjustedClose=true'
    df_ief = pd.read_csv(url_ief)

    url_shy = f'https://query1.finance.yahoo.com/v7/finance/download/SHY?period1={start_ts}&period2={today_ts}&interval=1d&events=history&includeAdjustedClose=true'
    df_shy = pd.read_csv(url_ief)

    spy = df_spy.set_index('Date')

    dates = spy.index
    if today_str in dates:
        dates = dates.drop(today_str)
        spy = spy.reindex(dates)

    ief = df_ief.set_index('Date').reindex(dates)
    shy = df_shy.set_index('Date').reindex(dates)

    spy_price = spy['Adj Close'].fillna(method='ffill')
    ief_price = ief['Adj Close'].fillna(method='ffill')
    shy_price = shy['Adj Close'].fillna(method='ffill')

    danger_spy_vol_thrs = 0.03

    spy_rets = np.log(spy_price) - np.log(spy_price.shift(1))

    spy_vol_3m = spy_rets.rolling(63).std(ddof=0)
    vol_signal_126 = make_trend_signal(spy_vol_3m, length=126)
    vol_signal_126 = vol_signal_126.fillna(method='ffill')

    risk_signal = (vol_signal_126 == -1).astype(int)
    if risk_signal.iloc[-1] == 0:
        print("Volatility risk off is active")

    spy_vol = spy_rets.iloc[-10:].std(ddof=0)
    if spy_vol > danger_spy_vol_thrs:
        print(f"SPY rolling 10d volatility is above {danger_spy_vol_thrs}")

    # ief_signal_252 = make_trend_signal(ief['Adj Close'])
    ief_signal_126 = make_trend_signal(ief_price, length=126)
    shy_signal_126 = make_trend_signal(shy_price, length=126)

    if ief_signal_126.iloc[-1] == 1:
        print("Low yields regime")
    elif ief_signal_126.iloc[-1] == -1:
        print("High yields regime")
    else:
        print("Neutral regime")

    if shy_signal_126.iloc[-1] == 1:
        print("Short term bonds up")

    bonds_regime_signal = pd.Series(0.0, index=ief_signal_126.index)
    bonds_regime_signal[(ief_signal_126 != -1) & (shy_signal_126 == -1)] = 1
    combined_risk_signal = 1 - ((bonds_regime_signal == 0) & (risk_signal == 0)).astype(int)

    if combined_risk_signal.iloc[-1] == 0:
        print("Combined risk off is active")

    # vwap
    length = 5
    vw_price = spy_price * spy['Volume']
    vw_price_cumsum = vw_price.rolling(length).sum()
    volume_cumsum = spy['Volume'].rolling(length).sum()
    VWAP = vw_price_cumsum / volume_cumsum
    offset = np.sqrt(((spy['Volume'] * ((spy_price - VWAP) ** 2)).rolling(length).sum()) / volume_cumsum)
    signal = pd.Series(0, index=spy.index)
    signal[spy['Adj Close'] > VWAP + offset] = -1
    signal[spy['Adj Close'] < VWAP - offset] = 1
    # propagate 1 and -1
    signal = signal.replace(0, np.nan)
    signal = signal.fillna(method='ffill')
    # make long-only sig
    signal = signal.replace(-1, 0).fillna(0)

    if signal.iloc[-1] == 1:
        print("VWAP signal active.")

    print("End of process.")

