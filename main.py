from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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
    
    if isinstance(result, dict) and 'answer' in result:
        return {"result": result['answer']}
    else:
        return {"result": str(result)}

@app.post("/str")
async def str_endpoint(input: TextInputStr):
    result = start_website_crawler(input.linkWeb)
    return {"result": str(result)}

@app.get("/")
def home():
    return {"message": "API آماده است!"}




