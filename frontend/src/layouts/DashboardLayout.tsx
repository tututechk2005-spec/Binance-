import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/services/api";
import toast from "react-hot-toast";
import {
  LayoutDashboard, TrendingUp, Briefcase, Zap, Settings,
  Key, LogOut, Menu, X, Bell, ChevronDown, Shield, User,
  DollarSign, BarChart3
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { notificationsApi } from "@/services/api";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/trading", icon: TrendingUp, label: "Trading" },
  { to: "/signals", icon: Zap, label: "AI Signals" },
  { to: "/portfolio", icon: Briefcase, label: "Portfolio" },
  { to: "/pricing", icon: DollarSign, label: "Pricing" },
  { to: "/settings", icon: Settings, label: "Settings" },
  { to: "/settings/api-keys", icon: Key, label: "API Keys" },
];

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const { data: unreadData } = useQuery({
    queryKey: ["notifications-unread"],
    queryFn: () => notificationsApi.getUnreadCount().then(r => r.data),
    refetchInterval: 30000,
  });

  const handleLogout = async () => {
    try { await authApi.logout(); } catch {}
    logout();
    navigate("/login");
    toast.success("Logged out successfully.");
  };

  return (
    <div className="flex h-screen bg-[#0b0e11] overflow-hidden">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#131720] border-r border-[#2b2f36] transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#2b2f36]">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gold-DEFAULT rounded-lg flex items-center justify-center">
                <BarChart3 size={16} className="text-black" />
              </div>
              <div>
                <div className="text-sm font-bold text-white">Binance AI</div>
                <div className="text-[10px] text-gold-DEFAULT font-semibold">TRADER PRO</div>
              </div>
            </div>
            <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-gray-400 hover:text-white">
              <X size={18} />
            </button>
          </div>

          {/* Nav */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink key={to} to={to} className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              } onClick={() => setSidebarOpen(false)}>
                <Icon size={17} />
                <span>{label}</span>
              </NavLink>
            ))}

            {(user?.role === "admin" || user?.role === "moderator") && (
              <>
                <div className="px-3 pt-4 pb-1">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Admin</span>
                </div>
                <NavLink to="/admin" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
                  <Shield size={17} />
                  <span>Admin Panel</span>
                </NavLink>
              </>
            )}
          </nav>

          {/* User */}
          <div className="px-3 py-4 border-t border-[#2b2f36]">
            <div className="flex items-center gap-3 px-2 py-2">
              <div className="w-8 h-8 bg-gold-DEFAULT/20 rounded-full flex items-center justify-center">
                <User size={14} className="text-gold-DEFAULT" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-white truncate">{user?.username}</div>
                <div className="text-xs text-gray-500 truncate capitalize">{user?.subscription_plan} plan</div>
              </div>
            </div>
            <button onClick={handleLogout} className="sidebar-link w-full mt-1 text-red-400 hover:text-red-300 hover:bg-red-500/10">
              <LogOut size={17} />
              <span>Log Out</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Backdrop */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col lg:ml-64 min-w-0">
        {/* Topbar */}
        <header className="flex items-center justify-between px-4 py-3 bg-[#131720] border-b border-[#2b2f36] sticky top-0 z-30">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-gray-400 hover:text-white p-1">
            <Menu size={20} />
          </button>

          <div className="flex items-center gap-2 lg:hidden">
            <div className="w-6 h-6 bg-gold-DEFAULT rounded flex items-center justify-center">
              <BarChart3 size={12} className="text-black" />
            </div>
            <span className="text-sm font-bold text-white">BAT Pro</span>
          </div>

          <div className="flex-1 hidden lg:block" />

          <div className="flex items-center gap-3">
            {user?.auto_trading_enabled && (
              <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-buy-DEFAULT/15 border border-buy-DEFAULT/30 rounded-full">
                <div className="w-1.5 h-1.5 rounded-full bg-buy-DEFAULT animate-pulse" />
                <span className="text-xs text-buy-DEFAULT font-medium">Auto Trading ON</span>
              </div>
            )}

            <button className="relative p-2 text-gray-400 hover:text-white rounded-lg hover:bg-[#2b2f36]">
              <Bell size={18} />
              {(unreadData?.count || 0) > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-sell-DEFAULT rounded-full text-[9px] font-bold text-white flex items-center justify-center">
                  {unreadData?.count}
                </span>
              )}
            </button>

            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-[#2b2f36] text-gray-300 hover:text-white transition-colors"
              >
                <div className="w-6 h-6 bg-gold-DEFAULT/20 rounded-full flex items-center justify-center">
                  <User size={12} className="text-gold-DEFAULT" />
                </div>
                <span className="text-sm font-medium hidden sm:block">{user?.username}</span>
                <ChevronDown size={14} />
              </button>
              {profileOpen && (
                <div className="absolute right-0 mt-1 w-48 bg-[#1e2026] border border-[#2b2f36] rounded-lg shadow-xl z-50 py-1">
                  <div className="px-3 py-2 border-b border-[#2b2f36]">
                    <div className="text-xs text-gray-400">Signed in as</div>
                    <div className="text-sm font-medium text-white truncate">{user?.email}</div>
                  </div>
                  <NavLink to="/settings" className="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-[#2b2f36]" onClick={() => setProfileOpen(false)}>
                    <Settings size={14} /> Settings
                  </NavLink>
                  <button onClick={() => { handleLogout(); setProfileOpen(false); }} className="flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 w-full">
                    <LogOut size={14} /> Log Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
