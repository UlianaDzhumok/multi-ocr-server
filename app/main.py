from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import easyocr
import pytesseract
from paddleocr import PaddleOCR
from typing import List
from PIL import Image
import numpy as np
import time
import cv2
import torch
import os
import asyncio
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

app = FastAPI()

# Ограничение на параллельные запросы (максимум 5 одновременно)
ocr_semaphore = asyncio.Semaphore(5)

# Монтируем статические файлы (если используются)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Разрешаем CORS (если запросы идут с другого домена)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы со всех источников
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Использовать ли GPU
USE_GPU = os.getenv("USE_GPU", "false").lower() == "true"
CUDA_AVAILABLE = torch.cuda.is_available()
USE_GPU_FINAL = USE_GPU and CUDA_AVAILABLE

# Функция загрузки изображения без обработки
def load_image_from_upload(file: UploadFile):
    """Читает изображение из загруженного файла без изменений."""
    try:
        image_data = file.file.read()
        image_np = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)  # Читаем в формате BGR
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка загрузки изображения: {str(e)}")

@app.get("/")
async def root():
   return RedirectResponse(url="/index.html")

@app.get("/index.html", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/GetOcr")
async def get_ocr(file: UploadFile = File(...), engine: str = Form(...)):
    async with ocr_semaphore:  # Ограничиваем количество параллельных запросов
        try:
            image = load_image_from_upload(file)
        except HTTPException as e:
            return JSONResponse(status_code=400, content={"error": str(e.detail)})

        result = {}

        if engine == "easyocr":
            reader = easyocr.Reader(['ru'], gpu=USE_GPU_FINAL, detector='DB', recognizer='Transformer')
            start_time = time.time()
            ocr_result = reader.readtext(image)
            execution_time = time.time() - start_time
            result = {
                "engine": "easyocr",
                "execution_time": f"{execution_time:.2f}",
                "text": "\n".join([r[1] for r in ocr_result])
            }

        elif engine == "tesseract":
            start_time = time.time()
            ocr_result = pytesseract.image_to_string(image, lang='rus')
            execution_time = time.time() - start_time
            result = {
                "engine": "tesseract",
                "execution_time": f"{execution_time:.2f}",
                "text": ocr_result
            }

        elif engine == "paddleocr":
            ocr = PaddleOCR(use_angle_cls=True, lang='ru', gpu=USE_GPU_FINAL, drop_score=0.3)
            start_time = time.time()
            ocr_result = ocr.ocr(image)
            execution_time = time.time() - start_time
            text_blocks = [(item[1][0], item[1][1]) for sublist in ocr_result for item in sublist]
            chunks = [block for block in text_blocks if len(block) > 0]
            result = {
                "engine": "paddleocr",
                "execution_time": f"{execution_time:.2f}",
                "text": "\n".join(chunk[0] for chunk in chunks)
            }

        elif engine == "suryaocr":
            langs = ["ru"]
            recognition_predictor = RecognitionPredictor()
            detection_predictor = DetectionPredictor()
            image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            start_time = time.time()
            predictions = recognition_predictor([image_pil], [langs], detection_predictor)
            execution_time = time.time() - start_time
            text_blocks = [text_line.text for text_line in predictions[0].text_lines]
            result = {
                "engine": "suryaocr",
                "execution_time": f"{execution_time:.2f}",
                "text": "\n".join(text_blocks)
            }

        else:
            raise HTTPException(status_code=400, detail=f"Неподдерживаемый движок OCR: {engine}")

        response = JSONResponse(content={"result": result})
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

@app.get("/GetOcrList")
async def get_ocr_list():
    engines = ["easyocr", "tesseract", "paddleocr", "suryaocr"]
    return {"available_engines": engines}

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000)) 
    host = os.getenv("HOST", "0.0.0.0")

    print(f"Starting server on {host}:{port}") 

    import uvicorn
    uvicorn.run("main:app", host=host, port=port)