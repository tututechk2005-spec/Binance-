import { Trade } from "@/types";

interface Props { trade: Trade; }

export default function TradeRow({ trade }: Props) {
  const isBuy = trade.trade_type === "BUY";
  const pnlPos = trade.pnl >= 0;

  const statusColor: Record<string, string> = {
    open: "text-blue-400 bg-blue-400/10",
    closed: "text-gray-400 bg-gray-400/10",
    pending: "text-gold-DEFAULT bg-gold-DEFAULT/10",
    cancelled: "text-gray-600 bg-gray-600/10",
    failed: "text-sell-DEFAULT bg-sell-DEFAULT/10",
  };

  return (
    <tr className="table-row-hover border-b border-[#2b2f36]/50">
      <td className="py-3 font-semibold text-white">{trade.symbol}</td>
      <td className="py-3">
        <span className={isBuy ? "badge-buy" : "badge-sell"}>{trade.trade_type}</span>
      </td>
      <td className="py-3 text-right font-mono text-gray-300 text-xs">
        ${trade.entry_price?.toFixed(4) || "-"}
      </td>
      <td className="py-3 text-right font-mono text-gray-300 text-xs">{trade.quantity}</td>
      <td className={`py-3 text-right font-mono text-sm font-semibold ${pnlPos ? "text-buy-DEFAULT" : "text-sell-DEFAULT"}`}>
        {pnlPos ? "+" : ""}{trade.pnl?.toFixed(4)}
      </td>
      <td className="py-3 text-center">
        <span className={`text-xs px-2 py-0.5 rounded capitalize font-medium ${statusColor[trade.status] || "text-gray-400 bg-gray-400/10"}`}>
          {trade.status}
        </span>
      </td>
    </tr>
  );
}
