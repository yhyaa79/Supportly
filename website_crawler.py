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
    """ساخت فولدر اصلی + فولدر اختصاصی سایت"""
    # --- فولدر اصلی ---
    main_folder = "advanced_website_crawler"
    os.makedirs(main_folder, exist_ok=True)
    
    # --- نام دامنه ---
    domain = urlparse(base_url).netloc
    folder_name = domain.replace('www.', '')
    folder_path = os.path.join(main_folder, folder_name)
    
    if os.path.exists(folder_path):
        print(f"اطلاعات این سایت قبلاً استخراج شده است!")
        print(f"مسیر: {folder_path}")
        print("هیچ عملیاتی انجام نشد.")
        return None
    
    os.makedirs(folder_path, exist_ok=True)
    print(f"فولدر جدید ساخته شد:")
    print(f"   {folder_path}")
    return folder_path


class AdvancedWebsiteCrawler:
    def __init__(self, base_url, max_pages=100, headless=True):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited_urls = set()
        self.pages_data = []
        self.domain = urlparse(base_url).netloc
        
        # ساخت فولدر خروجی
        self.output_folder = setup_output_folder(base_url)
        if not self.output_folder:
            raise SystemExit("خزیدن متوقف شد.")
        
        # تنظیمات Selenium
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
        """بررسی معتبر بودن URL"""
        if not url or url.startswith('#') or url.startswith('javascript:'):
            return False
            
        parsed = urlparse(url)
        return (parsed.netloc == self.domain and 
                parsed.scheme in ['http', 'https'] and
                not any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.mp4', '.css', '.js']))
    
    def scroll_page(self):
        """اسکرول صفحه برای بارگذاری محتوای lazy-load"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(3):  # 3 بار اسکرول
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            print(f"خطا در اسکرول: {e}")
    
    def extract_page_content(self, url):
        """استخراج محتوای یک صفحه با Selenium"""
        try:
            print(f"   → بارگذاری صفحه...")
            self.driver.get(url)
            
            # صبر برای بارگذاری کامل صفحه
            time.sleep(3)
            
            # اسکرول برای بارگذاری محتوای دینامیک
            self.scroll_page()
            
            # دریافت HTML کامل بعد از اجرای JavaScript
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # حذف تگ‌های غیرضروری
            for tag in soup(['script', 'style', 'noscript']):
                tag.decompose()
            
            # استخراج اطلاعات
            title = self.driver.title or ''
            
            # استخراج متا توضیحات
            meta_desc = ''
            try:
                meta_element = self.driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
                meta_desc = meta_element.get_attribute('content') or ''
            except:
                pass
            
            # استخراج تمام متن قابل مشاهده
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                text_content = body.text
                text_content = re.sub(r'\s+', ' ', text_content).strip()
            except:
                text_content = soup.get_text(separator=' ', strip=True)
            
            # استخراج هدینگ‌ها
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
            
            # استخراج لینک‌ها
            links = []
            try:
                link_elements = self.driver.find_elements(By.TAG_NAME, 'a')
                for link in link_elements:
                    try:
                        href = link.get_attribute('href')
                        if href:
                            absolute_url = urljoin(url, href)
                            # حذف fragment از URL
                            absolute_url = absolute_url.split('#')[0]
                            if self.is_valid_url(absolute_url):
                                links.append(absolute_url)
                    except:
                        continue
            except:
                pass
            
            # استخراج اطلاعات اضافی
            page_data = {
                'url': url,
                'title': title,
                'meta_description': meta_desc,
                'headings': headings,
                'content': text_content[:8000],  # محدود کردن محتوا
                'content_length': len(text_content),
                'links': list(set(links)),
                'links_count': len(set(links))
            }
            
            print(f"   ✓ عنوان: {title[:50]}...")
            print(f"   ✓ محتوا: {len(text_content)} کاراکتر")
            print(f"   ✓ لینک‌ها: {len(set(links))} عدد")
            
            return page_data
            
        except Exception as e:
            print(f"   ✗ خطا در استخراج {url}: {str(e)}")
            return None
    
    def crawl(self):
        """خزیدن روی وبسایت"""
        queue = deque([self.base_url])
        self.visited_urls.add(self.base_url)
        
        print("="*70)
        print(f"🚀 شروع خزیدن از: {self.base_url}")
        print(f"📊 حداکثر صفحات: {self.max_pages}")
        print("="*70 + "\n")
        
        try:
            while queue and len(self.pages_data) < self.max_pages:
                current_url = queue.popleft()
                print(f"\n📄 [{len(self.pages_data) + 1}/{self.max_pages}] {current_url}")
                
                page_data = self.extract_page_content(current_url)
                
                if page_data:
                    self.pages_data.append(page_data)
                    
                    # اضافه کردن لینک‌های جدید به صف
                    new_links = 0
                    for link in page_data['links']:
                        if link not in self.visited_urls and len(self.visited_urls) < self.max_pages * 2:
                            self.visited_urls.add(link)
                            queue.append(link)
                            new_links += 1
                    
                    print(f"   ✓ {new_links} لینک جدید به صف اضافه شد")
                
                time.sleep(2)  # تاخیر بین درخواست‌ها
            
            print("\n" + "="*70)
            print(f"✅ خزیدن تمام شد!")
            print(f"📊 تعداد صفحات استخراج شده: {len(self.pages_data)}")
            print(f"🔗 تعداد کل URL های کشف شده: {len(self.visited_urls)}")
            print("="*70 + "\n")
            
        finally:
            self.driver.quit()
        
        return self.pages_data
    
    def save_to_file(self, filename='website_data.json'):
        """ذخیره JSON در فولدر اختصاصی سایت"""
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
        print(f"ذخیره شد:\n {filepath}")
        
    
    def create_sitemap(self, filename='sitemap.txt'):
        """ایجاد نقشه سایت"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# نقشه سایت: {self.base_url}\n")
            f.write(f"# تاریخ: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# تعداد صفحات: {len(self.pages_data)}\n\n")
            
            for i, page in enumerate(self.pages_data, 1):
                f.write(f"{i}. {page['url']}\n")
                f.write(f"   عنوان: {page['title']}\n")
                f.write(f"   تعداد لینک: {page['links_count']}\n\n")
        
        print(f"🗺️  نقشه سایت در فایل {filename} ذخیره شد")
    
    def create_summary(self, filename='summary.txt'):
            filepath = os.path.join(self.output_folder, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write(f"گزارش خزیدن وبسایت\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"آدرس پایه: {self.base_url}\n")
                f.write(f"تعداد صفحات: {len(self.pages_data)}\n")
                f.write(f"تعداد URL های کشف شده: {len(self.visited_urls)}\n")
                f.write(f"تاریخ خزیدن: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("-" * 70 + "\n")
                f.write("فهرست صفحات:\n")
                f.write("-" * 70 + "\n\n")
                
                for i, page in enumerate(self.pages_data, 1):
                    f.write(f"{i}. {page['title']}\n")
                    f.write(f"   URL: {page['url']}\n")
                    f.write(f"   طول محتوا: {page['content_length']} کاراکتر\n")
                    f.write(f"   تعداد هدینگ: {len(page['headings'])}\n")
                    f.write(f"   تعداد لینک: {page['links_count']}\n\n")
            
            print(f"📝 خلاصه ذخیره شد:\n   {filepath}")



def start_website_crawler(website_url):
    
    print("\n" + "="*70)
    print("کرالر پیشرفته وبسایت با Selenium")
    print("ذخیره در فولدر اختصاصی + جلوگیری از تکرار")
    print("="*70 + "\n")
    
    try:
        crawler = AdvancedWebsiteCrawler(
            website_url, 
            max_pages=50,
            headless=True
        )
        
        # شروع خزیدن
        crawler.crawl()
        
        # ذخیره همه فایل‌ها در فولدر سایت
        crawler.save_to_file('website_data.json')
        crawler.create_sitemap('sitemap.txt')
        crawler.create_summary('summary.txt')
        
        print(f"\n🎉 همه چیز با موفقیت در فولدر زیر ذخیره شد:")
        print(f"   📂 {crawler.output_folder}")
        
    except SystemExit:
        pass  # اگر قبلاً بود، فقط پیام داده و خارج شده
    except Exception as e:
        print(f"خطای غیرمنتظره: {e}")