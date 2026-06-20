import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi, authApi } from "@/services/api";
import { useAuthStore } from "@/store/authStore";
import toast from "react-hot-toast";
import { Settings, Save, Shield, ToggleLeft, ToggleRight } from "lucide-react";

export default function SettingsPage() {
  const { user, setUser } = useAuthStore();
  const qc = useQueryClient();

  const [profile, setProfile] = useState({ full_name: user?.full_name || "", phone: "", country: "", timezone: "UTC" });
  const [password, setPassword] = useState({ current_password: "", new_password: "", confirm: "" });
  const [trading, setTrading] = useState({ risk_percent: user?.risk_percent || 1, max_trades_per_day: user?.max_trades_per_day || 10 });
  const [autoTrading, setAutoTrading] = useState(user?.auto_trading_enabled || false);

  const updateProfile = useMutation({
    mutationFn: () => usersApi.updateProfile(profile),
    onSuccess: () => toast.success("Profile updated."),
    onError: () => toast.error("Update failed."),
  });

  const updateSettings = useMutation({
    mutationFn: () => usersApi.updateTradingSettings({ ...trading, auto_trading_enabled: autoTrading }),
    onSuccess: () => {
      toast.success("Trading settings updated.");
      if (user) setUser({ ...user, auto_trading_enabled: autoTrading, risk_percent: trading.risk_percent, max_trades_per_day: trading.max_trades_per_day });
    },
    onError: () => toast.error("Update failed."),
  });

  const changePassword = useMutation({
    mutationFn: () => authApi.changePassword({ current_password: password.current_password, new_password: password.new_password }),
    onSuccess: () => { toast.success("Password changed."); setPassword({ current_password: "", new_password: "", confirm: "" }); },
    onError: (e: any) => toast.error(e?.response?.data?.detail || "Change failed."),
  });

  const toggleAuto = () => {
    const next = !autoTrading;
    setAutoTrading(next);
    usersApi.updateTradingSettings({ auto_trading_enabled: next })
      .then(() => {
        if (user) setUser({ ...user, auto_trading_enabled: next });
        toast.success(`Auto trading ${next ? "enabled" : "disabled"}.`);
      })
      .catch(() => { setAutoTrading(!next); toast.error("Update failed."); });
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Settings className="text-gold-DEFAULT" size={22} /> Settings
        </h1>
        <p className="text-gray-500 text-sm mt-0.5">Manage your account and trading preferences</p>
      </div>

      {/* Auto Trading Toggle */}
      <div className="card-dark p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-white flex items-center gap-2">Auto Trading</h2>
            <p className="text-sm text-gray-400 mt-1">Automatically execute trades based on AI signals</p>
          </div>
          <button onClick={toggleAuto} className="flex items-center gap-2 transition-colors">
            {autoTrading
              ? <ToggleRight size={40} className="text-buy-DEFAULT" />
              : <ToggleLeft size={40} className="text-gray-600" />
            }
          </button>
        </div>
        {autoTrading && (
          <div className="mt-3 p-3 bg-buy-DEFAULT/10 border border-buy-DEFAULT/20 rounded-lg text-sm text-buy-DEFAULT">
            Auto trading is active. Signals with sufficient confidence will trigger automatic orders.
          </div>
        )}
      </div>

      {/* Trading Settings */}
      <div className="card-dark p-5">
        <h2 className="font-semibold text-white mb-4">Trading Settings</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Risk Per Trade (%)</label>
            <input type="number" step={0.1} min={0.1} max={5} value={trading.risk_percent}
              onChange={e => setTrading(p => ({ ...p, risk_percent: parseFloat(e.target.value) }))}
              className="input-dark w-32" />
            <p className="text-xs text-gray-600 mt-1">Max 5%. Controls position size per trade.</p>
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Max Auto Trades Per Day</label>
            <input type="number" min={1} max={100} value={trading.max_trades_per_day}
              onChange={e => setTrading(p => ({ ...p, max_trades_per_day: parseInt(e.target.value) }))}
              className="input-dark w-32" />
          </div>
          <button onClick={() => updateSettings.mutate()} disabled={updateSettings.isPending} className="btn-primary flex items-center gap-2">
            <Save size={14} /> {updateSettings.isPending ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </div>

      {/* Profile */}
      <div className="card-dark p-5">
        <h2 className="font-semibold text-white mb-4">Profile Information</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Username</label>
            <input value={user?.username || ""} disabled className="input-dark opacity-50 cursor-not-allowed" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Email</label>
            <input value={user?.email || ""} disabled className="input-dark opacity-50 cursor-not-allowed" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Full Name</label>
            <input value={profile.full_name} onChange={e => setProfile(p => ({ ...p, full_name: e.target.value }))} className="input-dark" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Phone</label>
            <input value={profile.phone} onChange={e => setProfile(p => ({ ...p, phone: e.target.value }))} className="input-dark" placeholder="+1234567890" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Country</label>
            <input value={profile.country} onChange={e => setProfile(p => ({ ...p, country: e.target.value }))} className="input-dark" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Timezone</label>
            <input value={profile.timezone} onChange={e => setProfile(p => ({ ...p, timezone: e.target.value }))} className="input-dark" placeholder="UTC" />
          </div>
        </div>
        <button onClick={() => updateProfile.mutate()} disabled={updateProfile.isPending} className="btn-primary flex items-center gap-2 mt-4">
          <Save size={14} /> {updateProfile.isPending ? "Saving..." : "Save Profile"}
        </button>
      </div>

      {/* Change Password */}
      <div className="card-dark p-5">
        <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
          <Shield size={16} className="text-gold-DEFAULT" /> Change Password
        </h2>
        <div className="space-y-3">
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Current Password</label>
            <input type="password" value={password.current_password} onChange={e => setPassword(p => ({ ...p, current_password: e.target.value }))} className="input-dark" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">New Password</label>
            <input type="password" value={password.new_password} onChange={e => setPassword(p => ({ ...p, new_password: e.target.value }))} className="input-dark" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1.5">Confirm New Password</label>
            <input type="password" value={password.confirm} onChange={e => setPassword(p => ({ ...p, confirm: e.target.value }))} className="input-dark" />
          </div>
          <button onClick={() => {
            if (password.new_password !== password.confirm) { toast.error("Passwords do not match."); return; }
            changePassword.mutate();
          }} disabled={changePassword.isPending} className="btn-primary flex items-center gap-2">
            <Shield size={14} /> {changePassword.isPending ? "Changing..." : "Change Password"}
          </button>
        </div>
      </div>
    </div>
  );
}
