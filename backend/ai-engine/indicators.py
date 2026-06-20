import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {"macd": macd_line, "signal": signal_line, "histogram": histogram}


def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    return prices.ewm(span=period, adjust=False).mean()


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / period, min_periods=period).mean()


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return {"upper": upper, "middle": sma, "lower": lower}


def calculate_stochastic(
    high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3
) -> Dict[str, pd.Series]:
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_period).mean()
    return {"k": k, "d": d}


def calculate_volume_profile(
    closes: pd.Series, volumes: pd.Series, bins: int = 20
) -> Dict[str, Any]:
    price_min = closes.min()
    price_max = closes.max()
    price_bins = np.linspace(price_min, price_max, bins + 1)
    volume_profile = np.zeros(bins)
    for i, (price, vol) in enumerate(zip(closes, volumes)):
        bin_idx = np.searchsorted(price_bins, price, side="right") - 1
        if 0 <= bin_idx < bins:
            volume_profile[bin_idx] += vol
    poc_idx = np.argmax(volume_profile)
    poc_price = (price_bins[poc_idx] + price_bins[poc_idx + 1]) / 2
    return {
        "price_bins": price_bins.tolist(),
        "volume_profile": volume_profile.tolist(),
        "poc_price": float(poc_price),
    }


def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    typical_price = (high + low + close) / 3
    return (typical_price * volume).cumsum() / volume.cumsum()


def calculate_supertrend(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 10, multiplier: float = 3.0
) -> Dict[str, pd.Series]:
    atr = calculate_atr(high, low, close, period)
    hl2 = (high + low) / 2
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=close.index, dtype=float)
    direction = pd.Series(index=close.index, dtype=int)

    for i in range(1, len(close)):
        if close.iloc[i] > upper_band.iloc[i - 1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower_band.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]
            if direction.iloc[i] == 1 and lower_band.iloc[i] < lower_band.iloc[i - 1]:
                lower_band.iloc[i] = lower_band.iloc[i - 1]
            if direction.iloc[i] == -1 and upper_band.iloc[i] > upper_band.iloc[i - 1]:
                upper_band.iloc[i] = upper_band.iloc[i - 1]

        supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]

    return {"supertrend": supertrend, "direction": direction}


def calculate_ichimoku(
    high: pd.Series, low: pd.Series, close: pd.Series,
    tenkan: int = 9, kijun: int = 26, senkou_b: int = 52
) -> Dict[str, pd.Series]:
    tenkan_sen = (high.rolling(tenkan).max() + low.rolling(tenkan).min()) / 2
    kijun_sen = (high.rolling(kijun).max() + low.rolling(kijun).min()) / 2
    senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    senkou_b_line = ((high.rolling(senkou_b).max() + low.rolling(senkou_b).min()) / 2).shift(kijun)
    chikou = close.shift(-kijun)
    return {
        "tenkan_sen": tenkan_sen,
        "kijun_sen": kijun_sen,
        "senkou_a": senkou_a,
        "senkou_b": senkou_b_line,
        "chikou": chikou,
    }


def detect_divergence(prices: pd.Series, indicator: pd.Series, window: int = 5) -> Dict[str, List[int]]:
    bullish_divergences = []
    bearish_divergences = []
    for i in range(window, len(prices) - 1):
        price_window = prices.iloc[i - window:i + 1]
        ind_window = indicator.iloc[i - window:i + 1]
        if prices.iloc[i] == price_window.min() and indicator.iloc[i] > ind_window.min():
            bullish_divergences.append(i)
        if prices.iloc[i] == price_window.max() and indicator.iloc[i] < ind_window.max():
            bearish_divergences.append(i)
    return {"bullish": bullish_divergences, "bearish": bearish_divergences}
