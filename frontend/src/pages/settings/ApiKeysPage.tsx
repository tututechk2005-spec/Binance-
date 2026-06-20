import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "@/services/api";
import toast from "react-hot-toast";
import { Key, Plus, Trash2, CheckCircle, XCircle, Shield, RefreshCw } from "lucide-react";

const NETWORKS = [
  { value: "spot_mainnet", label: "Spot — Mainnet" },
  { value: "futures_mainnet", label: "Futures — Mainnet" },
  { value: "spot_testnet", label: "Spot — Testnet" },
  { value: "futures_testnet", label: "Futures — Testnet" },
];

export default function ApiKeysPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ label: "", api_key: "", api_secret: "", network_type: "spot_testnet" });

  const { data: keys, isLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: () => usersApi.getApiKeys().then(r => r.data),
  });

  const addKey = useMutation({
    mutationFn: () => usersApi.createApiKey(form),
    onSuccess: () => {
      toast.success("API key added.");
      qc.invalidateQueries({ queryKey: ["api-keys"] });
      setForm({ label: "", api_key: "", api_secret: "", network_type: "spot_testnet" });
      setShowForm(false);
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || "Failed to add key."),
  });

  const deleteKey = useMutation({
    mutationFn: (id: string) => usersApi.deleteApiKey(id),
    onSuccess: () => { toast.success("Key deleted."); qc.invalidateQueries({ queryKey: ["api-keys"] }); },
    onError: () => toast.error("Delete failed."),
  });

  const verifyKey = useMutation({
    mutationFn: (id: string) => usersApi.verifyApiKey(id),
    onSuccess: () => { toast.success("Key verified!"); qc.invalidateQueries({ queryKey: ["api-keys"] }); },
    onError: () => toast.error("Verification failed. Check your key permissions."),
  });

  return (
    <div className="space-y-6 animate-fade-in max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Key className="text-gold-DEFAULT" size={22} /> API Keys
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">Manage your Binance API keys for trading</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus size={15} /> Add Key
        </button>
      </div>

      {/* Info */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 text-sm text-blue-300 space-y-1">
        <div className="font-semibold text-blue-200 flex items-center gap-2"><Shield size={14} /> Security Notice</div>
        <div>Your API keys are encrypted at rest using AES-256. We strongly recommend creating Spot-only keys with read + trade permissions, and no withdrawal access.</div>
      </div>

      {/* Add Form */}
      {showForm && (
        <div className="card-dark p-5">
          <h2 className="font-semibold text-white mb-4">Add New API Key</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1.5">Label</label>
              <input value={form.label} onChange={e => setForm(p => ({ ...p, label: e.target.value }))} className="input-dark" placeholder="My Binance Key" />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1.5">Network Type</label>
              <select value={form.network_type} onChange={e => setForm(p => ({ ...p, network_type: e.target.value }))} className="input-dark">
                {NETWORKS.map(n => <option key={n.value} value={n.value}>{n.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1.5">API Key</label>
              <input value={form.api_key} onChange={e => setForm(p => ({ ...p, api_key: e.target.value }))} className="input-dark font-mono" placeholder="Binance API Key" />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1.5">API Secret</label>
              <input type="password" value={form.api_secret} onChange={e => setForm(p => ({ ...p, api_secret: e.target.value }))} className="input-dark font-mono" placeholder="Binance API Secret" />
            </div>
            <div className="flex gap-2">
              <button onClick={() => addKey.mutate()} disabled={addKey.isPending || !form.api_key || !form.api_secret || !form.label} className="btn-primary flex items-center gap-2 disabled:opacity-50">
                {addKey.isPending ? <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : <Plus size={14} />}
                Add Key
              </button>
              <button onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Keys list */}
      {isLoading ? (
        <div className="card-dark p-8 text-center text-gray-500">Loading...</div>
      ) : keys?.length === 0 ? (
        <div className="card-dark p-12 text-center">
          <Key size={48} className="text-gray-600 mx-auto mb-3" />
          <div className="text-gray-400 font-medium">No API keys added yet</div>
          <div className="text-gray-600 text-sm mt-1">Add your Binance API keys to start trading</div>
        </div>
      ) : (
        <div className="space-y-3">
          {keys?.map((key: any) => (
            <div key={key.id} className="card-dark p-5">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{key.label}</span>
                    {key.is_verified ? (
                      <CheckCircle size={14} className="text-buy-DEFAULT" />
                    ) : (
                      <XCircle size={14} className="text-gray-600" />
                    )}
                  </div>
                  <div className="text-sm text-gray-500 mt-1 capitalize">{key.network_type.replace("_", " ")}</div>
                  {key.permissions && <div className="text-xs text-gray-600 mt-1">Permissions: {key.permissions}</div>}
                  {key.last_used && <div className="text-xs text-gray-600 mt-0.5">Last used: {new Date(key.last_used).toLocaleString()}</div>}
                </div>
                <div className="flex items-center gap-2">
                  {!key.is_verified && (
                    <button onClick={() => verifyKey.mutate(key.id)} disabled={verifyKey.isPending} className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-gold-DEFAULT border border-gold-DEFAULT/30 hover:bg-gold-DEFAULT/10 rounded-lg transition-colors">
                      <RefreshCw size={12} /> Verify
                    </button>
                  )}
                  <button onClick={() => { if (confirm("Delete this API key?")) deleteKey.mutate(key.id); }} className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-sell-DEFAULT border border-sell-DEFAULT/30 hover:bg-sell-DEFAULT/10 rounded-lg transition-colors">
                    <Trash2 size={12} /> Delete
                  </button>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-[#2b2f36] flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${key.is_active ? "bg-buy-DEFAULT" : "bg-gray-600"}`} />
                <span className="text-xs text-gray-500">{key.is_active ? "Active" : "Inactive"}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
