import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "@/services/api";
import { FileText, AlertTriangle, Info, AlertCircle, RefreshCw } from "lucide-react";
import { format } from "date-fns";

export default function AdminLogsPage() {
  const [tab, setTab] = useState<"audit" | "system">("audit");
  const [page, setPage] = useState(1);
  const [levelFilter, setLevelFilter] = useState("");

  const { data: auditData, isLoading: auditLoading, refetch: refetchAudit } = useQuery({
    queryKey: ["audit-logs", page],
    queryFn: () => adminApi.getAuditLogs({ page, per_page: 30 }).then(r => r.data),
    enabled: tab === "audit",
    refetchInterval: 30000,
  });

  const { data: sysData, isLoading: sysLoading, refetch: refetchSys } = useQuery({
    queryKey: ["system-logs", page, levelFilter],
    queryFn: () => adminApi.getSystemLogs({ page, per_page: 50, level: levelFilter || undefined }).then(r => r.data),
    enabled: tab === "system",
    refetchInterval: 15000,
  });

  const levelIcon: Record<string, React.ReactNode> = {
    ERROR: <AlertCircle size={12} className="text-sell-DEFAULT" />,
    WARNING: <AlertTriangle size={12} className="text-gold-DEFAULT" />,
    INFO: <Info size={12} className="text-blue-400" />,
  };
  const levelColor: Record<string, string> = {
    ERROR: "text-sell-DEFAULT bg-sell-DEFAULT/10",
    WARNING: "text-gold-DEFAULT bg-gold-DEFAULT/10",
    INFO: "text-blue-400 bg-blue-400/10",
    DEBUG: "text-gray-400 bg-gray-400/10",
  };

  const refetch = tab === "audit" ? refetchAudit : refetchSys;
  const isLoading = tab === "audit" ? auditLoading : sysLoading;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText className="text-red-400" size={22} /> System Logs
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">Audit and system log monitoring</p>
        </div>
        <button onClick={() => refetch()} className="btn-secondary flex items-center gap-2 text-sm">
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex bg-[#131720] rounded-lg p-1 border border-[#2b2f36]">
          {(["audit", "system"] as const).map(t => (
            <button key={t} onClick={() => { setTab(t); setPage(1); }} className={`px-4 py-1.5 text-sm font-medium rounded-md capitalize transition-colors ${tab === t ? "bg-[#2b2f36] text-white" : "text-gray-500 hover:text-gray-300"}`}>
              {t === "audit" ? "Audit Logs" : "System Logs"}
            </button>
          ))}
        </div>
        {tab === "system" && (
          <select value={levelFilter} onChange={e => { setLevelFilter(e.target.value); setPage(1); }} className="input-dark w-32">
            <option value="">All Levels</option>
            <option value="ERROR">ERROR</option>
            <option value="WARNING">WARNING</option>
            <option value="INFO">INFO</option>
            <option value="DEBUG">DEBUG</option>
          </select>
        )}
      </div>

      <div className="card-dark overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading logs...</div>
        ) : tab === "audit" ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-[#2b2f36]">
                <tr className="text-gray-500">
                  <th className="text-left p-4 font-medium">Time</th>
                  <th className="text-left p-4 font-medium">User</th>
                  <th className="text-left p-4 font-medium">Action</th>
                  <th className="text-left p-4 font-medium">Resource</th>
                  <th className="text-left p-4 font-medium">IP</th>
                  <th className="text-center p-4 font-medium">Result</th>
                </tr>
              </thead>
              <tbody>
                {auditData?.logs?.map((log: any) => (
                  <tr key={log.id} className="table-row-hover border-b border-[#2b2f36]/50 text-xs">
                    <td className="p-4 text-gray-500">{format(new Date(log.created_at), "MMM dd HH:mm:ss")}</td>
                    <td className="p-4 text-gray-300">{log.username || "system"}</td>
                    <td className="p-4 font-medium text-white">{log.action}</td>
                    <td className="p-4 text-gray-400">{log.resource_type}{log.resource_id ? `#${log.resource_id}` : ""}</td>
                    <td className="p-4 font-mono text-gray-500">{log.ip_address}</td>
                    <td className="p-4 text-center">
                      <span className={`px-2 py-0.5 rounded font-medium ${log.success ? "text-buy-DEFAULT bg-buy-DEFAULT/10" : "text-sell-DEFAULT bg-sell-DEFAULT/10"}`}>
                        {log.success ? "OK" : "FAIL"}
                      </span>
                    </td>
                  </tr>
                ))}
                {!auditData?.logs?.length && (
                  <tr><td colSpan={6} className="text-center py-10 text-gray-500">No audit logs</td></tr>
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="divide-y divide-[#2b2f36]">
            {sysData?.logs?.map((log: any, i: number) => (
              <div key={i} className="flex items-start gap-3 p-3 hover:bg-[#2b2f36]/30 transition-colors">
                <div className="mt-0.5">{levelIcon[log.level] || <Info size={12} className="text-gray-600" />}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className={`text-xs px-1.5 py-0.5 rounded font-mono font-bold ${levelColor[log.level] || "text-gray-400 bg-gray-400/10"}`}>{log.level}</span>
                    <span className="text-xs text-gray-500">{log.logger}</span>
                    <span className="text-xs text-gray-600 ml-auto">{log.timestamp ? format(new Date(log.timestamp), "HH:mm:ss") : ""}</span>
                  </div>
                  <div className="text-xs text-gray-300 font-mono break-all">{log.message}</div>
                </div>
              </div>
            ))}
            {!sysData?.logs?.length && (
              <div className="text-center py-10 text-gray-500">No system logs found</div>
            )}
          </div>
        )}
      </div>

      {((tab === "audit" ? auditData?.pages : sysData?.pages) || 0) > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="btn-secondary disabled:opacity-40 px-3 py-1 text-sm">← Prev</button>
          <span className="text-sm text-gray-400">Page {page}</span>
          <button disabled={page === (tab === "audit" ? auditData?.pages : sysData?.pages)} onClick={() => setPage(p => p + 1)} className="btn-secondary disabled:opacity-40 px-3 py-1 text-sm">Next →</button>
        </div>
      )}
    </div>
  );
}
