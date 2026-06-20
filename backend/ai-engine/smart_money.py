import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional


def detect_market_structure(
    highs: pd.Series, lows: pd.Series, closes: pd.Series
) -> Dict[str, Any]:
    swing_highs = _find_swing_highs(highs, window=5)
    swing_lows = _find_swing_lows(lows, window=5)
    trend = _determine_trend(swing_highs, swing_lows, closes)
    bos_events = _detect_bos(swing_highs, swing_lows, closes, trend)
    choch_events = _detect_choch(swing_highs, swing_lows, closes, trend)
    return {
        "trend": trend,
        "swing_highs": swing_highs,
        "swing_lows": swing_lows,
        "bos": bos_events,
        "choch": choch_events,
    }


def _find_swing_highs(highs: pd.Series, window: int = 5) -> List[Dict]:
    swing_highs = []
    for i in range(window, len(highs) - window):
        if highs.iloc[i] == highs.iloc[i - window:i + window + 1].max():
            swing_highs.append({"index": i, "price": float(highs.iloc[i])})
    return swing_highs


def _find_swing_lows(lows: pd.Series, window: int = 5) -> List[Dict]:
    swing_lows = []
    for i in range(window, len(lows) - window):
        if lows.iloc[i] == lows.iloc[i - window:i + window + 1].min():
            swing_lows.append({"index": i, "price": float(lows.iloc[i])})
    return swing_lows


def _determine_trend(swing_highs: List[Dict], swing_lows: List[Dict], closes: pd.Series) -> str:
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return "sideways"
    last_highs = swing_highs[-3:] if len(swing_highs) >= 3 else swing_highs
    last_lows = swing_lows[-3:] if len(swing_lows) >= 3 else swing_lows
    higher_highs = all(last_highs[i]["price"] < last_highs[i + 1]["price"] for i in range(len(last_highs) - 1))
    higher_lows = all(last_lows[i]["price"] < last_lows[i + 1]["price"] for i in range(len(last_lows) - 1))
    lower_highs = all(last_highs[i]["price"] > last_highs[i + 1]["price"] for i in range(len(last_highs) - 1))
    lower_lows = all(last_lows[i]["price"] > last_lows[i + 1]["price"] for i in range(len(last_lows) - 1))
    if higher_highs and higher_lows:
        return "uptrend"
    elif lower_highs and lower_lows:
        return "downtrend"
    return "sideways"


def _detect_bos(swing_highs, swing_lows, closes, trend) -> List[Dict]:
    bos_events = []
    if trend == "uptrend" and len(swing_highs) >= 2:
        prev_high = swing_highs[-2]["price"]
        for i in range(swing_highs[-2]["index"], len(closes)):
            if closes.iloc[i] > prev_high:
                bos_events.append({
                    "type": "BOS_BULLISH",
                    "index": i,
                    "price": float(closes.iloc[i]),
                    "broken_level": prev_high,
                })
                break
    elif trend == "downtrend" and len(swing_lows) >= 2:
        prev_low = swing_lows[-2]["price"]
        for i in range(swing_lows[-2]["index"], len(closes)):
            if closes.iloc[i] < prev_low:
                bos_events.append({
                    "type": "BOS_BEARISH",
                    "index": i,
                    "price": float(closes.iloc[i]),
                    "broken_level": prev_low,
                })
                break
    return bos_events


def _detect_choch(swing_highs, swing_lows, closes, trend) -> List[Dict]:
    choch_events = []
    if trend == "uptrend" and len(swing_lows) >= 2:
        last_low = swing_lows[-1]["price"]
        prev_low = swing_lows[-2]["price"]
        if last_low < prev_low:
            choch_events.append({
                "type": "CHOCH_BEARISH",
                "index": swing_lows[-1]["index"],
                "price": last_low,
                "description": "Change of character: uptrend broken",
            })
    elif trend == "downtrend" and len(swing_highs) >= 2:
        last_high = swing_highs[-1]["price"]
        prev_high = swing_highs[-2]["price"]
        if last_high > prev_high:
            choch_events.append({
                "type": "CHOCH_BULLISH",
                "index": swing_highs[-1]["index"],
                "price": last_high,
                "description": "Change of character: downtrend broken",
            })
    return choch_events


