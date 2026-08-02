"""
Google Ads API Client
Creates and manages Google Ads campaigns targeting Aventura/Latin music fans
"""

import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import json

# Configuration
CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "79579797793")  # Without hyphens
DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")

def init_google_ads_client():
    """Initialize Google Ads API client"""
    if not all([DEVELOPER_TOKEN, CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        raise ValueError("Missing Google Ads credentials in .env")

    client = GoogleAdsClient.load_from_env(version="v17")
    return client

def create_campaign(client, campaign_name: str, budget_amount_micros: int) -> dict:
    """Create a new Google Ads campaign"""
    try:
        campaign_service = client.get_service("CampaignService")
        campaign_budget_service = client.get_service("CampaignBudgetService")

        # Create campaign budget
        campaign_budget = client.get_type("CampaignBudget")
        campaign_budget.name = f"{campaign_name} Budget"
        campaign_budget.amount_micros = budget_amount_micros
        campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD

        budget_operation = client.get_type("CampaignBudgetOperation")
        budget_operation.create = campaign_budget

        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=CUSTOMER_ID, operations=[budget_operation]
        )
        budget_id = budget_response.results[0].resource_name

        # Create campaign
        campaign = client.get_type("Campaign")
        campaign.name = campaign_name
        campaign.campaign_budget = budget_id
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.network_settings.target_search_network = True

        campaign_operation = client.get_type("CampaignOperation")
        campaign_operation.create = campaign

        campaign_response = campaign_service.mutate_campaigns(
            customer_id=CUSTOMER_ID, operations=[campaign_operation]
        )

        return {
            "success": True,
            "campaign_id": campaign_response.results[0].resource_name,
            "campaign_name": campaign_name,
            "budget": budget_amount_micros / 1_000_000
        }

    except GoogleAdsException as ex:
        return {
            "success": False,
            "error": str(ex)
        }

def get_campaigns() -> list:
    """Get all campaigns for this account"""
    try:
        client = init_google_ads_client()
        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign_budget.amount_micros
            FROM campaign
            ORDER BY campaign.id
        """

        results = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)

        campaigns = []
        for batch in results:
            for row in batch.results:
                campaigns.append({
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status,
                    "budget": row.campaign_budget.amount_micros / 1_000_000 if row.campaign_budget else 0
                })

        return campaigns

    except GoogleAdsException as ex:
        print(f"Error fetching campaigns: {ex}")
        return []

def pause_campaign(client, campaign_id: str) -> dict:
    """Pause a campaign"""
    try:
        campaign_service = client.get_service("CampaignService")

        campaign = client.get_type("Campaign")
        campaign.resource_name = f"customers/{CUSTOMER_ID}/campaigns/{campaign_id}"
        campaign.status = client.enums.CampaignStatusEnum.PAUSED

        operation = client.get_type("CampaignOperation")
        operation.update = campaign
        operation.update_mask.paths.append("status")

        response = campaign_service.mutate_campaigns(
            customer_id=CUSTOMER_ID, operations=[operation]
        )

        return {
            "success": True,
            "message": f"Campaign {campaign_id} paused"
        }

    except GoogleAdsException as ex:
        return {
            "success": False,
            "error": str(ex)
        }

def create_aventura_campaigns():
    """Create sample Aventura/Latin music targeting campaigns"""
    try:
        client = init_google_ads_client()

        campaigns_to_create = [
            ("Los Iconos - Aventura Discovery", 50_000_000),  # $50/day
            ("Los Iconos - Bachata Focus", 30_000_000),  # $30/day
            ("Los Iconos - Latin Music Fans", 40_000_000),  # $40/day
        ]

        results = []
        for campaign_name, budget in campaigns_to_create:
            result = create_campaign(client, campaign_name, budget)
            results.append(result)

        return {
            "success": True,
            "campaigns_created": len(results),
            "details": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Test function
if __name__ == "__main__":
    print("Google Ads API module loaded")
    print(f"Customer ID: {CUSTOMER_ID}")
    print(f"Developer Token: {'SET' if DEVELOPER_TOKEN else 'NOT SET'}")
    print(f"OAuth Credentials: {'SET' if all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]) else 'NOT SET'}")
