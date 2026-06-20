import { Signal } from "@/types";
import { TrendingUp, TrendingDown, Target, Shield, Zap } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface Props {
  signal: Signal;
  compact?: boolean;
}

export default function SignalCard({ signal, compact }: Props) {
  const isBuy = signal.signal_type === "BUY";
  const confColor = signal.confidence_score >= 80 ? "text-buy-DEFAULT" : signal.confidence_score >= 70 ? "text-gold-DEFAULT" : "text-sell-DEFAULT";

  if (compact) {
    return (
      <div className="flex items-center justify-between p-3 bg-[#131720] rounded-lg border border-[#2b2f36] hover:border-[#3d4249] transition-colors">
        <div className="flex items-center gap-2.5">
          <div className={`w-7 h-7 rounded-md flex items-center justify-center ${isBuy ? "bg-buy-DEFAULT/15" : "bg-sell-DEFAULT/15"}`}>
            {isBuy ? <TrendingUp size={13} className="text-buy-DEFAULT" /> : <TrendingDown size={13} className="text-sell-DEFAULT" />}
          </div>
          <div>
            <div className="text-sm font-semibold text-white">{signal.symbol}</div>
            <div className="text-xs text-gray-500">{signal.timeframe}</div>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-xs font-bold ${isBuy ? "badge-buy" : "badge-sell"}`}>{signal.signal_type}</div>
          <div className={`text-xs font-semibold mt-1 ${confColor}`}>{signal.confidence_score}%</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`card-dark p-5 border ${isBuy ? "border-buy-DEFAULT/30 hover:border-buy-DEFAULT/50" : "border-sell-DEFAULT/30 hover:border-sell-DEFAULT/50"} transition-colors`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isBuy ? "bg-buy-DEFAULT/15" : "bg-sell-DEFAULT/15"}`}>
            {isBuy ? <TrendingUp size={18} className="text-buy-DEFAULT" /> : <TrendingDown size={18} className="text-sell-DEFAULT" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-white">{signal.symbol}</span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded ${isBuy ? "badge-buy" : "badge-sell"}`}>{signal.signal_type}</span>
            </div>
            <div className="text-xs text-gray-500 mt-0.5">{signal.timeframe} • {formatDistanceToNow(new Date(signal.created_at), { addSuffix: true })}</div>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-xl font-bold font-mono ${confColor}`}>{signal.confidence_score}%</div>
          <div className="text-xs text-gray-500 mt-0.5">confidence</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-[#131720] rounded-lg p-3">
          <div className="text-xs text-gray-500 mb-1">Entry</div>
          <div className="text-sm font-mono font-semibold text-white">${signal.entry_price?.toFixed(4)}</div>
        </div>
        <div className="bg-[#131720] rounded-lg p-3">
          <div className="text-xs text-gray-500 mb-1 flex items-center gap-1"><Shield size={10} /> Stop Loss</div>
          <div className="text-sm font-mono font-semibold text-sell-DEFAULT">${signal.stop_loss?.toFixed(4)}</div>
        </div>
        <div className="bg-[#131720] rounded-lg p-3">
          <div className="text-xs text-gray-500 mb-1 flex items-center gap-1"><Target size={10} /> TP1</div>
          <div className="text-sm font-mono font-semibold text-buy-DEFAULT">${signal.take_profit_1?.toFixed(4)}</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {signal.bos_detected && <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded font-medium">BOS</span>}
        {signal.choch_detected && <span className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-400 rounded font-medium">CHOCH</span>}
        {signal.trend && <span className="px-2 py-0.5 text-xs bg-[#2b2f36] text-gray-300 rounded font-medium capitalize">{signal.trend}</span>}
        {signal.risk_reward_ratio && <span className="px-2 py-0.5 text-xs bg-gold-DEFAULT/20 text-gold-DEFAULT rounded font-medium">R:R {signal.risk_reward_ratio}</span>}
        {signal.indicators?.rsi && <span className="px-2 py-0.5 text-xs bg-[#2b2f36] text-gray-300 rounded font-mono">RSI {signal.indicators.rsi.toFixed(1)}</span>}
      </div>
    </div>
  );
}
