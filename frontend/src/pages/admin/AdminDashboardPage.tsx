import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/services/api";
import { Users, TrendingUp, Zap, DollarSign, Activity, Shield } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function AdminDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: () => adminApi.getDashboard().then(r => r.data),
    refetchInterval: 30000,
  });

  const { data: revenue } = useQuery({
    queryKey: ["revenue-analytics"],
    queryFn: () => adminApi.getRevenueAnalytics().then(r => r.data),
  });

  const stats = data ? [
    { label: "Total Users", value: data.users?.total || 0, icon: Users, color: "text-blue-400" },
    { label: "Active Users", value: data.users?.active || 0, icon: Activity, color: "text-buy-DEFAULT" },
    { label: "Auto Trading Users", value: data.users?.auto_trading || 0, icon: TrendingUp, color: "text-gold-DEFAULT" },
    { label: "Total Trades", value: data.trades?.total || 0, icon: TrendingUp, color: "text-blue-400" },
    { label: "Open Trades", value: data.trades?.open || 0, icon: Activity, color: "text-gold-DEFAULT" },
    { label: "Active Signals", value: data.signals?.active || 0, icon: Zap, color: "text-purple-400" },
    { label: "Total Revenue", value: `$${(data.revenue?.total || 0).toFixed(2)}`, icon: DollarSign, color: "text-buy-DEFAULT" },
    { label: "Total Signals", value: data.signals?.total || 0, icon: Zap, color: "text-gold-DEFAULT" },
  ] : [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Shield className="text-red-400" size={22} /> Admin Dashboard
        </h1>
        <p className="text-gray-500 text-sm mt-0.5">Platform overview and key metrics</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array(8).fill(0).map((_, i) => (
            <div key={i} className="stat-card animate-pulse h-24" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="stat-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-500 uppercase tracking-wider">{label}</span>
                <Icon size={15} className={color} />
              </div>
              <div className={`text-2xl font-bold font-mono ${color}`}>{value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Revenue chart */}
      {revenue?.monthly_revenue && (
        <div className="card-dark p-5">
          <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
            <DollarSign size={16} className="text-gold-DEFAULT" /> Monthly Revenue
          </h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={revenue.monthly_revenue}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2b2f36" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#6b7280" }} />
              <YAxis tick={{ fontSize: 11, fill: "#6b7280" }} />
              <Tooltip contentStyle={{ background: "#1e2026", border: "1px solid #2b2f36", borderRadius: "8px", color: "#fff", fontSize: "12px" }} />
              <Bar dataKey="revenue" fill="#f0b90b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Plan distribution */}
      {revenue?.plan_distribution && (
        <div className="card-dark p-5">
          <h2 className="font-semibold text-white mb-4">Users by Plan</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {Object.entries(revenue.plan_distribution).map(([plan, count]) => (
              <div key={plan} className="bg-[#131720] rounded-xl p-4 text-center border border-[#2b2f36]">
                <div className="text-2xl font-bold text-white">{count as number}</div>
                <div className="text-sm text-gray-500 capitalize mt-1">{plan}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
