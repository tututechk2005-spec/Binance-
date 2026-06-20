from typing import Dict, Any, Optional
import math


class RiskManager:
    def __init__(self, risk_percent: float = 1.0):
        self.risk_percent = min(max(risk_percent, 0.1), 5.0)

    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss: float,
        leverage: int = 1,
    ) -> Dict[str, float]:
        risk_amount = account_balance * (self.risk_percent / 100)
        price_diff = abs(entry_price - stop_loss)
        if price_diff == 0:
            return {"quantity": 0, "risk_amount": 0, "position_value": 0}
        raw_qty = (risk_amount * leverage) / price_diff
        quantity = math.floor(raw_qty * 1000) / 1000
        position_value = quantity * entry_price / leverage
        return {
            "quantity": quantity,
            "risk_amount": round(risk_amount, 4),
            "position_value": round(position_value, 4),
            "margin_required": round(position_value / leverage, 4),
            "risk_percent": self.risk_percent,
        }

    def validate_trade(
        self,
        account_balance: float,
        position_value: float,
        leverage: int = 1,
        max_position_percent: float = 20.0,
    ) -> Dict[str, Any]:
        margin = position_value / leverage
        margin_percent = (margin / account_balance) * 100
        is_valid = margin_percent <= max_position_percent
        return {
            "is_valid": is_valid,
            "margin_percent": round(margin_percent, 2),
            "max_position_percent": max_position_percent,
            "reason": None if is_valid else f"Position size {margin_percent:.1f}% exceeds limit {max_position_percent}%",
        }

    def calculate_breakeven(
        self, entry_price: float, fee_rate: float = 0.001, side: str = "BUY"
    ) -> float:
        if side == "BUY":
            return round(entry_price * (1 + fee_rate * 2), 8)
        return round(entry_price * (1 - fee_rate * 2), 8)

    def calculate_trailing_stop(
        self,
        current_price: float,
        highest_price: float,
        trail_percent: float = 2.0,
        side: str = "BUY",
    ) -> float:
        if side == "BUY":
            return round(highest_price * (1 - trail_percent / 100), 8)
        return round(lowest_price * (1 + trail_percent / 100), 8)

    def calculate_partial_take_profit(
        self,
        entry_price: float,
        take_profits: list,
        quantities: list,
    ) -> list:
        result = []
        for tp, qty in zip(take_profits, quantities):
            profit = (tp - entry_price) * qty
            result.append({
                "price": tp,
                "quantity": qty,
                "expected_profit": round(profit, 4),
            })
        return result

    def assess_risk_level(
        self,
        confidence: float,
        rr_ratio: float,
        trend: str,
        account_balance: float,
        open_positions_count: int,
    ) -> Dict[str, Any]:
        risk_score = 0
        if confidence >= 80:
            risk_score += 3
        elif confidence >= 70:
            risk_score += 2
        else:
            risk_score += 1

        if rr_ratio >= 3:
            risk_score += 3
        elif rr_ratio >= 2:
            risk_score += 2
        else:
            risk_score += 1

        if trend in ("uptrend", "downtrend"):
            risk_score += 2
        else:
            risk_score += 0

        if open_positions_count < 3:
            risk_score += 2
        elif open_positions_count < 5:
            risk_score += 1

        if risk_score >= 8:
            level = "LOW"
            suggested_risk = self.risk_percent
        elif risk_score >= 5:
            level = "MEDIUM"
            suggested_risk = self.risk_percent * 0.75
        else:
            level = "HIGH"
            suggested_risk = self.risk_percent * 0.5

        return {
            "risk_level": level,
            "risk_score": risk_score,
            "suggested_risk_percent": round(suggested_risk, 2),
            "max_concurrent_trades": 5 if level == "LOW" else 3 if level == "MEDIUM" else 1,
        }


def calculate_max_drawdown(pnl_history: list) -> float:
    if not pnl_history:
        return 0.0
    peak = pnl_history[0]
    max_dd = 0.0
    for pnl in pnl_history:
        if pnl > peak:
            peak = pnl
        dd = (peak - pnl) / peak if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
    return round(max_dd * 100, 2)


def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.02) -> float:
    import numpy as np
    if len(returns) < 2:
        return 0.0
    arr = np.array(returns)
    excess = arr - risk_free_rate / 252
    if arr.std() == 0:
        return 0.0
    return round(float(excess.mean() / arr.std() * math.sqrt(252)), 4)


def calculate_win_rate(trades: list) -> Dict[str, float]:
    if not trades:
        return {"win_rate": 0, "total_trades": 0, "wins": 0, "losses": 0}
    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    losses = len(trades) - wins
    return {
        "win_rate": round(wins / len(trades) * 100, 2),
        "total_trades": len(trades),
        "wins": wins,
        "losses": losses,
        "profit_factor": round(
            sum(t["pnl"] for t in trades if t.get("pnl", 0) > 0) /
            abs(sum(t["pnl"] for t in trades if t.get("pnl", 0) < 0) or 1),
            2
        ),
    }
