import json
import requests
from typing import List, Dict

from urllib.parse import urljoin, urlparse
import json


import os
from urllib.parse import urlparse


class WebsiteQASystem:
    def __init__(self, data_file: str, api_key: str, question: str = None):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-3.5-turbo"
        
        with open(data_file, 'r', encoding='utf-8') as f:
            self.website_data = json.load(f)
        
        print(f"Loaded {self.website_data['total_pages']} pages")
        
        # ذخیره سوال (اختیاری)
        self.last_question = question
        self.last_answer = None
        
        # اگر سوال داده شده بود، خودکار بپرس
        if question:
            self.last_answer = self.ask(question)

        
        print(f"✓ {self.website_data['total_pages']} صفحه بارگذاری شد")
    
    def create_context(self, query: str, max_pages: int = 5) -> str:
        """ایجاد کانتکست مرتبط با سوال کاربر"""
        # جستجوی صفحات مرتبط
        relevant_pages = []
        
        query_lower = query.lower()
        for page in self.website_data['pages']:
            # امتیازدهی به صفحات
            score = 0
            content_lower = (page['title'] + ' ' + 
                           page['meta_description'] + ' ' + 
                           page['content']).lower()
            
            # جستجوی کلمات کلیدی
            for word in query_lower.split():
                if len(word) > 2:
                    score += content_lower.count(word)
            
            if score > 0:
                relevant_pages.append((score, page))
        
        # مرتب‌سازی و انتخاب بهترین صفحات
        relevant_pages.sort(reverse=True, key=lambda x: x[0])
        top_pages = [page for _, page in relevant_pages[:max_pages]]
        
        # ساخت کانتکست
        context = f"اطلاعات وبسایت {self.website_data['base_url']}:\n\n"
        
        for i, page in enumerate(top_pages, 1):
            context += f"=== صفحه {i}: {page['title']} ===\n"
            context += f"URL: {page['url']}\n"
            if page['meta_description']:
                context += f"توضیحات: {page['meta_description']}\n"
            context += f"محتوا: {page['content'][:1000]}...\n\n"
        
        return context
    
    def ask(self, question: str) -> Dict:
        """پرسیدن سوال از سیستم"""
        # ایجاد کانتکست
        context = self.create_context(question)
        
        # ساخت پیام برای مدل
        messages = [
            {
                "role": "system",
                "content": f"""تو یک دستیار هوشمند هستی که به سوالات کاربران درباره یک وبسایت پاسخ می‌دهی.
اطلاعات زیر از وبسایت استخراج شده است. فقط بر اساس این اطلاعات پاسخ بده.
اگر جوابی در اطلاعات نبود، به کاربر بگو که این اطلاعات در دسترس نیست.
پاسخ‌هایت باید دقیق، مفید و به زبان فارسی باشد.

{context}"""
            },
            {
                "role": "user",
                "content": question
            }
        ]
        
        # ارسال درخواست به API
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(answer)
            return {
                "success": True,
                "answer": answer,
                "model": self.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    


# نحوه استفاده
def start_sebsite_QA(text, linkWeb):
    # کلید API خود را از openrouter.ai دریافت کنید
    API_KEY = "sk-or-v1-"

    # --- فولدر اصلی ---
    main_folder = "advanced_website_crawler"
    os.makedirs(main_folder, exist_ok=True)
    
    # --- نام دامنه ---
    # تغییر بده به:
    domain = urlparse(linkWeb).netloc       
    folder_name = domain.replace('www.', '')
    folder_path = os.path.join(main_folder, folder_name)
    

    # ایجاد سیستم پرسش و پاسخ
    result = WebsiteQASystem(
        data_file=f'{folder_path}/website_data.json',
        api_key=API_KEY,
        question= text
    )

    return result.last_answer
    
    # یا استفاده مستقیم:
    # result = qa_system.ask("قیمت گوشی‌های سامسونگ چقدر است؟")
    # print(result['answer'])