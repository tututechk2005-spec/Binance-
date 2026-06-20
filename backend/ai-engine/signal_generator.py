import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from loguru import logger

from .indicators import (
    calculate_rsi, calculate_macd, calculate_ema,
    calculate_atr, calculate_bollinger_bands, calculate_vwap
)
from .smart_money import (
    detect_market_structure, detect_order_blocks,
    detect_fair_value_gaps, detect_liquidity_zones, detect_supply_demand_zones
)
from .risk_management import RiskManager


class SignalGenerator:
    def __init__(self, risk_percent: float = 1.0):
        self.risk_manager = RiskManager(risk_percent)

    def klines_to_dataframe(self, klines: list) -> pd.DataFrame:
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_buy_base",
            "taker_buy_quote", "ignore"
        ])
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.set_index("timestamp")
        return df

    def generate_signal(self, symbol: str, klines: list, timeframe: str = "1h") -> Optional[Dict[str, Any]]:
        try:
            df = self.klines_to_dataframe(klines)
            if len(df) < 100:
                logger.warning(f"Insufficient data for {symbol}: {len(df)} candles")
                return None

            closes = df["close"]
            highs = df["high"]
            lows = df["low"]
            opens = df["open"]
            volumes = df["volume"]
            current_price = float(closes.iloc[-1])

            rsi = calculate_rsi(closes)
            macd_data = calculate_macd(closes)
            ema_20 = calculate_ema(closes, 20)
            ema_50 = calculate_ema(closes, 50)
            ema_200 = calculate_ema(closes, 200)
            atr = calculate_atr(highs, lows, closes)
            bb = calculate_bollinger_bands(closes)
            vwap = calculate_vwap(highs, lows, closes, volumes)

            rsi_val = float(rsi.iloc[-1])
            macd_val = float(macd_data["macd"].iloc[-1])
            macd_sig = float(macd_data["signal"].iloc[-1])
            macd_hist = float(macd_data["histogram"].iloc[-1])
            ema20_val = float(ema_20.iloc[-1])
            ema50_val = float(ema_50.iloc[-1])
            ema200_val = float(ema_200.iloc[-1])
            atr_val = float(atr.iloc[-1])
            bb_upper = float(bb["upper"].iloc[-1])
            bb_lower = float(bb["lower"].iloc[-1])
            vwap_val = float(vwap.iloc[-1])

            market_structure = detect_market_structure(highs, lows, closes)
            order_blocks = detect_order_blocks(opens, highs, lows, closes)
            fvgs = detect_fair_value_gaps(highs, lows, closes)
            liquidity = detect_liquidity_zones(highs, lows, closes)
            supply_demand = detect_supply_demand_zones(opens, highs, lows, closes)

            trend = market_structure.get("trend", "sideways")
            bos_events = market_structure.get("bos", [])
            choch_events = market_structure.get("choch", [])

            buy_score = 0
            sell_score = 0
            max_score = 100

            if rsi_val < 30:
                buy_score += 15
            elif rsi_val < 50:
                buy_score += 8
            elif rsi_val > 70:
                sell_score += 15
            elif rsi_val > 50:
                sell_score += 8

            if macd_val > macd_sig and macd_hist > 0:
                buy_score += 15
            elif macd_val < macd_sig and macd_hist < 0:
                sell_score += 15

            if current_price > ema20_val > ema50_val > ema200_val:
                buy_score += 20
            elif current_price < ema20_val < ema50_val < ema200_val:
                sell_score += 20
            elif current_price > ema200_val:
                buy_score += 10
            else:
                sell_score += 10

            if current_price < bb_lower:
                buy_score += 10
            elif current_price > bb_upper:
                sell_score += 10

            if current_price > vwap_val:
                buy_score += 5
            else:
                sell_score += 5

            if trend == "uptrend":
                buy_score += 15
            elif trend == "downtrend":
                sell_score += 15

            if any(b["type"] == "BOS_BULLISH" for b in bos_events):
                buy_score += 10
            if any(b["type"] == "BOS_BEARISH" for b in bos_events):
                sell_score += 10
            if any(c["type"] == "CHOCH_BULLISH" for c in choch_events):
                buy_score += 10
            if any(c["type"] == "CHOCH_BEARISH" for c in choch_events):
                sell_score += 10

            demand_nearby = any(
                z["bottom"] <= current_price <= z["top"] * 1.02
                for z in supply_demand.get("demand", [])
            )
            supply_nearby = any(
                z["bottom"] * 0.98 <= current_price <= z["top"]
                for z in supply_demand.get("supply", [])
            )
            if demand_nearby:
                buy_score += 10
            if supply_nearby:
                sell_score += 10

            bullish_fvg = any(
                f["bottom"] <= current_price <= f["top"] * 1.01
                for f in fvgs.get("bullish", [])
            )
            bearish_fvg = any(
                f["bottom"] * 0.99 <= current_price <= f["top"]
                for f in fvgs.get("bearish", [])
            )
            if bullish_fvg:
                buy_score += 5
            if bearish_fvg:
                sell_score += 5

            if buy_score <= sell_score and buy_score < 50:
                logger.debug(f"No signal for {symbol}: buy={buy_score}, sell={sell_score}")
                return None

            signal_type = "BUY" if buy_score > sell_score else "SELL"
            confidence = min(
                round((max(buy_score, sell_score) / max_score) * 100, 2),
                99.0
            )

            if confidence < 60:
                return None

            sl_distance = atr_val * 1.5
            tp1_distance = atr_val * 2.0
            tp2_distance = atr_val * 3.5
            tp3_distance = atr_val * 5.0

            if signal_type == "BUY":
                stop_loss = round(current_price - sl_distance, 8)
                take_profit_1 = round(current_price + tp1_distance, 8)
                take_profit_2 = round(current_price + tp2_distance, 8)
                take_profit_3 = round(current_price + tp3_distance, 8)
            else:
                stop_loss = round(current_price + sl_distance, 8)
                take_profit_1 = round(current_price - tp1_distance, 8)
                take_profit_2 = round(current_price - tp2_distance, 8)
                take_profit_3 = round(current_price - tp3_distance, 8)

            rr_ratio = round(abs(take_profit_1 - current_price) / abs(stop_loss - current_price), 2)

            return {
                "symbol": symbol,
                "signal_type": signal_type,
                "confidence_score": confidence,
                "entry_price": current_price,
                "stop_loss": stop_loss,
                "take_profit_1": take_profit_1,
                "take_profit_2": take_profit_2,
                "take_profit_3": take_profit_3,
                "timeframe": timeframe,
                "risk_reward_ratio": rr_ratio,
                "indicators": {
                    "rsi": rsi_val,
                    "macd": macd_val,
                    "macd_signal": macd_sig,
                    "macd_histogram": macd_hist,
                    "ema_20": ema20_val,
                    "ema_50": ema50_val,
                    "ema_200": ema200_val,
                    "atr": atr_val,
                    "bb_upper": bb_upper,
                    "bb_lower": bb_lower,
                    "vwap": vwap_val,
                },
                "market_structure": trend,
                "trend": trend,
                "bos_detected": len(bos_events) > 0,
                "choch_detected": len(choch_events) > 0,
                "liquidity_zones": liquidity,
                "order_blocks": order_blocks,
                "fair_value_gaps": fvgs,
                "smart_money_concepts": {
                    "bos": bos_events,
                    "choch": choch_events,
                    "demand_zone_nearby": demand_nearby,
                    "supply_zone_nearby": supply_nearby,
                    "bullish_fvg": bullish_fvg,
                    "bearish_fvg": bearish_fvg,
                },
                "analysis_data": {
                    "buy_score": buy_score,
                    "sell_score": sell_score,
                },
            }
        except Exception as e:
            logger.error(f"Signal generation error for {symbol}: {e}")
            return None


WATCHED_PAIRS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT",
    "LINKUSDT", "LTCUSDT", "UNIUSDT", "ATOMUSDT", "FILUSDT",
    "NEARUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "INJUSDT",
]
