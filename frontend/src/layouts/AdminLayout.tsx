import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/services/api";
import toast from "react-hot-toast";
import {
  LayoutDashboard, Users, TrendingUp, Zap, CreditCard,
  FileText, LogOut, Menu, X, BarChart3, ArrowLeft
} from "lucide-react";

const adminNav = [
  { to: "/admin", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/admin/users", icon: Users, label: "Users" },
  { to: "/admin/trades", icon: TrendingUp, label: "Trades" },
  { to: "/admin/signals", icon: Zap, label: "Signals" },
  { to: "/admin/payments", icon: CreditCard, label: "Payments" },
  { to: "/admin/logs", icon: FileText, label: "System Logs" },
];

export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try { await authApi.logout(); } catch {}
    logout();
    navigate("/login");
    toast.success("Logged out.");
  };

  return (
    <div className="flex h-screen bg-[#0b0e11] overflow-hidden">
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#131720] border-r border-[#2b2f36] transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#2b2f36]">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center">
                <BarChart3 size={16} className="text-white" />
              </div>
              <div>
                <div className="text-sm font-bold text-white">Admin Panel</div>
                <div className="text-[10px] text-red-400 font-semibold">SUPER ACCESS</div>
              </div>
            </div>
            <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-gray-400 hover:text-white">
              <X size={18} />
            </button>
          </div>

          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            <NavLink to="/dashboard" className="sidebar-link text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 mb-3">
              <ArrowLeft size={17} /> <span>Back to App</span>
            </NavLink>
            {adminNav.map(({ to, icon: Icon, label }) => (
              <NavLink key={to} to={to} end={to === "/admin"} className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`} onClick={() => setSidebarOpen(false)}>
                <Icon size={17} /> <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="px-3 py-4 border-t border-[#2b2f36]">
            <div className="px-2 py-1 mb-2">
              <div className="text-sm font-medium text-white">{user?.username}</div>
              <div className="text-xs text-red-400 capitalize">{user?.role}</div>
            </div>
            <button onClick={handleLogout} className="sidebar-link w-full text-red-400 hover:text-red-300 hover:bg-red-500/10">
              <LogOut size={17} /> <span>Log Out</span>
            </button>
          </div>
        </div>
      </aside>

      {sidebarOpen && <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />}

      <div className="flex-1 flex flex-col lg:ml-64 min-w-0">
        <header className="flex items-center justify-between px-4 py-3 bg-[#131720] border-b border-[#2b2f36] sticky top-0 z-30">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-gray-400 hover:text-white">
            <Menu size={20} />
          </button>
          <div className="text-sm font-semibold text-red-400 hidden lg:block">ADMIN MODE</div>
          <div className="text-xs text-gray-500">{user?.email}</div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
