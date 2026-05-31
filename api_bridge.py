from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
import io
from PIL import Image
import numpy as np
import base64
import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

print("=== ПРОВЕРКА ОКРУЖЕНИЯ ===")
print("Текущая директория:", os.getcwd())
print("КЛЮЧ ANTHROPIC В OS:", "ДОСТУПЕН" if os.environ.get("ANTHROPIC_API_KEY") else "ОТСУТСТВУЕТ")
print("==========================")

# Импортируем существующую логику
from modules import photo_engineer, techcard, colorimetry

app = FastAPI(title="Digital Mentor API Bridge", version="1.0.0")

@app.post("/calibrate")
async def calibrate_white_balance(image: UploadFile = File(...)):
    """
    Калибровка баланса белого по серой карте
    """
    try:
        # Читаем изображение
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Вызываем существующую логику из photo_engineer
        # Предполагаем, что там есть функция для калибровки
        result = photo_engineer.calibrate_white_balance(img)
        
        return JSONResponse(content={
            "success": True,
            "result": result
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@app.post("/analyze-point")
async def analyze_color_point(
    image: UploadFile = File(...),
    x: int = Form(...),
    y: int = Form(...)
):
    """
    Анализ цвета в точке с координатами (x, y)
    """
    try:
        # Читаем изображение
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")

        # Вызываем существующую логику из techcard
        # Предполагаем, что там есть функция для анализа точки
        result = techcard.analyze_color_point(img, x, y)

        return JSONResponse(content={
            "success": True,
            "result": {
                "x": x,
                "y": y,
                "color": result
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@app.post("/analyze-work")
async def analyze_work(
    image: UploadFile = File(...),
    vita_shade: str = Form(...),
    work_stage: str = Form(...),
    analysis_type: str = Form(...),
    comment: str = Form(default=""),
    teeth: str = Form(default="")
):
    """
    Анализ работы с помощью Claude AI
    """
    try:
        # Читаем изображение
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        img_array = np.array(img)

        # Формируем заметки с информацией о зубах
        teeth_info = f"Работа техники: зубы {teeth}. " if teeth else ""
        full_notes = teeth_info + comment

        # Получаем API ключ из переменной окружения
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        # Вызываем существующую логику из colorimetry
        result = colorimetry.analyze_with_claude(
            img_array, vita_shade, full_notes, work_stage, analysis_type, api_key
        )

        return JSONResponse(content={
            "success": True,
            "result": result
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@app.get("/")
async def root():
    return {"message": "Digital Mentor API Bridge is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
