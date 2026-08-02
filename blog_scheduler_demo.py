#!/usr/bin/env python3
"""
Blog Scheduler - DEMO MODE
Tests the entire blog generation pipeline without requiring Google Photos
"""

import os
import json
from datetime import datetime
from blog_generator import BlogGenerator
from dotenv import load_dotenv

load_dotenv()

if not os.getenv('ANTHROPIC_API_KEY'):
    raise SystemExit("ANTHROPIC_API_KEY missing. Add it to .env before running.")

class DemoBlogScheduler:
    def __init__(self):
        self.blog_generator = BlogGenerator()
        self.tracking_file = 'blog_tracker.json'
        self.load_tracking()

    def load_tracking(self):
        try:
            with open(self.tracking_file, 'r') as f:
                self.tracked_photos = json.load(f)
        except FileNotFoundError:
            self.tracked_photos = {'processed_photos': [], 'last_run': None}

    def save_tracking(self):
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.tracked_photos, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving tracking: {e}")

    def generate_demo_blog(self):
        """Generate a demo blog post for testing"""
        try:
            print("\n" + "="*60)
            print("🎵 DEMO MODE - BLOG GENERATION TEST")
            print("="*60)

            # Demo data (simulating fetched content)
            topic = "Los Iconos de la Bachata: A Timeless Musical Journey"

            demo_materials = [
                {
                    'title': 'Concert Performance Archives',
                    'content': 'Los Iconos de la Bachata has been performing worldwide since the 1980s, bringing authentic bachata music to audiences across the globe.',
                    'date': '2026-08-02'
                },
                {
                    'title': 'Music History Documentation',
                    'content': 'The group revolutionized bachata music by blending traditional Dominican sounds with contemporary production techniques.',
                    'date': '2026-08-02'
                }
            ]

            demo_research = [
                {
                    'title': 'Bachata Music Evolution',
                    'snippet': 'Bachata originated in the Dominican Republic and has evolved into one of the most popular Latin music genres worldwide.',
                    'url': 'https://musichistory.example.com/bachata'
                },
                {
                    'title': 'Los Iconos Cultural Impact',
                    'snippet': 'The group has influenced a generation of musicians and continues to draw passionate fans from around the world.',
                    'url': 'https://culture.example.com/los-iconos'
                }
            ]

            demo_images = [
                {
                    'name': 'performance_2026.jpg',
                    'date': '2026-08-02',
                    'description': 'Los Iconos performing at sold-out venue'
                }
            ]

            # Step 1: Generate blog post
            print("\n1️⃣  Generating blog post with Claude AI...")
            blog_result = self.blog_generator.generate_blog_post(
                topic,
                demo_materials,
                demo_research,
                demo_images
            )

            if not blog_result['success']:
                print(f"   ❌ Blog generation failed: {blog_result['error']}")
                return False

            print(f"   ✅ Blog generated ({blog_result['token_usage']['output']} tokens)")

            # Step 2: Generate title
            print("\n2️⃣  Creating title and metadata...")
            blog_title = self.blog_generator.generate_blog_title(topic, demo_materials)
            email_subject = self.blog_generator.generate_email_subject(blog_title)
            print(f"   ✅ Title: {blog_title}")
            print(f"   ✅ Email: {email_subject}")

            # Step 3: Save blog post
            print("\n3️⃣  Saving blog post...")
            filepath = self.blog_generator.save_blog_post(
                blog_title,
                blog_result['content'],
                'demo_test_blog'
            )
            print(f"   ✅ Saved: {filepath}")

            # Step 4: Show what would be emailed
            print("\n4️⃣  Email preview:")
            print(f"   Subject: {email_subject}")
            print(f"   Recipients: 3 test customers")
            print(f"   Blog URL: https://blog.losiconosdelabachata.com/{filepath.split(chr(92))[-1]}")
            print(f"   Preview: {blog_result['content'][:150]}...")

            # Step 5: Track (demo)
            print("\n5️⃣  Tracking...")
            self.tracked_photos['processed_photos'].append('demo_photo_001')
            self.tracked_photos['last_run'] = datetime.now().isoformat()
            self.save_tracking()
            print("   ✅ Demo blog tracked")

            print("\n" + "="*60)
            print("✅ DEMO COMPLETE!")
            print("="*60)
            print("""
Your blog engine is WORKING! 🎉

Next steps:
1. Check your blogs/ folder for the generated HTML file
2. Review the blog post content
3. When ready with Google Photos, run: python blog_scheduler.py

For production:
  python start_marino_007.py

This will run WhatsApp + Blog Engine together!
            """)

            return True

        except Exception as e:
            print(f"❌ Error in demo generation: {e}")
            return False

if __name__ == "__main__":
    scheduler = DemoBlogScheduler()
    scheduler.generate_demo_blog()
