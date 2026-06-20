import { Outlet } from "react-router-dom";
import { BarChart3 } from "lucide-react";

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-gradient-dark flex">
      {/* Left side — branding */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 bg-[#131720] border-r border-[#2b2f36] p-12">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gold-DEFAULT rounded-xl flex items-center justify-center">
            <BarChart3 size={20} className="text-black" />
          </div>
          <div>
            <div className="text-lg font-bold text-white">Binance AI Trader</div>
            <div className="text-xs text-gold-DEFAULT font-semibold tracking-widest uppercase">Pro Edition</div>
          </div>
        </div>

        <div className="space-y-6">
          <h1 className="text-4xl font-bold text-white leading-tight">
            Trade Smarter with
            <span className="text-gold-DEFAULT"> AI-Powered </span>
            Signals
          </h1>
          <p className="text-gray-400 text-lg leading-relaxed">
            Advanced Smart Money Concepts, liquidity detection, and automated trading
            powered by our proprietary AI engine.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "AI Accuracy", value: "87.4%" },
              { label: "Active Traders", value: "12,400+" },
              { label: "Signals/Day", value: "200+" },
              { label: "Avg. Monthly ROI", value: "+23.7%" },
            ].map(({ label, value }) => (
              <div key={label} className="bg-[#1e2026] rounded-xl p-4 border border-[#2b2f36]">
                <div className="text-2xl font-bold text-gold-DEFAULT">{value}</div>
                <div className="text-sm text-gray-400 mt-1">{label}</div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-sm text-gray-600">
          Trading involves risk. Only invest what you can afford to lose.
        </p>
      </div>

      {/* Right side — form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-gold-DEFAULT rounded-lg flex items-center justify-center">
              <BarChart3 size={16} className="text-black" />
            </div>
            <span className="font-bold text-white">Binance AI Trader Pro</span>
          </div>
          <Outlet />
        </div>
      </div>
    </div>
  );
}
