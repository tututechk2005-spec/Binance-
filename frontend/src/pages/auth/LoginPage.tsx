import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { authApi } from "@/services/api";
import { useAuthStore } from "@/store/authStore";
import toast from "react-hot-toast";
import { Eye, EyeOff, LogIn } from "lucide-react";

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(1, "Password required"),
});
type Form = z.infer<typeof schema>;

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const { register, handleSubmit, formState: { errors } } = useForm<Form>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: Form) => {
    setLoading(true);
    try {
      const res = await authApi.login(data.email, data.password);
      const d = res.data;
      setAuth(
        { id: d.user_id, username: d.username, email: d.email, role: d.role, subscription_plan: "free", auto_trading_enabled: false, risk_percent: 1, max_trades_per_day: 10, is_active: true, is_verified: true, created_at: new Date().toISOString() },
        d.access_token,
        d.refresh_token
      );
      toast.success(`Welcome back, ${d.username}!`);
      navigate("/dashboard");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Welcome back</h2>
        <p className="text-gray-400 mt-1">Sign in to your trading account</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">Email</label>
          <input {...register("email")} type="email" placeholder="you@example.com" className="input-dark" />
          {errors.email && <p className="mt-1 text-xs text-sell-DEFAULT">{errors.email.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
          <div className="relative">
            <input {...register("password")} type={showPassword ? "text" : "password"} placeholder="••••••••" className="input-dark pr-10" />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {errors.password && <p className="mt-1 text-xs text-sell-DEFAULT">{errors.password.message}</p>}
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 py-3 disabled:opacity-50 disabled:cursor-not-allowed">
          {loading ? <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : <LogIn size={16} />}
          {loading ? "Signing in..." : "Sign In"}
        </button>
      </form>

      <div className="text-center text-sm text-gray-500">
        Don't have an account?{" "}
        <Link to="/register" className="text-gold-DEFAULT hover:text-gold-dark font-medium">Create account</Link>
      </div>

      <div className="bg-[#1e2026] rounded-xl p-4 border border-[#2b2f36] text-sm text-gray-400 space-y-1">
        <div className="font-medium text-gray-300 mb-2">Demo credentials:</div>
        <div>Email: <span className="text-gold-DEFAULT font-mono">admin@batpro.app</span></div>
        <div>Password: <span className="text-gold-DEFAULT font-mono">Admin@123456</span></div>
      </div>
    </div>
  );
}
