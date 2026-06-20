export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: "admin" | "user" | "moderator";
  subscription_plan: "free" | "basic" | "pro" | "enterprise";
  auto_trading_enabled: boolean;
  risk_percent: number;
  max_trades_per_day: number;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: string;
  username: string;
  email: string;
  role: string;
}

export interface Signal {
  id: string;
  symbol: string;
  signal_type: "BUY" | "SELL";
  status: "active" | "triggered" | "expired" | "cancelled";
  confidence_score: number;
  entry_price: number;
  stop_loss: number;
  take_profit_1?: number;
  take_profit_2?: number;
  take_profit_3?: number;
  timeframe: string;
  risk_reward_ratio?: number;
  indicators?: Record<string, number>;
  market_structure?: string;
  trend?: string;
  bos_detected: boolean;
  choch_detected: boolean;
  notes?: string;
  expires_at?: string;
  created_at: string;
}

export interface Trade {
  id: string;
  symbol: string;
  trade_type: "BUY" | "SELL";
  order_type: string;
  market_type: "spot" | "futures";
  status: "pending" | "open" | "closed" | "cancelled" | "failed";
  quantity: number;
  entry_price?: number;
  exit_price?: number;
  stop_loss?: number;
  take_profit?: number;
  leverage: number;
  pnl: number;
  pnl_percent: number;
  fee: number;
  is_auto_trade: boolean;
  is_testnet: boolean;
  opened_at?: string;
  closed_at?: string;
  created_at: string;
}

export interface Position {
  id: string;
  symbol: string;
  market_type: string;
  side: "BUY" | "SELL";
  quantity: number;
  entry_price: number;
  current_price?: number;
  leverage: number;
  unrealized_pnl: number;
  realized_pnl: number;
  stop_loss?: number;
  take_profit?: number;
  is_active: boolean;
  is_testnet: boolean;
  opened_at?: string;
}

export interface ApiKey {
  id: string;
  label: string;
  network_type: "spot_mainnet" | "futures_mainnet" | "spot_testnet" | "futures_testnet";
  is_active: boolean;
  is_verified: boolean;
  permissions?: string;
  last_used?: string;
  created_at: string;
}

export interface PortfolioOverview {
  open_trades: number;
  closed_trades: number;
  total_pnl: number;
  win_rate: number;
  winning_trades: number;
  losing_trades: number;
  binance_balances: BinanceBalance[];
  auto_trading_enabled: boolean;
  risk_percent: number;
}

export interface BinanceBalance {
  asset: string;
  free: string;
  locked: string;
}

export interface Plan {
  id: string;
  name: string;
  slug: string;
  description?: string;
  price_monthly: number;
  price_quarterly?: number;
  price_yearly?: number;
  max_api_keys: number;
  max_auto_trades_per_day: number;
  max_signals_per_day: number;
}

export interface Payment {
  id: string;
  provider: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  data?: Record<string, unknown>;
  created_at: string;
}

export interface AdminStats {
  users: { total: number; active: number; auto_trading: number };
  trades: { total: number; open: number };
  signals: { total: number; active: number };
  revenue: { total: number; currency: string };
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}
