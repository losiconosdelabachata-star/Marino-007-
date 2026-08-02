import fetch from 'node-fetch';

const SHOPIFY_STORE = process.env.SHOPIFY_STORE;
const API_KEY = process.env.SHOPIFY_API_KEY;
const API_PASSWORD = process.env.SHOPIFY_API_PASSWORD;

const baseUrl = `https://${API_KEY}:${API_PASSWORD}@${SHOPIFY_STORE}/admin/api/2024-01`;

export async function fetchAffiliates() {
  try {
    const response = await fetch(`${baseUrl}/metafields.json?namespace=affiliate`, {
      method: 'GET',
    });
    const data = await response.json();
    return data.metafields || [];
  } catch (error) {
    console.error('Error fetching affiliates:', error);
    return [];
  }
}

export async function getOrdersByAffiliate(affiliateId: string) {
  try {
    const response = await fetch(
      `${baseUrl}/orders.json?fields=id,total_price,created_at&limit=250`,
      { method: 'GET' }
    );
    const data = await response.json();
    return data.orders || [];
  } catch (error) {
    console.error('Error fetching orders:', error);
    return [];
  }
}

export async function getShopInfo() {
  try {
    const response = await fetch(`${baseUrl}/shop.json`, { method: 'GET' });
    const data = await response.json();
    return data.shop;
  } catch (error) {
    console.error('Error fetching shop info:', error);
    return null;
  }
}
