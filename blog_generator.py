"""
Blog Generator
Uses Claude AI to generate engaging blog posts from materials and web research
"""

import os
import sys
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

class BlogGenerator:
    def __init__(self):
        """Initialize blog generator with Claude"""
        self.client = Anthropic()
        self.model = "claude-sonnet-5"
        self.brand = "Los Iconos de la Bachata"

    def generate_blog_post(self, topic, materials, web_research, images_info):
        """Generate a blog post using Claude AI"""
        try:
            # Format the prompt
            prompt = f"""
You are a professional music blog writer for {self.brand}, a legendary bachata group.

Generate an engaging, informative blog post based on this material:

**Topic:** {topic}

**Materials from Photos/Drive:**
{json.dumps(materials, indent=2)}

**Web Research:**
{json.dumps(web_research, indent=2)}

**Associated Images:**
{json.dumps(images_info, indent=2)}

Please create a blog post that:
1. Starts with an engaging headline and introduction
2. Incorporates the materials and research naturally
3. Tells a compelling story about {self.brand}
4. Includes mentions of the photos/materials
5. Ends with a call-to-action (product promotion or newsletter signup)
6. Is 800-1200 words long
7. Uses a warm, personal tone appropriate for fans

Format: Return as HTML with proper tags (h1, p, img, etc.)
"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response (handle different content types)
            blog_content = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    blog_content += block.text
            return {
                'success': True,
                'content': blog_content,
                'generated_at': datetime.now().isoformat(),
                'token_usage': {
                    'input': message.usage.input_tokens,
                    'output': message.usage.output_tokens
                }
            }

        except Exception as e:
            print(f"❌ Error generating blog: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_blog_title(self, topic, materials):
        """Generate an engaging blog title"""
        try:
            prompt = f"""
Generate a compelling, SEO-friendly blog post title for {self.brand}.

Topic: {topic}
Context: {json.dumps(materials[:1], indent=2) if materials else 'General music blog'}

Requirements:
- Under 60 characters
- Include relevant keywords
- Be engaging and clickable
- Reflect the warm, personal brand of {self.brand}

Return ONLY the title, nothing else.
"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return message.content[0].text.strip()

        except Exception as e:
            print(f"❌ Error generating title: {e}")
            return f"New Story from {self.brand}"

    def generate_email_subject(self, blog_title):
        """Generate an engaging email subject"""
        try:
            prompt = f"""
Generate an engaging email subject line for a promotional email about this blog post.

Blog Title: {blog_title}

Requirements:
- Under 50 characters
- Include emoji if appropriate
- Create urgency or curiosity
- Encourage opens

Return ONLY the subject line, nothing else.
"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return message.content[0].text.strip()

        except Exception as e:
            print(f"❌ Error generating subject: {e}")
            return f"New from {self.brand}: {blog_title[:30]}"

    def save_blog_post(self, title, content, topic, output_dir='blogs'):
        """Save blog post to file"""
        try:
            # Create directory if needed
            os.makedirs(output_dir, exist_ok=True)

            # Create filename from title
            filename = f"{datetime.now().strftime('%Y-%m-%d')}_{topic.replace(' ', '_').lower()[:30]}.html"
            filepath = os.path.join(output_dir, filename)

            # Wrap in HTML template
            full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #d4af37;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 10px;
        }}
        h2, h3 {{
            color: #d4af37;
        }}
        .blog-meta {{
            color: #999;
            font-style: italic;
            margin-bottom: 20px;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <article>
        <h1>{title}</h1>
        <div class="blog-meta">
            Published on {datetime.now().strftime('%B %d, %Y')} | {self.brand}
        </div>
        {content}
    </article>
</body>
</html>
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_html)

            print(f"✅ Blog saved: {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ Error saving blog: {e}")
            return None

if __name__ == "__main__":
    generator = BlogGenerator()

    # Example usage
    test_topic = "Journey Through Time"
    test_materials = [
        {"date": "2015", "description": "Early performances", "photo_count": 15}
    ]
    test_research = [
        {"title": "The Evolution of Bachata", "snippet": "Bachata music has evolved..."}
    ]
    test_images = [
        {"name": "concert_2015.jpg", "date": "2015-05-12"}
    ]

    # Generate blog
    result = generator.generate_blog_post(test_topic, test_materials, test_research, test_images)

    if result['success']:
        title = generator.generate_blog_title(test_topic, test_materials)
        filepath = generator.save_blog_post(title, result['content'], test_topic)
        print(f"Blog generated: {title}")
    else:
        print(f"Error: {result['error']}")
