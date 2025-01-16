from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import easyocr
import pytesseract
from paddleocr import PaddleOCR
from pydantic import BaseModel
from typing import List
from PIL import Image
import base64
import numpy as np
import time

app = FastAPI()

class OCRRequest(BaseModel):
    file: str  # Строка Base64
    engines: list

# Здесь 'directory' должен указывать на папку, где находятся static файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Разрешаем запросы CORS от любого источника
origins = ["*"]  # Для простоты можно разрешить доступ со всех источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
   return RedirectResponse(url="/index.html")

@app.get("/index.html", response_class=HTMLResponse)
async def index_page(request: Request):
    # Просто рендерим страницу без параметров engines
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ocr")  # Убедитесь, что здесь используется POST
async def ocr(request: OCRRequest):
    try:
        image_data = base64.b64decode(request.file)
        image = Image.open(BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при декодировании изображения: {str(e)}")
    
    results = []
    
    # Работа с выбранными OCR движками
    if "easyocr" in request.engines:
        reader = easyocr.Reader(['ru'], gpu=False)
        start_time = time.time()
        result = reader.readtext(np.array(image))
        execution_time = time.time() - start_time
        results.append({"engine": "easyocr", "execution_time": f"{execution_time:.2f}", "text": " ".join([r[1] for r in result])})
    
    if "tesseract" in request.engines:
        start_time = time.time()
        result =  pytesseract.image_to_string(image, lang='rus')
        execution_time = time.time() - start_time
        results.append({"engine": "tesseract", "execution_time": f"{execution_time:.2f}", "text": result.replace("\n", "  ")})
    
    if "paddleocr" in request.engines:
        ocr = PaddleOCR(use_angle_cls=True, lang='ru', gpu=False)
        start_time = time.time()
        result = ocr.ocr(np.array(image))
        execution_time = time.time() - start_time
        text_blocks = [(item[1][0], item[1][1]) for sublist in result for item in sublist]
        chunks=[block for block in text_blocks if len(block) > 0]
        results.append({"engine": "paddleocr", "execution_time": f"{execution_time:.2f}", "text": " ".join(chunk[0] for chunk in chunks)})
    
        print(results)
    
    return {"results": results}
    
if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get('PORT', 8000)))
