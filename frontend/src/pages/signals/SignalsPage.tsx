import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { signalsApi } from "@/services/api";
import SignalCard from "@/components/signals/SignalCard";
import { Zap, TrendingUp, TrendingDown, Filter } from "lucide-react";

const TIMEFRAMES = ["", "15m", "30m", "1h", "4h", "1d"];
const TYPES = ["", "BUY", "SELL"];

export default function SignalsPage() {
  const [type, setType] = useState("");
  const [timeframe, setTimeframe] = useState("");
  const [minConf, setMinConf] = useState(60);
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["signals", { type, timeframe, minConf, page }],
    queryFn: () => signalsApi.getSignals({
      signal_type: type || undefined,
      timeframe: timeframe || undefined,
      min_confidence: minConf,
      page,
      per_page: 12,
    }).then(r => r.data),
    refetchInterval: 60000,
  });

  const { data: stats } = useQuery({
    queryKey: ["signal-stats"],
    queryFn: () => signalsApi.getStats().then(r => r.data),
    refetchInterval: 60000,
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Zap className="text-gold-DEFAULT" size={22} /> AI Signals
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">Real-time AI-generated trading signals</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total Signals", value: stats?.total_signals || 0, icon: Zap },
          { label: "Active", value: stats?.active_signals || 0, icon: Zap, color: "text-buy-DEFAULT" },
          { label: "BUY Signals", value: stats?.buy_signals || 0, icon: TrendingUp, color: "text-buy-DEFAULT" },
          { label: "SELL Signals", value: stats?.sell_signals || 0, icon: TrendingDown, color: "text-sell-DEFAULT" },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="stat-card">
            <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">{label}</div>
            <div className={`text-2xl font-bold font-mono ${color || "text-white"}`}>{value}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="card-dark p-4 flex flex-wrap gap-3 items-center">
        <Filter size={15} className="text-gray-500" />
        <select value={type} onChange={e => { setType(e.target.value); setPage(1); }} className="input-dark w-32">
          <option value="">All Types</option>
          {TYPES.filter(Boolean).map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select value={timeframe} onChange={e => { setTimeframe(e.target.value); setPage(1); }} className="input-dark w-32">
          <option value="">All TFs</option>
          {TIMEFRAMES.filter(Boolean).map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-500">Min Confidence:</label>
          <input type="number" min={0} max={100} value={minConf} onChange={e => { setMinConf(Number(e.target.value)); setPage(1); }} className="input-dark w-20" />
          <span className="text-xs text-gray-500">%</span>
        </div>
        <div className="ml-auto text-xs text-gray-500">{data?.total || 0} signals found</div>
      </div>

      {/* Signals Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array(6).fill(0).map((_, i) => (
            <div key={i} className="card-dark p-5 h-52 animate-pulse">
              <div className="h-4 bg-[#2b2f36] rounded w-1/2 mb-3" />
              <div className="h-3 bg-[#2b2f36] rounded w-3/4 mb-2" />
              <div className="h-3 bg-[#2b2f36] rounded w-1/3" />
            </div>
          ))}
        </div>
      ) : (
        <>
          {data?.signals?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {data.signals.map((s: any) => <SignalCard key={s.id} signal={s} />)}
            </div>
          ) : (
            <div className="card-dark p-16 text-center">
              <Zap size={48} className="text-gray-600 mx-auto mb-4" />
              <div className="text-gray-400 font-medium">No signals match your filters</div>
              <div className="text-gray-600 text-sm mt-1">Try adjusting the filters above</div>
            </div>
          )}

          {data?.pages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="btn-secondary disabled:opacity-40 px-3 py-1.5 text-sm">← Prev</button>
              <span className="text-sm text-gray-400">Page {page} of {data.pages}</span>
              <button disabled={page === data.pages} onClick={() => setPage(p => p + 1)} className="btn-secondary disabled:opacity-40 px-3 py-1.5 text-sm">Next →</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
