import { useQuery } from "@tanstack/react-query";
import { portfolioApi } from "@/services/api";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Briefcase, TrendingUp, Target, Award, BarChart3, DollarSign } from "lucide-react";
import { format } from "date-fns";

const COLORS = ["#0ecb81", "#f0b90b", "#3b82f6", "#8b5cf6", "#f6465d", "#06b6d4"];

export default function PortfolioPage() {
  const { data: overview } = useQuery({
    queryKey: ["portfolio-overview"],
    queryFn: () => portfolioApi.getOverview().then(r => r.data),
    refetchInterval: 30000,
  });

  const { data: pnlHistory } = useQuery({
    queryKey: ["pnl-history-90"],
    queryFn: () => portfolioApi.getPnlHistory(90).then(r => r.data),
  });

  const { data: balances } = useQuery({
    queryKey: ["balances"],
    queryFn: () => portfolioApi.getBalances().then(r => r.data),
    refetchInterval: 60000,
  });

  const { data: performance } = useQuery({
    queryKey: ["performance"],
    queryFn: () => portfolioApi.getPerformance().then(r => r.data),
  });

  const chartData = pnlHistory?.map((d: any) => ({
    date: format(new Date(d.date), "MMM dd"),
    pnl: d.pnl,
  })) || [];

  let cum = 0;
  const cumulativeData = chartData.map((d: any) => { cum += d.pnl; return { ...d, cumulative: parseFloat(cum.toFixed(4)) }; });

  const allBalances = balances?.flatMap((b: any) => b.balances || []) || [];
  const pieData = allBalances.slice(0, 6).map((b: any) => ({
    name: b.asset || b.balance,
    value: parseFloat(b.free || b.balance || "0"),
  })).filter((d: any) => d.value > 0);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Briefcase className="text-gold-DEFAULT" size={22} /> Portfolio
        </h1>
        <p className="text-gray-500 text-sm mt-0.5">Your complete portfolio overview and analytics</p>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total PNL", value: `${(overview?.total_pnl || 0) >= 0 ? "+" : ""}$${(overview?.total_pnl || 0).toFixed(4)}`, icon: DollarSign, color: (overview?.total_pnl || 0) >= 0 ? "text-buy-DEFAULT" : "text-sell-DEFAULT" },
          { label: "Win Rate", value: `${overview?.win_rate || 0}%`, icon: Target, color: "text-gold-DEFAULT" },
          { label: "Total Trades", value: (overview?.open_trades || 0) + (overview?.closed_trades || 0), icon: BarChart3, color: "text-white" },
          { label: "Profit Factor", value: performance?.profit_factor?.toFixed(2) || "—", icon: Award, color: "text-buy-DEFAULT" },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="stat-card">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-gray-500 uppercase tracking-wider">{label}</span>
              <Icon size={15} className="text-gray-600" />
            </div>
            <div className={`text-2xl font-bold font-mono ${color}`}>{value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Cumulative PNL */}
        <div className="xl:col-span-2 card-dark p-5">
          <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp size={16} className="text-gold-DEFAULT" /> PNL Chart (90 days)
          </h2>
          {cumulativeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={cumulativeData}>
                <defs>
                  <linearGradient id="cumGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ecb81" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#0ecb81" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2b2f36" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6b7280" }} />
                <YAxis tick={{ fontSize: 10, fill: "#6b7280" }} />
                <Tooltip contentStyle={{ background: "#1e2026", border: "1px solid #2b2f36", borderRadius: "8px", color: "#fff", fontSize: "12px" }} />
                <Area type="monotone" dataKey="cumulative" stroke="#0ecb81" fill="url(#cumGrad)" strokeWidth={2} dot={false} name="Cumulative PNL" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-60 flex items-center justify-center text-gray-500 text-sm">No trade history yet</div>
          )}
        </div>

        {/* Asset allocation */}
        <div className="card-dark p-5">
          <h2 className="font-semibold text-white mb-4">Asset Allocation</h2>
          {pieData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3} dataKey="value">
                    {pieData.map((_: any, i: number) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1e2026", border: "1px solid #2b2f36", borderRadius: "8px", color: "#fff", fontSize: "12px" }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-2">
                {pieData.map((d: any, i: number) => (
                  <div key={d.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                      <span className="text-gray-300">{d.name}</span>
                    </div>
                    <span className="font-mono text-xs text-gray-400">{d.value.toFixed(4)}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="h-48 flex items-center justify-center text-gray-500 text-sm text-center">
              Connect & verify API keys<br />to see balances
            </div>
          )}
        </div>
      </div>

      {/* Balances */}
      {balances && balances.length > 0 && (
        <div className="card-dark p-5">
          <h2 className="font-semibold text-white mb-4">Binance Balances</h2>
          {balances.map((kb: any) => (
            <div key={kb.key_label} className="mb-4">
              <div className="text-sm text-gray-400 mb-2 font-medium">{kb.key_label} <span className="text-xs text-gray-600">({kb.network})</span></div>
              {kb.error ? (
                <div className="text-xs text-sell-DEFAULT">{kb.error}</div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-2">
                  {(kb.balances || []).map((b: any) => (
                    <div key={b.asset || b.balance} className="bg-[#131720] rounded-lg p-3 border border-[#2b2f36]">
                      <div className="text-xs text-gray-500 font-semibold">{b.asset}</div>
                      <div className="text-sm font-mono text-white mt-1">{parseFloat(b.free || b.balance || "0").toFixed(4)}</div>
                      {b.locked && parseFloat(b.locked) > 0 && <div className="text-xs text-gray-600 mt-0.5">locked: {parseFloat(b.locked).toFixed(4)}</div>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Performance table */}
      {performance && (
        <div className="card-dark p-5">
          <h2 className="font-semibold text-white mb-4">Performance Metrics</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {[
              { label: "Total Return", value: `${performance.total_return >= 0 ? "+" : ""}$${performance.total_return?.toFixed(4)}`, color: performance.total_return >= 0 ? "text-buy-DEFAULT" : "text-sell-DEFAULT" },
              { label: "Win Rate", value: `${performance.win_rate}%`, color: performance.win_rate >= 50 ? "text-buy-DEFAULT" : "text-sell-DEFAULT" },
              { label: "Avg Win", value: `+$${performance.avg_win?.toFixed(4)}`, color: "text-buy-DEFAULT" },
              { label: "Avg Loss", value: `$${performance.avg_loss?.toFixed(4)}`, color: "text-sell-DEFAULT" },
              { label: "Profit Factor", value: performance.profit_factor?.toFixed(2), color: "text-gold-DEFAULT" },
              { label: "Max Drawdown", value: `-${performance.max_drawdown}%`, color: "text-sell-DEFAULT" },
              { label: "Best Trade", value: `+$${performance.best_trade?.toFixed(4)}`, color: "text-buy-DEFAULT" },
              { label: "Worst Trade", value: `$${performance.worst_trade?.toFixed(4)}`, color: "text-sell-DEFAULT" },
              { label: "Sharpe Ratio", value: performance.sharpe_ratio?.toFixed(4), color: "text-gold-DEFAULT" },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-[#131720] rounded-xl p-4 border border-[#2b2f36]">
                <div className="text-xs text-gray-500 mb-1">{label}</div>
                <div className={`text-lg font-bold font-mono ${color}`}>{value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
