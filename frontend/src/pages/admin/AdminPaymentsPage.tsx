import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/services/api";
import { CreditCard, Filter } from "lucide-react";
import { format } from "date-fns";

export default function AdminPaymentsPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [providerFilter, setProviderFilter] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["admin-payments", page, statusFilter, providerFilter],
    queryFn: () => adminApi.getPayments({
      page, per_page: 25,
      status: statusFilter || undefined,
      provider: providerFilter || undefined,
    }).then(r => r.data),
    refetchInterval: 30000,
  });

  const statusColor: Record<string, string> = {
    completed: "text-buy-DEFAULT bg-buy-DEFAULT/10",
    pending: "text-gold-DEFAULT bg-gold-DEFAULT/10",
    failed: "text-sell-DEFAULT bg-sell-DEFAULT/10",
    refunded: "text-blue-400 bg-blue-400/10",
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <CreditCard className="text-red-400" size={22} /> Payments
        </h1>
        <p className="text-gray-500 text-sm mt-0.5">Revenue: ${data?.total_revenue?.toFixed(2) || "0.00"}</p>
      </div>

      <div className="card-dark p-4 flex flex-wrap gap-3 items-center">
        <Filter size={14} className="text-gray-500" />
        <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }} className="input-dark w-36">
          <option value="">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
          <option value="refunded">Refunded</option>
        </select>
        <select value={providerFilter} onChange={e => { setProviderFilter(e.target.value); setPage(1); }} className="input-dark w-36">
          <option value="">All Providers</option>
          <option value="stripe">Stripe</option>
          <option value="paypal">PayPal</option>
          <option value="mtn">MTN</option>
          <option value="airtel">Airtel</option>
        </select>
        <div className="ml-auto text-xs text-gray-500">{data?.total || 0} payments</div>
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
                  <th className="text-left p-4 font-medium">Provider</th>
                  <th className="text-right p-4 font-medium">Amount</th>
                  <th className="text-left p-4 font-medium">Plan</th>
                  <th className="text-left p-4 font-medium">Interval</th>
                  <th className="text-center p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {data?.payments?.map((p: any) => (
                  <tr key={p.id} className="table-row-hover border-b border-[#2b2f36]/50">
                    <td className="p-4">
                      <div className="text-sm font-medium text-white">{p.username}</div>
                      <div className="text-xs text-gray-500">{p.email}</div>
                    </td>
                    <td className="p-4">
                      <span className="text-xs capitalize bg-[#2b2f36] px-2 py-0.5 rounded text-gray-300">{p.provider}</span>
                    </td>
                    <td className="p-4 text-right font-mono font-semibold text-white">
                      ${p.amount?.toFixed(2)} <span className="text-xs text-gray-500">{p.currency}</span>
                    </td>
                    <td className="p-4 text-xs capitalize text-gray-300">{p.plan_name}</td>
                    <td className="p-4 text-xs capitalize text-gray-400">{p.billing_interval}</td>
                    <td className="p-4 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded capitalize font-medium ${statusColor[p.status] || "text-gray-400 bg-gray-400/10"}`}>{p.status}</span>
                    </td>
                    <td className="p-4 text-xs text-gray-500">{p.created_at ? format(new Date(p.created_at), "MMM dd, yyyy HH:mm") : ""}</td>
                  </tr>
                ))}
                {!data?.payments?.length && (
                  <tr><td colSpan={7} className="text-center py-10 text-gray-500">No payments found</td></tr>
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
