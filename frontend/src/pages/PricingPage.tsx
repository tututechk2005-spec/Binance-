import { useQuery, useMutation } from "@tanstack/react-query";
import { paymentsApi } from "@/services/api";
import { useAuthStore } from "@/store/authStore";
import toast from "react-hot-toast";
import { Check, Crown, Zap, Star, Rocket } from "lucide-react";

const PLAN_ICONS: Record<string, React.ReactNode> = {
  free: <Zap size={22} className="text-gray-400" />,
  basic: <Star size={22} className="text-blue-400" />,
  pro: <Crown size={22} className="text-gold-DEFAULT" />,
  enterprise: <Rocket size={22} className="text-purple-400" />,
};

const FEATURES: Record<string, string[]> = {
  free: ["5 signals/day", "1 API key", "Manual trading only", "Basic portfolio view", "Community support"],
  basic: ["50 signals/day", "3 API keys", "5 auto-trades/day", "Full portfolio analytics", "Email support"],
  pro: ["200 signals/day", "10 API keys", "25 auto-trades/day", "Advanced AI signals", "SMC & liquidity analysis", "Priority support", "Performance reports"],
  enterprise: ["Unlimited signals", "Unlimited API keys", "Unlimited auto-trades", "Custom AI strategies", "Dedicated account manager", "24/7 phone support", "Custom integrations"],
};

export default function PricingPage() {
  const { user } = useAuthStore();

  const { data: plans } = useQuery({
    queryKey: ["plans"],
    queryFn: () => paymentsApi.getPlans().then(r => r.data),
  });

  const stripeCheckout = useMutation({
    mutationFn: (data: { plan_id: string; interval: string }) => paymentsApi.createStripeSession(data),
    onSuccess: (res) => {
      if (res.data.checkout_url) window.open(res.data.checkout_url, "_blank");
      else toast.error("Could not create checkout session.");
    },
    onError: () => toast.error("Checkout failed. Try again."),
  });

  const orderedPlans = ["free", "basic", "pro", "enterprise"];

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white">Upgrade Your Trading</h1>
        <p className="text-gray-400 mt-2 text-lg">Choose the plan that fits your trading style</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {orderedPlans.map((slug) => {
          const plan = plans?.find((p: any) => p.slug === slug);
          const isCurrentPlan = user?.subscription_plan === slug;
          const isPro = slug === "pro";

          return (
            <div key={slug} className={`relative card-dark p-6 flex flex-col ${isPro ? "border-gold-DEFAULT/50 bg-gold-DEFAULT/5" : ""}`}>
              {isPro && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <div className="bg-gold-DEFAULT text-black text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">Most Popular</div>
                </div>
              )}

              <div className="flex items-center gap-3 mb-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${isPro ? "bg-gold-DEFAULT/20" : "bg-[#2b2f36]"}`}>
                  {PLAN_ICONS[slug]}
                </div>
                <div>
                  <div className="font-bold text-white capitalize">{slug}</div>
                  {isCurrentPlan && <div className="text-xs text-buy-DEFAULT font-medium">Current Plan</div>}
                </div>
              </div>

              <div className="mb-4">
                {plan ? (
                  <>
                    <div className="text-3xl font-bold text-white">
                      ${plan.price_monthly}
                      <span className="text-sm text-gray-500 font-normal">/mo</span>
                    </div>
                    {plan.price_yearly && (
                      <div className="text-xs text-buy-DEFAULT mt-1">Save ${Math.round((plan.price_monthly * 12 - plan.price_yearly) / 12)}/mo billed yearly</div>
                    )}
                  </>
                ) : slug === "free" ? (
                  <div className="text-3xl font-bold text-white">$0<span className="text-sm text-gray-500 font-normal">/mo</span></div>
                ) : (
                  <div className="text-3xl font-bold text-white animate-pulse bg-[#2b2f36] h-9 w-24 rounded" />
                )}
              </div>

              <div className="space-y-2.5 flex-1 mb-6">
                {(FEATURES[slug] || []).map((f) => (
                  <div key={f} className="flex items-center gap-2 text-sm">
                    <Check size={14} className={isPro ? "text-gold-DEFAULT" : "text-buy-DEFAULT"} />
                    <span className="text-gray-300">{f}</span>
                  </div>
                ))}
              </div>

              {!isCurrentPlan && slug !== "free" && (
                <div className="space-y-2">
                  <button
                    onClick={() => plan && stripeCheckout.mutate({ plan_id: plan.id, interval: "monthly" })}
                    disabled={stripeCheckout.isPending || !plan}
                    className={`w-full py-2.5 rounded-lg font-semibold text-sm transition-colors disabled:opacity-50 ${isPro ? "btn-primary" : "btn-secondary"}`}
                  >
                    {stripeCheckout.isPending ? "..." : "Pay with Stripe"}
                  </button>
                  {(slug === "basic" || slug === "pro") && (
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => plan && paymentsApi.initiateMtn({ plan_id: plan.id, phone: "" }).then(() => toast.success("MTN request sent.")).catch(() => toast.error("MTN failed."))}
                        className="btn-secondary text-xs py-2 text-yellow-400"
                      >
                        MTN MoMo
                      </button>
                      <button
                        onClick={() => plan && paymentsApi.initiateAirtel({ plan_id: plan.id, phone: "" }).then(() => toast.success("Airtel request sent.")).catch(() => toast.error("Airtel failed."))}
                        className="btn-secondary text-xs py-2 text-red-400"
                      >
                        Airtel Money
                      </button>
                    </div>
                  )}
                </div>
              )}

              {isCurrentPlan && (
                <div className="text-center py-2.5 text-sm text-buy-DEFAULT font-medium border border-buy-DEFAULT/30 rounded-lg">
                  Current Plan
                </div>
              )}

              {!isCurrentPlan && slug === "free" && (
                <div className="text-center py-2.5 text-sm text-gray-500">Free forever</div>
              )}
            </div>
          );
        })}
      </div>

      <div className="card-dark p-6 text-center max-w-2xl mx-auto">
        <h3 className="font-semibold text-white mb-2">Payment Methods Accepted</h3>
        <div className="flex flex-wrap justify-center gap-3 text-sm text-gray-400">
          <span className="px-3 py-1.5 bg-[#131720] rounded-lg border border-[#2b2f36]">💳 Stripe (Cards, SEPA)</span>
          <span className="px-3 py-1.5 bg-[#131720] rounded-lg border border-[#2b2f36]">📱 PayPal</span>
          <span className="px-3 py-1.5 bg-[#131720] rounded-lg border border-[#2b2f36]">🟡 MTN Mobile Money</span>
          <span className="px-3 py-1.5 bg-[#131720] rounded-lg border border-[#2b2f36]">🔴 Airtel Money</span>
        </div>
        <p className="text-xs text-gray-600 mt-4">All payments are secure and encrypted. Cancel anytime. Trading involves risk.</p>
      </div>
    </div>
  );
}
