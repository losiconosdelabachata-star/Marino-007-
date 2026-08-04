"""
Daily Blog Scheduler
Orchestrates blog generation, posting, and email blasts for Los Iconos de la Bachata
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from google_photos_api import GooglePhotosClient
from google_drive_api import GoogleDriveClient
from web_search_api import WebSearchClient
from blog_generator import BlogGenerator
from email_service import EmailService
from dotenv import load_dotenv

import paths

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

class BlogScheduler:
    def __init__(self):
        """Initialize the blog scheduler"""
        self.photos_client = GooglePhotosClient()
        self.drive_client = GoogleDriveClient()
        self.search_client = WebSearchClient()
        self.blog_generator = BlogGenerator()
        self.email_service = EmailService()
        self.tracking_file = paths.BLOG_TRACKER
        self.load_tracking()

    def load_tracking(self):
        """Load tracking file to know which photos have been blogged"""
        try:
            with open(self.tracking_file, 'r') as f:
                self.tracked_photos = json.load(f)
        except FileNotFoundError:
            self.tracked_photos = {'processed_photos': [], 'last_run': None}

    def save_tracking(self):
        """Save tracking file"""
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.tracked_photos, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving tracking: {e}")

    def get_next_photo_batch(self):
        """Get the next unprocessed photo for today's blog"""
        try:
            all_photos = self.photos_client.get_all_photos(limit=365)

            # Find first unprocessed photo
            for photo in all_photos:
                if photo['id'] not in self.tracked_photos['processed_photos']:
                    return photo

            print("⚠️  No unprocessed photos found")
            return None

        except Exception as e:
            print(f"❌ Error getting photos: {e}")
            return None

    def get_related_materials(self, photo_date):
        """Get related materials from Google Drive with similar date"""
        try:
            docs = self.drive_client.list_all_documents()
            related = []

            for doc in docs:
                # Match documents with similar dates
                doc_date = doc.get('createdTime', '')[:10]  # YYYY-MM-DD
                if doc_date == photo_date:
                    content = self.drive_client.get_document_content(doc['id'])
                    related.append({
                        'title': doc['name'],
                        'content': content[:500],  # First 500 chars
                        'date': doc_date
                    })

            return related[:3]  # Return top 3

        except Exception as e:
            print(f"❌ Error getting materials: {e}")
            return []

    def get_web_research(self, topic):
        """Search web for related content"""
        try:
            results = self.search_client.search_topic(topic)
            return [
                {
                    'title': r['title'],
                    'snippet': r['snippet'],
                    'url': r['url']
                }
                for r in results
            ]
        except Exception as e:
            print(f"❌ Error searching web: {e}")
            return []

    def notify_whatsapp(self, blog_title, recipient_count):
        """Tell Marino a post went live. Never fails the run - a missing
        alert is not a reason to lose a published blog."""
        try:
            import whatsapp_client

            status = whatsapp_client.check_status()
            if not status.get('connected'):
                print("   ⚠️  WhatsApp not linked - skipping alert")
                print("      Re-link from the dashboard's WhatsApp panel.")
                return

            message = (
                "📝 NEW BLOG POSTED\n"
                f"{blog_title}\n\n"
                f"📧 Emailed to {recipient_count} customers\n"
                f"🕒 {datetime.now().strftime('%b %d, %Y at %I:%M %p')}"
            )
            result = whatsapp_client.send_to_marino(message)
            if result.get('success'):
                print("   ✅ WhatsApp alert sent")
            else:
                print(f"   ⚠️  Alert not delivered: {result.get('error', 'unknown')}")
        except Exception as e:
            print(f"   ⚠️  WhatsApp alert failed: {e}")

    def generate_daily_blog(self):
        """Generate and post a daily blog"""
        try:
            print("\n" + "="*60)
            print("🎵 STARTING DAILY BLOG GENERATION")
            print("="*60)

            # Step 1: Get next photo
            print("\n1️⃣  Fetching next photo...")
            photo = self.get_next_photo_batch()
            if not photo:
                print("⚠️  No photos to process")
                return False

            photo_date = str(photo.get('created_time', ''))[:10]
            topic = f"{photo.get('description', 'Los Iconos Moment')} ({photo_date})"
            print(f"   ✅ Photo: {topic}")

            # Step 2: Get related materials
            print("\n2️⃣  Gathering related materials...")
            materials = self.get_related_materials(photo_date)
            print(f"   ✅ Found {len(materials)} related documents")

            # Step 3: Search web
            print("\n3️⃣  Researching topic...")
            research = self.get_web_research(topic)
            print(f"   ✅ Found {len(research)} web articles")

            # Step 4: Generate blog post
            print("\n4️⃣  Generating blog post with Claude...")
            blog_result = self.blog_generator.generate_blog_post(
                topic,
                materials,
                research,
                [photo]
            )

            if not blog_result['success']:
                print(f"   ❌ Blog generation failed: {blog_result['error']}")
                return False

            print(f"   ✅ Blog generated ({blog_result['token_usage']['output']} tokens)")

            # Step 5: Generate title
            print("\n5️⃣  Creating title and metadata...")
            blog_title = self.blog_generator.generate_blog_title(topic, materials)
            email_subject = self.blog_generator.generate_email_subject(blog_title)
            print(f"   ✅ Title: {blog_title}")

            # Step 6: Save blog post
            print("\n6️⃣  Saving blog post...")
            filepath = self.blog_generator.save_blog_post(
                blog_title,
                blog_result['content'],
                topic.replace(' ', '_')
            )
            print(f"   ✅ Saved: {filepath}")

            # Step 7: Send promotional emails
            print("\n7️⃣  Sending promotional emails...")
            customer_emails = self.email_service.load_customer_emails()

            if customer_emails:
                # Get products to promote (you'd fetch these from Shopify)
                products = [
                    {'name': 'Latest Album', 'price': '29.99', 'url': 'https://shop.losiconosdelabachata.com'},
                    {'name': 'Merchandise', 'price': '19.99', 'url': 'https://shop.losiconosdelabachata.com'},
                    {'name': 'Concert Tickets', 'price': '75.00', 'url': 'https://tickets.losiconosdelabachata.com'},
                ]

                blog_url = f"https://blog.losiconosdelabachata.com/{filepath.split('/')[-1]}"

                self.email_service.send_blast_email(
                    customer_emails,
                    email_subject,
                    blog_title,
                    blog_result['content'][:300],
                    blog_url,
                    products
                )
                print(f"   ✅ Emails sent to {len(customer_emails)} customers")
            else:
                print("   ⚠️  No customer emails found")

            # Step 8: Update tracking
            print("\n8️⃣  Updating tracking...")
            self.tracked_photos['processed_photos'].append(photo['id'])
            self.tracked_photos['last_run'] = datetime.now().isoformat()
            self.save_tracking()
            print("   ✅ Tracking updated")

            # Step 9: Ping Marino on WhatsApp so a post never goes out unnoticed
            print("\n9️⃣  Sending WhatsApp alert...")
            self.notify_whatsapp(blog_title, len(customer_emails or []))

            print("\n" + "="*60)
            print("✅ DAILY BLOG COMPLETE!")
            print("="*60 + "\n")

            return True

        except Exception as e:
            print(f"❌ Error in blog generation: {e}")
            return False

    def schedule_daily_run(self):
        """Schedule blog generation to run daily at specified time"""
        # Run at 9 AM every day
        target_hour = 9
        target_minute = 0

        print(f"📅 Blog scheduler running. Will generate blogs daily at {target_hour}:{target_minute:02d}")

        while True:
            now = datetime.now()
            target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

            # If target time has passed today, schedule for tomorrow
            if now > target_time:
                target_time += timedelta(days=1)

            # Calculate wait time
            wait_seconds = (target_time - now).total_seconds()

            print(f"\n⏰ Next blog generation: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Waiting {int(wait_seconds / 3600)} hours {int((wait_seconds % 3600) / 60)} minutes...\n")

            # Wait until target time
            time.sleep(wait_seconds)

            # Generate blog
            self.generate_daily_blog()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Daily blog generator for Los Iconos")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Generate one post and exit. The dashboard's 'Post blog now' button uses this.",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Stay running and publish on the schedule in .env (BLOG_SCHEDULE_HOUR).",
    )
    args = parser.parse_args()

    scheduler = BlogScheduler()

    if args.daemon:
        scheduler.schedule_daily_run()
    else:
        # --once and the bare invocation both mean "one post, then exit"
        print("Generating one blog now...")
        scheduler.generate_daily_blog()
