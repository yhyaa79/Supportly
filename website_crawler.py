from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from collections import deque
import re

import os
from urllib.parse import urlparse

def setup_output_folder(base_url):

    main_folder = "advanced_website_crawler"
    os.makedirs(main_folder, exist_ok=True)
    
    domain = urlparse(base_url).netloc
    folder_name = domain.replace('www.', '')
    folder_path = os.path.join(main_folder, folder_name)
    
    if os.path.exists(folder_path):
        print(f"The information on this site has already been extracted!")
        print(f"path: {folder_path}")
        print("No operation was performed.")
        return None
    
    os.makedirs(folder_path, exist_ok=True)
    print(f"New folder created:")
    print(f"   {folder_path}")
    return folder_path


class AdvancedWebsiteCrawler:
    def __init__(self, base_url, max_pages=100, headless=True):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls = set()
        self.pages_data = []
        self.domain = urlparse(base_url).netloc
        
        # Create an output folder
        self.output_folder = setup_output_folder(base_url)
        if not self.output_folder:
            raise SystemExit("خزیدن متوقف شد.")
        
        # Settings Selenium
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def is_valid_url(self, url):
        if not url or url.startswith('#') or url.startswith('javascript:'):
            return False
            
        parsed = urlparse(url)
        return (parsed.netloc == self.domain and 
                parsed.scheme in ['http', 'https'] and
                not any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.mp4', '.css', '.js']))
    
    def scroll_page(self):
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(3):  
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            print(f"Scroll error: {e}")
    
    def extract_page_content(self, url):
        try:
            self.driver.get(url)
            
            time.sleep(3)
            
            self.scroll_page()
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            for tag in soup(['script', 'style', 'noscript']):
                tag.decompose()
            
            title = self.driver.title or ''
            
            meta_desc = ''
            try:
                meta_element = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
                meta_desc = meta_element.get_attribute('content') or ''
            except:
                pass
            
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                text_content = body.text
                text_content = re.sub(r'\s+', ' ', text_content).strip()
            except:
                text_content = soup.get_text(separator=' ', strip=True)
            
            headings = []
            for i in range(1, 7):
                try:
                    heading_elements = self.driver.find_elements(By.TAG_NAME, f'h{i}')
                    for heading in heading_elements:
                        h_text = heading.text.strip()
                        if h_text:
                            headings.append(h_text)
                except:
                    pass
            
            links = []
            try:
                link_elements = self.driver.find_elements(By.TAG_NAME, 'a')
                for link in link_elements:
                    try:
                        href = link.get_attribute('href')
                        if href:
                            absolute_url = urljoin(url, href)
                            absolute_url = absolute_url.split('#')[0]
                            if self.is_valid_url(absolute_url):
                                links.append(absolute_url)
                    except:
                        continue
            except:
                pass
            
            page_data = {
                'url': url,
                'title': title,
                'meta_description': meta_desc,
                'headings': headings,
                'content': text_content[:8000], 
                'content_length': len(text_content),
                'links': list(set(links)),
                'links_count': len(set(links))
            }
            
            return page_data
            
        except Exception as e:
            print(f"error: {url}: {str(e)}")
            return None
    
    def crawl(self):
        queue = deque([self.base_url])
        self.visited_urls.add(self.base_url)
        
        try:
            while queue and len(self.pages_data) < self.max_pages:
                current_url = queue.popleft()
                print(f"\n📄 [{len(self.pages_data) + 1}/{self.max_pages}] {current_url}")
                
                page_data = self.extract_page_content(current_url)
                
                if page_data:
                    self.pages_data.append(page_data)
                    
                    new_links = 0
                    for link in page_data['links']:
                        if link not in self.visited_urls and len(self.visited_urls) < self.max_pages * 2:
                            self.visited_urls.add(link)
                            queue.append(link)
                            new_links += 1
                                    
                time.sleep(2)  
            
        finally:
            self.driver.quit()
        
        return self.pages_data
    
    def save_to_file(self, filename='website_data.json'):
        filepath = os.path.join(self.output_folder, filename)
        data = {
            'base_url': self.base_url,
            'total_pages': len(self.pages_data),
            'total_urls_discovered': len(self.visited_urls),
            'crawled_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'pages': self.pages_data
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"saved:\n {filepath}")
        
    
    def create_sitemap(self, filename='sitemap.txt'):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Site map: {self.base_url}\n")
            f.write(f"# Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Number of pages: {len(self.pages_data)}\n\n")
            
            for i, page in enumerate(self.pages_data, 1):
                f.write(f"{i}. {page['url']}\n")
                f.write(f"   Title: {page['title']}\n")
                f.write(f"   Number of links: {page['links_count']}\n\n")
        
        print(f"🗺️  Site map saved to file {filename}")
    
    def create_summary(self, filename='summary.txt'):
            filepath = os.path.join(self.output_folder, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write(f"Website Crawling Report\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Base URL: {self.base_url}\n")
                f.write(f"Number of pages: {len(self.pages_data)}\n")
                f.write(f"Number of discovered URLs: {len(self.visited_urls)}\n")
                f.write(f"Crawling date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("-" * 70 + "\n")
                f.write("List of pages:\n")
                f.write("-" * 70 + "\n\n")
                
                for i, page in enumerate(self.pages_data, 1):
                    f.write(f"{i}. {page['title']}\n")
                    f.write(f"   URL: {page['url']}\n")
                    f.write(f"   Content length: {page['content_length']} characters\n")
                    f.write(f"   Number of headings: {len(page['headings'])}\n")
                    f.write(f"   Number of links: {page['links_count']}\n\n")
            
            print(f"Summary saved:\n   {filepath}")



def start_website_crawler(website_url):
    
    try:
        crawler = AdvancedWebsiteCrawler(
            website_url, 
            max_pages=50,
            headless=True
        )
        
        crawler.crawl()
        
        crawler.save_to_file('website_data.json')
        crawler.create_sitemap('sitemap.txt')
        crawler.create_summary('summary.txt')
        
        print(f"   📂 {crawler.output_folder}")
        
    except SystemExit:
        pass 
    except Exception as e:
        print(f"error: {e}")