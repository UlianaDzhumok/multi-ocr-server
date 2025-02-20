FROM pytorch/pytorch:2.5.1-cuda11.8-cudnn9-devel

# Установим переменную окружения для автоматической установки
ENV DEBIAN_FRONTEND=noninteractive

# Установка Python и pip
RUN apt-get update && apt-get install -y \
    python3.10 python3-pip git libssl3 libglib2.0-0 libsm6 libxext6 libxrender-dev libtesseract-dev \
    libgl1-mesa-glx \
    && apt-get clean

# Установка Tesseract-OCR
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev
RUN apt-get update && apt-get install -y tesseract-ocr-rus

# Создание рабочей директории
WORKDIR /app

# Копирование приложения
COPY app /app

# Обновление pip
RUN python3 -m pip install --upgrade pip

# Установка EasyOCR, FastAPI и Uvicorn
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменную окружения LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda-11.2/targets/x86_64-linux/lib:$LD_LIBRARY_PATH

ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn main:app --host ${HOST} --port ${PORT}"]
