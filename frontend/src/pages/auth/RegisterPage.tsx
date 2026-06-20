import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { authApi } from "@/services/api";
import { useAuthStore } from "@/store/authStore";
import toast from "react-hot-toast";
import { Eye, EyeOff, UserPlus } from "lucide-react";

const schema = z.object({
  username: z.string().min(3, "Min 3 characters").max(50),
  email: z.string().email("Invalid email"),
  full_name: z.string().optional(),
  password: z.string().min(8, "Min 8 characters"),
  confirm_password: z.string(),
}).refine((d) => d.password === d.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});
type Form = z.infer<typeof schema>;

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const { register, handleSubmit, formState: { errors } } = useForm<Form>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: Form) => {
    setLoading(true);
    try {
      const res = await authApi.register({ username: data.username, email: data.email, password: data.password, full_name: data.full_name });
      const d = res.data;
      setAuth(
        { id: d.user_id, username: d.username, email: d.email, role: d.role, subscription_plan: "free", auto_trading_enabled: false, risk_percent: 1, max_trades_per_day: 10, is_active: true, is_verified: false, created_at: new Date().toISOString() },
        d.access_token,
        d.refresh_token
      );
      toast.success("Account created! Welcome to BAT Pro.");
      navigate("/dashboard");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Create your account</h2>
        <p className="text-gray-400 mt-1">Start trading with AI-powered signals today</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Username</label>
            <input {...register("username")} placeholder="trader123" className="input-dark" />
            {errors.username && <p className="mt-1 text-xs text-sell-DEFAULT">{errors.username.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Full Name</label>
            <input {...register("full_name")} placeholder="John Doe" className="input-dark" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">Email</label>
          <input {...register("email")} type="email" placeholder="you@example.com" className="input-dark" />
          {errors.email && <p className="mt-1 text-xs text-sell-DEFAULT">{errors.email.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">Password</label>
          <div className="relative">
            <input {...register("password")} type={showPassword ? "text" : "password"} placeholder="Min 8 characters" className="input-dark pr-10" />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {errors.password && <p className="mt-1 text-xs text-sell-DEFAULT">{errors.password.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">Confirm Password</label>
          <input {...register("confirm_password")} type="password" placeholder="Repeat password" className="input-dark" />
          {errors.confirm_password && <p className="mt-1 text-xs text-sell-DEFAULT">{errors.confirm_password.message}</p>}
        </div>

        <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 py-3 disabled:opacity-50">
          {loading ? <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : <UserPlus size={16} />}
          {loading ? "Creating account..." : "Create Account"}
        </button>
      </form>

      <div className="text-center text-sm text-gray-500">
        Already have an account?{" "}
        <Link to="/login" className="text-gold-DEFAULT hover:text-gold-dark font-medium">Sign in</Link>
      </div>
    </div>
  );
}
