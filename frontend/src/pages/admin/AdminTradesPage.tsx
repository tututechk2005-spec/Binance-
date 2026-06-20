import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/services/api";
import { TrendingUp, Filter } from "lucide-react";
import { format } from "date-fns";

export default function AdminTradesPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["admin-trades", page, statusFilter],
    queryFn: () => adminApi.getTrades({ page, per_page: 25, status: statusFilter || undefined }).then(r => r.data),
    refetchInterval: 15000,
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <TrendingUp className="text-red-400" size={22} /> Trades
        </h1>
        <p className="text-gray-500 text-sm mt-0.5">{data?.total || 0} total trades</p>
      </div>

      <div className="card-dark p-4 flex items-center gap-3">
        <Filter size={14} className="text-gray-500" />
        <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }} className="input-dark w-36">
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
          <option value="pending">Pending</option>
          <option value="cancelled">Cancelled</option>
          <option value="failed">Failed</option>
        </select>
        <div className="ml-auto text-xs text-gray-500">{data?.total || 0} trades</div>
      </div>

      <div className="card-dark overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-[#2b2f36]">
                <tr className="text-gray-500">
                  <th className="text-left p-4 font-medium">User</th>
                  <th className="text-left p-4 font-medium">Symbol</th>
                  <th className="text-left p-4 font-medium">Type</th>
                  <th className="text-right p-4 font-medium">Entry</th>
                  <th className="text-right p-4 font-medium">Qty</th>
                  <th className="text-right p-4 font-medium">PNL</th>
                  <th className="text-center p-4 font-medium">Status</th>
                  <th className="text-center p-4 font-medium">Auto</th>
                  <th className="text-left p-4 font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {data?.trades?.map((t: any) => (
                  <tr key={t.id} className="table-row-hover border-b border-[#2b2f36]/50">
                    <td className="p-4 text-xs text-gray-400">{t.username}</td>
                    <td className="p-4 font-semibold text-white">{t.symbol}</td>
                    <td className="p-4"><span className={t.trade_type === "BUY" ? "badge-buy" : "badge-sell"}>{t.trade_type}</span></td>
                    <td className="p-4 text-right font-mono text-xs text-gray-300">${t.entry_price?.toFixed(4) || "-"}</td>
                    <td className="p-4 text-right font-mono text-xs text-gray-300">{t.quantity}</td>
                    <td className={`p-4 text-right font-mono text-sm font-semibold ${t.pnl >= 0 ? "text-buy-DEFAULT" : "text-sell-DEFAULT"}`}>
                      {t.pnl >= 0 ? "+" : ""}{t.pnl?.toFixed(4)}
                    </td>
                    <td className="p-4 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded capitalize ${t.status === "open" ? "text-blue-400 bg-blue-400/10" : "text-gray-400 bg-gray-400/10"}`}>{t.status}</span>
                    </td>
                    <td className="p-4 text-center">
                      {t.is_auto_trade ? <span className="text-gold-DEFAULT text-xs">Auto</span> : <span className="text-gray-600 text-xs">Manual</span>}
                    </td>
                    <td className="p-4 text-xs text-gray-500">{t.created_at ? format(new Date(t.created_at), "MMM dd HH:mm") : ""}</td>
                  </tr>
                ))}
                {!data?.trades?.length && (
                  <tr><td colSpan={9} className="text-center py-10 text-gray-500">No trades found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {data?.pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="btn-secondary disabled:opacity-40 px-3 py-1 text-sm">← Prev</button>
          <span className="text-sm text-gray-400">Page {page} of {data.pages}</span>
          <button disabled={page === data.pages} onClick={() => setPage(p => p + 1)} className="btn-secondary disabled:opacity-40 px-3 py-1 text-sm">Next →</button>
        </div>
      )}
    </div>
  );
}
