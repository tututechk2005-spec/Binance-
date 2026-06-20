import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/services/api";
import { Zap, Filter } from "lucide-react";
import { format } from "date-fns";

export default function AdminSignalsPage() {
  const [page, setPage] = useState(1);
  const [typeFilter, setTypeFilter] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["admin-signals", page, typeFilter],
    queryFn: () => adminApi.getSignals({ page, per_page: 25, signal_type: typeFilter || undefined }).then(r => r.data),
    refetchInterval: 30000,
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Zap className="text-red-400" size={22} /> Signals
        </h1>
        <p className="text-gray-500 text-sm mt-0.5">{data?.total || 0} total signals</p>
      </div>

      <div className="card-dark p-4 flex items-center gap-3">
        <Filter size={14} className="text-gray-500" />
        <select value={typeFilter} onChange={e => { setTypeFilter(e.target.value); setPage(1); }} className="input-dark w-32">
          <option value="">All Types</option>
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
        <div className="ml-auto text-xs text-gray-500">{data?.total || 0} signals</div>
      </div>

      <div className="card-dark overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-[#2b2f36]">
                <tr className="text-gray-500">
                  <th className="text-left p-4 font-medium">Symbol</th>
                  <th className="text-left p-4 font-medium">Type</th>
                  <th className="text-left p-4 font-medium">TF</th>
                  <th className="text-right p-4 font-medium">Confidence</th>
                  <th className="text-right p-4 font-medium">Entry</th>
                  <th className="text-right p-4 font-medium">SL</th>
                  <th className="text-right p-4 font-medium">TP1</th>
                  <th className="text-center p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {data?.signals?.map((s: any) => (
                  <tr key={s.id} className="table-row-hover border-b border-[#2b2f36]/50">
                    <td className="p-4 font-semibold text-white">{s.symbol}</td>
                    <td className="p-4"><span className={s.signal_type === "BUY" ? "badge-buy" : "badge-sell"}>{s.signal_type}</span></td>
                    <td className="p-4 text-xs text-gray-400">{s.timeframe}</td>
                    <td className="p-4 text-right font-mono text-sm font-semibold text-gold-DEFAULT">{s.confidence_score}%</td>
                    <td className="p-4 text-right font-mono text-xs text-gray-300">${s.entry_price?.toFixed(4)}</td>
                    <td className="p-4 text-right font-mono text-xs text-sell-DEFAULT">${s.stop_loss?.toFixed(4)}</td>
                    <td className="p-4 text-right font-mono text-xs text-buy-DEFAULT">${s.take_profit_1?.toFixed(4)}</td>
                    <td className="p-4 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded capitalize ${s.status === "active" ? "text-buy-DEFAULT bg-buy-DEFAULT/10" : "text-gray-400 bg-gray-400/10"}`}>{s.status}</span>
                    </td>
                    <td className="p-4 text-xs text-gray-500">{s.created_at ? format(new Date(s.created_at), "MMM dd HH:mm") : ""}</td>
                  </tr>
                ))}
                {!data?.signals?.length && (
                  <tr><td colSpan={9} className="text-center py-10 text-gray-500">No signals found</td></tr>
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
