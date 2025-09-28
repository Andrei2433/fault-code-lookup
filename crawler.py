#!/usr/bin/env python3
"""
Ross-Tech VCDS Fault Codes Crawler

This script crawls the Ross-Tech wiki to extract fault codes and their details,
then saves them to a SQLite database for offline use.
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FaultCodeCrawler:
    def __init__(self, db_path: str = "fault_codes.db"):
        self.db_path = db_path
        self.base_url = "https://wiki.ross-tech.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.test_mode = False
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with the required schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fault_codes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                title TEXT,
                symptoms TEXT,
                causes TEXT,
                solutions TEXT,
                UNIQUE(code)
            )
        ''')
        
        # Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE fault_codes ADD COLUMN full_content TEXT")
            logger.info("Added full_content column")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE fault_codes ADD COLUMN special_notes TEXT")
            logger.info("Added special_notes column")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE fault_codes ADD COLUMN technical_info TEXT")
            logger.info("Added technical_info column")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def get_fault_code_links_from_page(self, url: str) -> tuple:
        """Extract fault code links from a single page and return next page URL."""
        logger.info(f"Fetching fault code links from: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links in the category page
            links = []
            
            # Try multiple selectors for the category content
            category_selectors = [
                'div#mw-pages',
                'div.mw-category',
                'div.mw-category-group',
                'div#content',
                'div.mw-content-ltr'
            ]
            
            category_content = None
            for selector in category_selectors:
                category_content = soup.select_one(selector)
                if category_content:
                    logger.info(f"Found category content using selector: {selector}")
                    break
            
            if category_content:
                # Look for all links that might be fault codes
                all_links = category_content.find_all('a', href=True)
                logger.info(f"Found {len(all_links)} total links in category content")
                
                for link in all_links:
                    href = link['href']
                    link_text = link.get_text().strip()
                    
                    # Check if this looks like a fault code link
                    if any(indicator in href.lower() for indicator in ['fault_code', 'fault-code', 'faultcode']):
                        full_url = urljoin(self.base_url, href)
                        links.append(full_url)
                        logger.debug(f"Found fault code link: {link_text} -> {full_url}")
                    # Also check if the link text contains a 5-digit code
                    elif re.search(r'\d{5}', link_text):
                        full_url = urljoin(self.base_url, href)
                        links.append(full_url)
                        logger.debug(f"Found potential fault code link by text: {link_text} -> {full_url}")
            
            # If we still haven't found links, try a broader search
            if not links:
                logger.info("No links found with specific selectors, trying broader search...")
                all_links = soup.find_all('a', href=True)
                logger.info(f"Found {len(all_links)} total links on page")
                
                for link in all_links:
                    href = link['href']
                    link_text = link.get_text().strip()
                    
                    # Look for links that contain fault code patterns
                    if (re.search(r'\d{5}', link_text) and 
                        ('fault' in link_text.lower() or 'code' in link_text.lower())):
                        full_url = urljoin(self.base_url, href)
                        links.append(full_url)
                        logger.debug(f"Found fault code link (broad search): {link_text} -> {full_url}")
            
            # Look for next page link
            next_page_url = None
            pagination_selectors = [
                'div.mw-category-group a',
                'div#mw-pages a',
                'a[href*="pagefrom"]'
            ]
            
            for selector in pagination_selectors:
                pagination_links = soup.select(selector)
                for link in pagination_links:
                    href = link.get('href', '')
                    link_text = link.get_text().strip()
                    
                    # Look for "next page" links
                    if 'pagefrom=' in href and 'next' in link_text.lower():
                        next_page_url = urljoin(self.base_url, href)
                        logger.info(f"Found next page link: {link_text} -> {next_page_url}")
                        break
                if next_page_url:
                    break
            
            logger.info(f"Found {len(links)} fault code links on this page")
            return links, next_page_url
            
        except requests.RequestException as e:
            logger.error(f"Error fetching page {url}: {e}")
            return [], None
    
    def get_all_fault_code_links(self, start_url: str) -> List[str]:
        """Get all fault code links from all pages."""
        all_links = []
        current_url = start_url
        page_count = 0
        max_pages = 50  # Safety limit to prevent infinite loops
        
        logger.info("Starting to crawl all pages for fault code links...")
        
        while current_url and page_count < max_pages:
            page_count += 1
            logger.info(f"Processing page {page_count}...")
            
            links, next_url = self.get_fault_code_links_from_page(current_url)
            all_links.extend(links)
            
            logger.info(f"Page {page_count}: Found {len(links)} links (Total so far: {len(all_links)})")
            
            if not next_url:
                logger.info("No more pages found. Crawling complete.")
                break
                
            current_url = next_url
            time.sleep(1)  # Be respectful to the server
        
        if page_count >= max_pages:
            logger.warning(f"Reached maximum page limit ({max_pages}). There might be more pages.")
        
        logger.info(f"Total fault code links found across {page_count} pages: {len(all_links)}")
        return all_links
    
    def extract_fault_code_data(self, url: str) -> Optional[Dict[str, str]]:
        """Extract fault code data from a single page."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract fault code from URL or page title
            fault_code = self.extract_code_from_url(url)
            if not fault_code:
                # Try to extract from page title
                title_element = soup.find('h1', {'class': 'firstHeading'})
                if title_element:
                    title_text = title_element.get_text()
                    code_match = re.search(r'(\d{5})', title_text)
                    if code_match:
                        fault_code = code_match.group(1)
            
            if not fault_code:
                logger.warning(f"Could not extract fault code from: {url}")
                return None
            
            # Extract title
            title = self.extract_title(soup)
            
            # Extract all main content
            full_content = self.extract_full_content(soup)
            
            # Extract specific sections
            symptoms = self.extract_section(soup, ['Possible Symptoms', 'Symptoms'])
            causes = self.extract_section(soup, ['Possible Causes', 'Causes'])
            solutions = self.extract_section(soup, ['Possible Solutions', 'Solutions'])
            special_notes = self.extract_section(soup, ['Special Notes', 'Notes', 'Additional Information', 'Additional Notes'])
            technical_info = self.extract_section(soup, ['Technical Information', 'Technical Details', 'Specifications', 'Technical Data'])
            
            return {
                'code': fault_code,
                'title': title,
                'full_content': full_content,
                'symptoms': symptoms,
                'causes': causes,
                'solutions': solutions,
                'special_notes': special_notes,
                'technical_info': technical_info
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching page {url}: {e}")
            return None
    
    def extract_code_from_url(self, url: str) -> Optional[str]:
        """Extract fault code from URL."""
        # Look for 5-digit codes in the URL
        code_match = re.search(r'(\d{5})', url)
        return code_match.group(1) if code_match else None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the title from the page."""
        title_element = soup.find('h1', {'class': 'firstHeading'})
        if title_element:
            title_text = title_element.get_text().strip()
            # Remove fault code from title if present
            title_text = re.sub(r'^\d{5}\s*[-:]\s*', '', title_text)
            return title_text
        return ""
    
    def extract_full_content(self, soup: BeautifulSoup) -> str:
        """Extract all main content from the page."""
        content_parts = []
        
        # Find the main content area
        content_selectors = [
            'div#mw-content-text',
            'div.mw-content-ltr',
            'div#content',
            'div.mw-parser-output'
        ]
        
        content_area = None
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                break
        
        if not content_area:
            return ""
        
        # Extract all text content, preserving structure
        for element in content_area.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'div', 'span']):
            text = element.get_text().strip()
            if text and len(text) > 3:  # Only include meaningful text
                # Add element type for context
                tag_name = element.name
                if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    content_parts.append(f"\n{text}\n")
                elif tag_name in ['ul', 'ol']:
                    content_parts.append(f"\n{text}\n")
                else:
                    content_parts.append(text)
        
        return '\n'.join(content_parts)
    
    def extract_section(self, soup: BeautifulSoup, section_names: List[str]) -> str:
        """Extract content from a specific section."""
        for section_name in section_names:
            # Look for headings with the section name (more flexible matching)
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            for heading in headings:
                heading_text = heading.get_text().strip()
                # Check if this heading matches any of our section names
                if any(name.lower() in heading_text.lower() for name in section_names):
                    content = []
                    # Get the next sibling elements until we hit another heading
                    for sibling in heading.find_next_siblings():
                        if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            break
                        if sibling.name in ['p', 'ul', 'ol', 'div', 'li', 'span']:
                            text = sibling.get_text().strip()
                            if text and len(text) > 2:
                                content.append(text)
                    
                    if content:
                        return '\n'.join(content)
        
        return ""
    
    def save_fault_code(self, data: Dict[str, str]):
        """Save fault code data to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO fault_codes 
                (code, title, full_content, symptoms, causes, solutions, special_notes, technical_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['code'], 
                data['title'], 
                data['full_content'],
                data['symptoms'], 
                data['causes'], 
                data['solutions'],
                data['special_notes'],
                data['technical_info']
            ))
            
            conn.commit()
            logger.info(f"Saved fault code: {data['code']} - {data['title']}")
            
        except sqlite3.Error as e:
            logger.error(f"Database error saving {data['code']}: {e}")
        finally:
            conn.close()
    
    def crawl_all_fault_codes(self, start_url: str):
        """Main method to crawl all fault codes."""
        logger.info("Starting fault code crawling...")
        
        # Get all fault code links from all pages
        links = self.get_all_fault_code_links(start_url)
        
        if not links:
            logger.error("No fault code links found!")
            return
        
        # Limit links in test mode
        if self.test_mode:
            links = links[:5]
            logger.info(f"Test mode: Processing only first {len(links)} fault code pages...")
        else:
            logger.info(f"Processing {len(links)} fault code pages...")
        
        success_count = 0
        error_count = 0
        
        for i, link in enumerate(links, 1):
            logger.info(f"Processing {i}/{len(links)}: {link}")
            
            data = self.extract_fault_code_data(link)
            if data:
                self.save_fault_code(data)
                success_count += 1
            else:
                error_count += 1
            
            # Be respectful to the server
            time.sleep(1)
            
            # Progress update every 10 items (or every item in test mode)
            if self.test_mode or i % 10 == 0:
                logger.info(f"Progress: {i}/{len(links)} completed. Success: {success_count}, Errors: {error_count}")
        
        logger.info(f"Crawling completed! Success: {success_count}, Errors: {error_count}")
    
    def get_database_stats(self):
        """Get statistics about the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM fault_codes")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

def main():
    """Main function to run the crawler."""
    start_url = "https://wiki.ross-tech.com/wiki/index.php?title=Category:Fault_Codes&pageuntil=01262#mw-pages"
    
    crawler = FaultCodeCrawler()
    
    print("Ross-Tech VCDS Fault Codes Crawler")
    print("=" * 40)
    print(f"Starting URL: {start_url}")
    print(f"Database: {crawler.db_path}")
    print()
    
    # Check if database already has data
    existing_count = crawler.get_database_stats()
    if existing_count > 0:
        response = input(f"Database already contains {existing_count} fault codes. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Crawling cancelled.")
            return
    
    # Ask if user wants to test with a few fault codes first
    test_mode = input("Run in test mode (crawl only first 5 fault codes)? (y/n): ")
    if test_mode.lower() == 'y':
        print("Running in test mode - will crawl only first 5 fault codes")
        crawler.test_mode = True
    else:
        crawler.test_mode = False
    
    try:
        crawler.crawl_all_fault_codes(start_url)
        
        final_count = crawler.get_database_stats()
        print(f"\nCrawling completed! Database now contains {final_count} fault codes.")
        
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
