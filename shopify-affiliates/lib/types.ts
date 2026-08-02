export interface Affiliate {
  id: string;
  shopify_id: string | null;
  name: string;
  email: string;
  phone: string | null;
  status: string;
  commission_rate: number;
  total_sales: number;
  total_commissions: number;
  created_at: string;
}

export interface Message {
  id: string;
  from_id: string;
  to_id: string | null;
  message: string;
  is_broadcast: number;
  created_at: string;
}

export interface AffiliateStats {
  id: string;
  name: string;
  email: string;
  order_count: number | null;
  total_sales: number | null;
  total_commissions: number | null;
  avg_commission: number | null;
}
