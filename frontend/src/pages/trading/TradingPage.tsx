import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tradesApi } from "@/services/api";
import TradeRow from "@/components/trading/TradeRow";
import { Activity, RefreshCw, TrendingUp } from "lucide-react";
import toast from "react-hot-toast";
import { format } from "date-fns";

export default function TradingPage() {
  const [tab, setTab] = useState<"open" | "all">("open");
  const [page, setPage] = useState(1);
  const qc = useQueryClient();

  const { data: tradesData, isLoading, refetch } = useQuery({
    queryKey: ["trades", tab, page],
    queryFn: () => tradesApi.getTrades({
      status: tab === "open" ? "open" : undefined,
      page,
      per_page: 20,
    }).then(r => r.data),
    refetchInterval: 15000,
  });

  const { data: positions } = useQuery({
    queryKey: ["positions"],
    queryFn: () => tradesApi.getPositions().then(r => r.data),
    refetchInterval: 15000,
  });

  const { data: stats } = useQuery({
    queryKey: ["trade-stats"],
    queryFn: () => tradesApi.getStats().then(r => r.data),
  });

  const closeTrade = useMutation({
    mutationFn: (id: string) => tradesApi.closeTrade(id),
    onSuccess: () => {
      toast.success("Trade closed.");
      qc.invalidateQueries({ queryKey: ["trades"] });
      qc.invalidateQueries({ queryKey: ["portfolio-overview"] });
    },
    onError: () => toast.error("Failed to close trade."),
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="text-gold-DEFAULT" size={22} /> Trading
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">Manage your open and closed trades</p>
        </div>
        <button onClick={() => refetch()} className="btn-secondary flex items-center gap-2 text-sm">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Total Trades", value: stats.total_trades },
            { label: "Open", value: stats.open_trades, color: "text-blue-400" },
            { label: "Win Rate", value: `${stats.win_rate}%`, color: stats.win_rate >= 50 ? "text-buy-DEFAULT" : "text-sell-DEFAULT" },
            { label: "Total PNL", value: `${stats.total_pnl >= 0 ? "+" : ""}$${stats.total_pnl?.toFixed(4)}`, color: stats.total_pnl >= 0 ? "text-buy-DEFAULT" : "text-sell-DEFAULT" },
          ].map(({ label, value, color }) => (
            <div key={label} className="stat-card">
              <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">{label}</div>
              <div className={`text-2xl font-bold font-mono ${color || "text-white"}`}>{value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Open Positions (Futures) */}
      {positions && positions.length > 0 && (
        <div className="card-dark p-5">
          <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Activity size={16} className="text-gold-DEFAULT" /> Open Positions
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 border-b border-[#2b2f36]">
                  <th className="text-left pb-3 font-medium">Symbol</th>
                  <th className="text-left pb-3 font-medium">Side</th>
                  <th className="text-right pb-3 font-medium">Entry</th>
                  <th className="text-right pb-3 font-medium">Size</th>
                  <th className="text-right pb-3 font-medium">Leverage</th>
                  <th className="text-right pb-3 font-medium">Unrealized PNL</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p: any) => (
                  <tr key={p.id} className="table-row-hover border-b border-[#2b2f36]/50">
                    <td className="py-3 font-semibold text-white">{p.symbol}</td>
                    <td className="py-3"><span className={p.side === "BUY" ? "badge-buy" : "badge-sell"}>{p.side}</span></td>
                    <td className="py-3 text-right font-mono text-xs">${p.entry_price?.toFixed(4)}</td>
                    <td className="py-3 text-right font-mono text-xs">{p.quantity}</td>
                    <td className="py-3 text-right text-xs">{p.leverage}x</td>
                    <td className={`py-3 text-right font-mono font-semibold ${p.unrealized_pnl >= 0 ? "text-buy-DEFAULT" : "text-sell-DEFAULT"}`}>
                      {p.unrealized_pnl >= 0 ? "+" : ""}{p.unrealized_pnl?.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Trade History */}
      <div className="card-dark p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex bg-[#131720] rounded-lg p-1">
            {(["open", "all"] as const).map(t => (
              <button key={t} onClick={() => { setTab(t); setPage(1); }} className={`px-4 py-1.5 text-sm font-medium rounded-md capitalize transition-colors ${tab === t ? "bg-[#2b2f36] text-white" : "text-gray-500 hover:text-gray-300"}`}>
                {t === "open" ? "Open Trades" : "All Trades"}
              </button>
            ))}
          </div>
          <div className="ml-auto text-xs text-gray-500">{tradesData?.total || 0} total</div>
        </div>

        {isLoading ? (
          <div className="h-48 flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-gold-DEFAULT/30 border-t-gold-DEFAULT rounded-full animate-spin" />
          </div>
        ) : (
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
                  <th className="text-center pb-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {tradesData?.trades?.length > 0 ? (
                  tradesData.trades.map((t: any) => (
                    <tr key={t.id} className="table-row-hover border-b border-[#2b2f36]/50">
                      <td className="py-3 font-semibold text-white">{t.symbol}</td>
                      <td className="py-3"><span className={t.trade_type === "BUY" ? "badge-buy" : "badge-sell"}>{t.trade_type}</span></td>
                      <td className="py-3 text-right font-mono text-xs text-gray-300">${t.entry_price?.toFixed(4) || "-"}</td>
                      <td className="py-3 text-right font-mono text-xs text-gray-300">{t.quantity}</td>
                      <td className={`py-3 text-right font-mono text-sm font-semibold ${t.pnl >= 0 ? "text-buy-DEFAULT" : "text-sell-DEFAULT"}`}>
                        {t.pnl >= 0 ? "+" : ""}{t.pnl?.toFixed(4)}
                      </td>
                      <td className="py-3 text-center">
                        <span className={`text-xs px-2 py-0.5 rounded capitalize font-medium ${t.status === "open" ? "text-blue-400 bg-blue-400/10" : "text-gray-400 bg-gray-400/10"}`}>{t.status}</span>
                      </td>
                      <td className="py-3 text-center">
                        {t.status === "open" && (
                          <button onClick={() => closeTrade.mutate(t.id)} disabled={closeTrade.isPending} className="text-xs text-sell-DEFAULT hover:text-sell-dark bg-sell-DEFAULT/10 hover:bg-sell-DEFAULT/20 px-2 py-1 rounded transition-colors">
                            Close
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr><td colSpan={7} className="text-center py-10 text-gray-500">No trades found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {tradesData?.pages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-4">
            <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="btn-secondary disabled:opacity-40 px-3 py-1 text-sm">← Prev</button>
            <span className="text-sm text-gray-400">Page {page} of {tradesData.pages}</span>
            <button disabled={page === tradesData.pages} onClick={() => setPage(p => p + 1)} className="btn-secondary disabled:opacity-40 px-3 py-1 text-sm">Next →</button>
          </div>
        )}
      </div>
    </div>
  );
}
