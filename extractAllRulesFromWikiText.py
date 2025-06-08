#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract All Law Rules Links from WikiText
==============================================

This script extracts all <a> tag links (href property) from the Hebrew WikiSource page
that ARE law rules, stores them in a vector (list), and prints them all.

Author: Generated for extractAllRulesFromWikiText project
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
import os
import urllib.parse
from datetime import datetime
from html2docx import html2docx
import sys
import hashlib

HEBREW_MONTHS = {
    "ינואר": 1,
    "פברואר": 2,
    "מרץ": 3,
    "אפריל": 4,
    "מאי": 5,
    "יוני": 6,
    "יולי": 7,
    "אוגוסט": 8,
    "ספטמבר": 9,
    "אוקטובר": 10,
    "נובמבר": 11,
    "דצמבר": 12,
}

def file_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def get_script_dir():
    # Get the directory where the script/exe is located
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (exe)
        return os.path.dirname(sys.executable)
    else:
        # If the application is run from a Python interpreter
        return os.path.dirname(os.path.abspath(__file__))


def fetch_latest_update_date(history_url):
    """Return the latest change date from the history page in dd/MM/yyyy format."""
    try:
        response = requests.get(history_url, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        elem = soup.find(class_="mw-changeslist-date")
        if not elem:
            print("Could not find a changes list date element")
            return None
        text = elem.get_text(strip=True)
        # Expected format: "16:50, 28 במרץ 2025"
        parts = text.split(",", 1)
        date_part = parts[1].strip() if len(parts) > 1 else text
        match = re.search(r"(\d{1,2})\s+ב([^\s]+)\s+(\d{4})", date_part)
        if not match:
            print(f"Unexpected date format: {text}")
            return None
        day = int(match.group(1))
        month_name = match.group(2)
        year = int(match.group(3))
        month = HEBREW_MONTHS.get(month_name)
        if not month:
            print(f"Unknown month name: {month_name}")
            return None
        return f"{day:02d}/{month:02d}/{year}"
    except Exception as e:
        print(f"Error fetching history page: {e}")
        return None


def should_download(history_url, last_file="lastUpdated.txt"):
    """Determine whether files should be downloaded based on last update."""
    last_file = os.path.join(get_script_dir(), last_file)
    
    latest_date = fetch_latest_update_date(history_url)
    if not latest_date:
        print("Could not determine latest date. Assuming download needed.")
        return True

    if not os.path.exists(last_file):
        with open(last_file, "w", encoding="utf-8") as f:
            f.write(latest_date)
        return True

    with open(last_file, "r", encoding="utf-8") as f:
        stored_date = f.read().strip()

    if stored_date != latest_date:
        with open(last_file, "w", encoding="utf-8") as f:
            f.write(latest_date)
        return True

    print("Version unchanged. Skipping download process.")
    return False

class WikiTextLinkExtractor:
    def __init__(self, base_url="https://he.wikisource.org"):
        self.base_url = base_url
        self.session = requests.Session()
        # Set a proper user agent to avoid getting blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def fetch_page_content(self, url):
        """Fetch the content of the given URL"""
        try:
            print(f"Fetching content from: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            print(f"Successfully fetched {len(response.text)} characters")
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def is_law_rule_link(self, href, link_text=""):
        """
        Determine if a link is a law rule based on various criteria
        Returns True if it's a law rule, False otherwise
        """
        if not href:
            return True  # Consider empty hrefs as law rules to filter them out
            
        # Patterns that typically indicate law rules in Hebrew legal documents
        law_patterns = [
            r'חוק',  # Law
            r'פקודת',  # Ordinance
            r'תקנות',  # Regulations
            r'צו',   # Order
            r'הודע',  # Notice
            r'כללי',  # Rules
            r'נוהל',  # Procedure
            r'הורא',  # Instructions
            r'הנחיות',  # Guidance
            r'תקנון',  # Regulations
            r'החלט',  # decision
            r'הנחי',  # instruction
            r'היתר',  # mandate
            r'הכרז',  # declaration
            r'אכרז',  # proposal
            r'דבר',  # proposal
            r'נורמ',  # proposal
            r'הודע',  # proposal
            r'רשימ',  # proposal
            r'דריש',  # proposal
            r'קוו',  # proposal
            r'קביע',  # proposal
            r'רשימ',  # proposal
            r'פרט',  # proposal
        ]
        
        # Check if the href or link text contains law-related terms
        combined_text = f"{href} {link_text}".lower()
        
        for pattern in law_patterns:
            if re.search(pattern, combined_text):
                return True
                
        # Additional checks for specific URL patterns that might indicate laws
        if '/wiki/' in href and any(term in href for term in ['%D7%97%D7%95%D7%A7', '%D7%A4%D7%A7%D7%95%D7%93%D7%AA', '%D7%AA%D7%A7%D7%A0%D7%95%D7%AA']):
            return True
            
        return False
    
    def is_internal_navigation_link(self, href):
        """Check if link is internal navigation (edit, history, etc.)"""
        navigation_patterns = [
            'action=edit',
            'action=history', 
            'oldid=',
            '#',  # anchor links
            'Special:',
            'Help:',
            'Template:',
            'Category:',
            'File:',
            'MediaWiki:',
            '/w/index.php'
        ]
        
        return any(pattern in href for pattern in navigation_patterns)
    
    def extract_law_links(self, url):
        """Extract all law rule links from the given URL"""
        content = self.fetch_page_content(url)
        if not content:
            return []
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all <a> tags with href attributes
        all_links = soup.find_all('a', href=True)
        print(f"Found {len(all_links)} total links")
        
        law_links = []
        
        for link in all_links:
            href = link.get('href', '').strip()
            link_text = link.get_text(strip=True)
            
            if not href:
                continue
                
            # Skip internal navigation links
            if self.is_internal_navigation_link(href):
                continue
                
            # Convert relative URLs to absolute
            if href.startswith('/'):
                full_url = urljoin(self.base_url, href)
            elif href.startswith('http'):
                full_url = href
            else:
                continue  # Skip other relative links
                
            # Check if it IS a law rule
            if self.is_law_rule_link(href, link_text):
                law_links.append({
                    'url': full_url,
                    'text': link_text,
                    'original_href': href
                })
                
        print(f"Filtered to {len(law_links)} law rule links")
        return law_links

    def extract_law_content(self, url):
        """Extract the main content from a law page"""
        content = self.fetch_page_content(url)
        if not content:
            return None
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find the main content div
        main_content = soup.find('div', {'id': 'mw-content-text'})
        if not main_content:
            return None


        # Remove all img elements from the content
        for img in main_content.find_all('img'):
            img.decompose()

        # Remove all span elements with class "mw-editsection"
        for span in main_content.find_all('span', class_="mw-editsection"):
            span.decompose()



        # Create a new HTML document with proper structure
        html_template = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{soup.title.string if soup.title else 'Law Document'}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    {str(main_content)}
</body>
</html>"""
        
        return html_template

    def save_law_contents(self, law_links, max_links=-1):
        """Save the content of law links to files"""
        # Create extracted_rules directory if it doesn't exist
        output_dir = os.path.join(get_script_dir(), "extracted_rules2")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        saved_count = 0
        if max_links <= 1:
            max_links = len(law_links)
        for link_data in law_links[:max_links]:
            try:
                # Extract content
                content = self.extract_law_content(link_data['url'])
                if not content:
                    print(f"Could not extract content from: {link_data['url']}")
                    continue

                file_hash1 = file_hash(content)

                # Create filename from URL
                parsed_url = urlparse(link_data['url'])
                path_parts = parsed_url.path.split('/')
                filename = path_parts[-1] if path_parts[-1] else path_parts[-2]

                # Decode URL-encoded filename
                filename = urllib.parse.unquote(filename)
                
                # Add .htm extension
                file_path = os.path.join(output_dir, f"{filename}.htm")

                file_hash2 = ""
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content2 = f.read()
                        file_hash2 = file_hash(content2)
                if file_hash1 == file_hash2:
                    print(f"File content unchanged: {file_path}")
                    continue

                # Save content to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"Saved content to: {file_path}")

                # Also create a docx file from the HTML content
                try:
                    docx_buffer = html2docx(content, filename)
                    docx_path = os.path.join(output_dir, f"{filename}.docx")
                    with open(docx_path, "wb") as df:
                        df.write(docx_buffer.getvalue())
                    print(f"Saved docx to: {docx_path}")
                except Exception as e:
                    print(f"Error converting to docx: {e}")

                saved_count += 1

                # Add a small delay to be nice to the server
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing {link_data['url']}: {e}")
                
        return saved_count

def main():
    """Main function to execute the link extraction"""
    history_url = (
        "https://he.wikisource.org/w/index.php?title=%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97&action=history"
    )
    if not should_download(history_url):
        return
    target_url = "https://he.wikisource.org/wiki/%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97"
    
    # Create extractor instance
    extractor = WikiTextLinkExtractor()
    
    # Extract law rule links
    law_links_vector = extractor.extract_law_links(target_url)
    
    # Iterate through the vector and print all links
    if law_links_vector:
        for i, link_data in enumerate(law_links_vector, 1):
            print(f"{i:3d}. URL: {link_data['url']}")
            if link_data['text']:
                print(f"     Text: {link_data['text']}")
            print(f"     Original href: {link_data['original_href']}")
            print()
    else:
        print("No law rule links found.")
    
    print(f"\n=== SUMMARY ===")
    print(f"Successfully extracted {len(law_links_vector)} law rule links")
    
    # Save results to file
    output_file = os.path.join(get_script_dir(), "extracted_law_links.txt")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, link_data in enumerate(law_links_vector, 1):
                f.write(f"{i}. {link_data['url']}\n")
                if link_data['text']:
                    f.write(f"   Text: {link_data['text']}\n")
                f.write(f"   Original href: {link_data['original_href']}\n\n")
        print(f"Results also saved to: {output_file}")
    except Exception as e:
        print(f"Error saving to file: {e}")
        
    print("\n=== Extracting Law Contents ===")
    saved_count = extractor.save_law_contents(law_links_vector)
    print(f"\nSuccessfully saved content of {saved_count} law links to the 'extracted_rules' folder")

if __name__ == "__main__":
    main() 