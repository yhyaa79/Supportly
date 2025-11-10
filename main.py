from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ← اینو اضافه کن
from pydantic import BaseModel
from website_crawler import start_website_crawler
from website_QA import start_sebsite_QA

""" server
cd /Users/yayhaeslami/Python/my_workspace/resume/my_project/support_web
uvicorn main:app --host 0.0.0.0 --port 8000

"""

""" local
cd /Users/yayhaeslami/Python/my_workspace/resume/my_project/support_web
uvicorn main:app --reload
"""
app = FastAPI()

# ==== CORS: اجازه بده مرورگر از هرجا بفرسته ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # تو تولید بذار ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ============================================

class TextInputRun(BaseModel):
    text: str
    linkWeb: str
    model: str

class TextInputStr(BaseModel):
    linkWeb: str

@app.post("/run")
async def run_function(input: TextInputRun):
    result = start_sebsite_QA(input.text, input.linkWeb, input.model)
    
    # فقط مقدار answer رو برگردون
    if isinstance(result, dict) and 'answer' in result:
        return {"result": result['answer']}
    else:
        return {"result": str(result)}

# یک بار کال میشود رد ذمان باذ شرن
@app.post("/str")
async def str_endpoint(input: TextInputStr):
    result = start_website_crawler(input.linkWeb)
    return {"result": str(result)}

@app.get("/")
def home():
    return {"message": "API آماده است!"}



def my_python_function(text: str, linkWeb: str) -> str:
    return f"سلام از {linkWeb}! پیام شما: {text.upper()} بود."





