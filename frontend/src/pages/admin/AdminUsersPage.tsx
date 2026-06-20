import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/services/api";
import toast from "react-hot-toast";
import { Users, Search, ToggleLeft, ToggleRight, Shield } from "lucide-react";
import { format } from "date-fns";

export default function AdminUsersPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [roleFilter, setRoleFilter] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["admin-users", search, page, roleFilter],
    queryFn: () => adminApi.getUsers({ search: search || undefined, page, per_page: 20, role: roleFilter || undefined }).then(r => r.data),
    refetchInterval: 30000,
  });

  const toggleStatus = useMutation({
    mutationFn: (id: string) => adminApi.toggleUserStatus(id),
    onSuccess: () => { toast.success("User status updated."); qc.invalidateQueries({ queryKey: ["admin-users"] }); },
    onError: () => toast.error("Failed."),
  });

  const changeRole = useMutation({
    mutationFn: ({ id, role }: { id: string; role: string }) => adminApi.changeUserRole(id, role),
    onSuccess: () => { toast.success("Role updated."); qc.invalidateQueries({ queryKey: ["admin-users"] }); },
    onError: () => toast.error("Failed."),
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Users className="text-red-400" size={22} /> Users Management
        </h1>
        <p className="text-gray-500 text-sm mt-0.5">{data?.total || 0} total users</p>
      </div>

      <div className="card-dark p-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-40">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} placeholder="Search username, email..." className="input-dark pl-9" />
        </div>
        <select value={roleFilter} onChange={e => { setRoleFilter(e.target.value); setPage(1); }} className="input-dark w-36">
          <option value="">All Roles</option>
          <option value="user">User</option>
          <option value="admin">Admin</option>
          <option value="moderator">Moderator</option>
        </select>
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
                  <th className="text-left p-4 font-medium">Role</th>
                  <th className="text-left p-4 font-medium">Plan</th>
                  <th className="text-center p-4 font-medium">Auto Trade</th>
                  <th className="text-left p-4 font-medium">Joined</th>
                  <th className="text-center p-4 font-medium">Status</th>
                  <th className="text-center p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.users?.map((u: any) => (
                  <tr key={u.id} className="table-row-hover border-b border-[#2b2f36]/50">
                    <td className="p-4">
                      <div className="font-medium text-white">{u.username}</div>
                      <div className="text-xs text-gray-500">{u.email}</div>
                    </td>
                    <td className="p-4">
                      <select
                        value={u.role}
                        onChange={e => changeRole.mutate({ id: u.id, role: e.target.value })}
                        className="text-xs bg-[#2b2f36] border border-[#3d4249] rounded px-2 py-1 text-white"
                      >
                        <option value="user">user</option>
                        <option value="moderator">moderator</option>
                        <option value="admin">admin</option>
                      </select>
                    </td>
                    <td className="p-4 capitalize">
                      <span className="text-xs px-2 py-0.5 bg-[#2b2f36] rounded text-gray-300">{u.subscription_plan}</span>
                    </td>
                    <td className="p-4 text-center">
                      {u.auto_trading_enabled ? <span className="text-buy-DEFAULT text-xs font-medium">ON</span> : <span className="text-gray-600 text-xs">OFF</span>}
                    </td>
                    <td className="p-4 text-xs text-gray-400">
                      {format(new Date(u.created_at), "MMM dd, yyyy")}
                    </td>
                    <td className="p-4 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded ${u.is_active ? "text-buy-DEFAULT bg-buy-DEFAULT/10" : "text-sell-DEFAULT bg-sell-DEFAULT/10"}`}>
                        {u.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      <button onClick={() => toggleStatus.mutate(u.id)} disabled={toggleStatus.isPending} className="text-xs px-2 py-1 bg-[#2b2f36] hover:bg-[#3d4249] rounded transition-colors text-gray-300">
                        {u.is_active ? "Disable" : "Enable"}
                      </button>
                    </td>
                  </tr>
                ))}
                {!data?.users?.length && (
                  <tr><td colSpan={7} className="text-center py-10 text-gray-500">No users found</td></tr>
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