def detect_order_blocks(
    opens: pd.Series, highs: pd.Series, lows: pd.Series, closes: pd.Series, lookback: int = 50
) -> Dict[str, List[Dict]]:
    bullish_obs = []
    bearish_obs = []
    df = pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes})
    recent = df.tail(lookback)
    for i in range(2, len(recent) - 2):
        candle = recent.iloc[i]
        next_candle = recent.iloc[i + 1]
        if candle["close"] < candle["open"] and next_candle["close"] > next_candle["open"]:
            if next_candle["close"] > candle["high"]:
                bullish_obs.append({
                    "index": recent.index[i],
                    "top": float(candle["open"]),
                    "bottom": float(candle["close"]),
                    "type": "bullish",
                    "strength": float((next_candle["close"] - candle["low"]) / candle["high"] * 100),
                })
        if candle["close"] > candle["open"] and next_candle["close"] < next_candle["open"]:
            if next_candle["close"] < candle["low"]:
                bearish_obs.append({
                    "index": recent.index[i],
                    "top": float(candle["close"]),
                    "bottom": float(candle["open"]),
                    "type": "bearish",
                    "strength": float((candle["high"] - next_candle["close"]) / candle["low"] * 100),
                })
    return {"bullish": bullish_obs[-5:], "bearish": bearish_obs[-5:]}


def detect_fair_value_gaps(
    highs: pd.Series, lows: pd.Series, closes: pd.Series, lookback: int = 50
) -> Dict[str, List[Dict]]:
    bullish_fvgs = []
    bearish_fvgs = []
    for i in range(1, min(lookback, len(highs) - 1)):
        idx = len(highs) - lookback + i
        if idx < 2:
            continue
        prev_candle_high = highs.iloc[idx - 2]
        current_candle_low = lows.iloc[idx]
        prev_candle_low = lows.iloc[idx - 2]
        current_candle_high = highs.iloc[idx]
        if current_candle_low > prev_candle_high:
            bullish_fvgs.append({
                "top": float(current_candle_low),
                "bottom": float(prev_candle_high),
                "index": idx,
                "type": "bullish",
                "size": float(current_candle_low - prev_candle_high),
            })
        if current_candle_high < prev_candle_low:
            bearish_fvgs.append({
                "top": float(prev_candle_low),
                "bottom": float(current_candle_high),
                "index": idx,
                "type": "bearish",
                "size": float(prev_candle_low - current_candle_high),
            })
    return {"bullish": bullish_fvgs[-5:], "bearish": bearish_fvgs[-5:]}


def detect_liquidity_zones(
    highs: pd.Series, lows: pd.Series, closes: pd.Series, lookback: int = 100
) -> Dict[str, List[Dict]]:
    recent_highs = highs.tail(lookback)
    recent_lows = lows.tail(lookback)
    swing_highs_prices = []
    swing_lows_prices = []
    for i in range(3, len(recent_highs) - 3):
        if recent_highs.iloc[i] == recent_highs.iloc[i - 3:i + 4].max():
            swing_highs_prices.append(float(recent_highs.iloc[i]))
        if recent_lows.iloc[i] == recent_lows.iloc[i - 3:i + 4].min():
            swing_lows_prices.append(float(recent_lows.iloc[i]))
    buyside_liquidity = [{"price": p, "type": "buyside", "strength": "high"} for p in swing_highs_prices[-5:]]
    sellside_liquidity = [{"price": p, "type": "sellside", "strength": "high"} for p in swing_lows_prices[-5:]]
    current_price = float(closes.iloc[-1])
    premium_zone = float(closes.tail(lookback).quantile(0.75))
    discount_zone = float(closes.tail(lookback).quantile(0.25))
    equilibrium = float(closes.tail(lookback).median())
    return {
        "buyside": buyside_liquidity,
        "sellside": sellside_liquidity,
        "premium_zone": premium_zone,
        "discount_zone": discount_zone,
        "equilibrium": equilibrium,
        "current_price": current_price,
        "is_premium": current_price > equilibrium,
        "is_discount": current_price < equilibrium,
    }


def detect_supply_demand_zones(
    opens: pd.Series, highs: pd.Series, lows: pd.Series, closes: pd.Series, lookback: int = 100
) -> Dict[str, List[Dict]]:
    supply_zones = []
    demand_zones = []
    for i in range(2, min(lookback, len(closes)) - 2):
        idx = len(closes) - min(lookback, len(closes)) + i
        candle_body = abs(closes.iloc[idx] - opens.iloc[idx])
        candle_range = highs.iloc[idx] - lows.iloc[idx]
        if candle_range == 0:
            continue
        body_ratio = candle_body / candle_range
        if body_ratio > 0.6:
            if closes.iloc[idx] < opens.iloc[idx]:
                supply_zones.append({
                    "top": float(max(opens.iloc[idx], closes.iloc[idx])),
                    "bottom": float(min(opens.iloc[idx], closes.iloc[idx])),
                    "strength": float(body_ratio),
                    "index": idx,
                })
            elif closes.iloc[idx] > opens.iloc[idx]:
                demand_zones.append({
                    "top": float(max(opens.iloc[idx], closes.iloc[idx])),
                    "bottom": float(min(opens.iloc[idx], closes.iloc[idx])),
                    "strength": float(body_ratio),
                    "index": idx,
                })
    return {"supply": supply_zones[-5:], "demand": demand_zones[-5:]}
