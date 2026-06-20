import { useQuery } from "@tanstack/react-query";
import { portfolioApi, signalsApi, tradesApi } from "@/services/api";
import { useAuthStore } from "@/store/authStore";
import { TrendingUp, TrendingDown, Zap, BarChart3, Activity, Target, Award, DollarSign } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { format } from "date-fns";
import SignalCard from "@/components/signals/SignalCard";
import TradeRow from "@/components/trading/TradeRow";

export default function DashboardPage() {
  const { user } = useAuthStore();

  const { data: overview } = useQuery({
    queryKey: ["portfolio-overview"],
    queryFn: () => portfolioApi.getOverview().then(r => r.data),
    refetchInterval: 30000,
  });

  const { data: pnlHistory } = useQuery({
    queryKey: ["pnl-history"],
    queryFn: () => portfolioApi.getPnlHistory(30).then(r => r.data),
    refetchInterval: 60000,
  });

  const { data: signalsData } = useQuery({
    queryKey: ["signals-active"],
    queryFn: () => signalsApi.getLatestActive(5).then(r => r.data),
    refetchInterval: 60000,
  });

  const { data: tradesData } = useQuery({
    queryKey: ["trades-recent"],
    queryFn: () => tradesApi.getTrades({ per_page: 5 }).then(r => r.data),
    refetchInterval: 30000,
  });

  const { data: performance } = useQuery({
    queryKey: ["performance"],
    queryFn: () => portfolioApi.getPerformance().then(r => r.data),
  });

  const stats = [
    { label: "Total PNL", value: `${(overview?.total_pnl || 0) >= 0 ? "+" : ""}$${(overview?.total_pnl || 0).toFixed(2)}`, icon: DollarSign, positive: (overview?.total_pnl || 0) >= 0 },
    { label: "Open Trades", value: overview?.open_trades || 0, icon: Activity, positive: true },
    { label: "Win Rate", value: `${overview?.win_rate || 0}%`, icon: Target, positive: true },
    { label: "Total Return", value: `${(performance?.total_return || 0) >= 0 ? "+" : ""}${(performance?.total_return || 0).toFixed(4)}`, icon: Award, positive: (performance?.total_return || 0) >= 0 },
  ];

  const chartData = pnlHistory?.map((d: any) => ({
    date: format(new Date(d.date), "MMM dd"),
    pnl: d.pnl,
    cumulative: 0,
  })) || [];
  let cum = 0;
  chartData.forEach((d: any) => { cum += d.pnl; d.cumulative = parseFloat(cum.toFixed(4)); });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-0.5">Welcome back, {user?.username}</p>
        </div>
        {user?.auto_trading_enabled && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-buy-DEFAULT/15 border border-buy-DEFAULT/30 rounded-full">
            <div className="w-2 h-2 rounded-full bg-buy-DEFAULT animate-pulse" />
            <span className="text-sm text-buy-DEFAULT font-medium">Auto Trading Active</span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, icon: Icon, positive }) => (
          <div key={label} className="stat-card">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-gray-500 font-medium uppercase tracking-wider">{label}</span>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${positive ? "bg-buy-DEFAULT/15" : "bg-sell-DEFAULT/15"}`}>
                <Icon size={15} className={positive ? "text-buy-DEFAULT" : "text-sell-DEFAULT"} />
              </div>
            </div>
            <div className={`text-2xl font-bold font-mono ${typeof value === "string" && value.startsWith("-") ? "text-sell-DEFAULT" : typeof value === "string" && value.startsWith("+") ? "text-buy-DEFAULT" : "text-white"}`}>
              {value}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* PNL Chart */}
        <div className="xl:col-span-2 card-dark p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white flex items-center gap-2">
              <BarChart3 size={16} className="text-gold-DEFAULT" /> Cumulative PNL (30 days)
            </h2>
          </div>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="pnlGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ecb81" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#0ecb81" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2b2f36" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#6b7280" }} />
                <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} />
                <Tooltip contentStyle={{ background: "#1e2026", border: "1px solid #2b2f36", borderRadius: "8px", color: "#fff", fontSize: "12px" }} />
                <Area type="monotone" dataKey="cumulative" stroke="#0ecb81" fill="url(#pnlGrad)" strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-56 flex items-center justify-center text-gray-500 text-sm">No trade history yet</div>
          )}
        </div>

        {/* Active Signals */}
        <div className="card-dark p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white flex items-center gap-2">
              <Zap size={16} className="text-gold-DEFAULT" /> Active Signals
            </h2>
          </div>
          <div className="space-y-3">
            {signalsData?.length > 0 ? (
              signalsData.slice(0, 4).map((s: any) => (
                <SignalCard key={s.id} signal={s} compact />
              ))
            ) : (
              <div className="text-center py-8 text-gray-500 text-sm">No active signals</div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Trades */}
      <div className="card-dark p-5">
        <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
          <Activity size={16} className="text-gold-DEFAULT" /> Recent Trades
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 border-b border-[#2b2f36]">
                <th className="text-left pb-3 font-medium">Symbol</th>
                <th className="text-left pb-3 font-medium">Type</th>
                <th className="text-right pb-3 font-medium">Entry</th>
                <th className="text-right pb-3 font-medium">Qty</th>
                <th className="text-right pb-3 font-medium">PNL</th>
                <th className="text-center pb-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {tradesData?.trades?.length > 0 ? (
                tradesData.trades.map((t: any) => <TradeRow key={t.id} trade={t} />)
              ) : (
                <tr><td colSpan={6} className="text-center py-8 text-gray-500">No trades yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance metrics */}
      {performance && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { label: "Total Trades", value: performance.total_trades },
            { label: "Win Rate", value: `${performance.win_rate}%` },
            { label: "Avg Win", value: `+$${performance.avg_win?.toFixed(2)}` },
            { label: "Avg Loss", value: `$${performance.avg_loss?.toFixed(2)}` },
            { label: "Profit Factor", value: performance.profit_factor?.toFixed(2) },
            { label: "Max Drawdown", value: `${performance.max_drawdown}%` },
          ].map(({ label, value }) => (
            <div key={label} className="stat-card text-center">
              <div className="text-lg font-bold font-mono text-white">{value}</div>
              <div className="text-xs text-gray-500 mt-1">{label}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
