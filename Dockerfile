# Используем базовый образ с CUDA 11.2 и cuDNN для Ubuntu 20.04
FROM nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04

# Устанавливаем переменные окружения для автоматической установки
ENV DEBIAN_FRONTEND=noninteractive

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    gnupg \
    software-properties-common \
    && apt-get clean

# Добавляем репозиторий CUDA для Ubuntu 20.04
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub && \
    gpg --dearmor -o /usr/share/keyrings/nvidia-archive-keyring.gpg 3bf863cc.pub && \
    echo "deb [signed-by=/usr/share/keyrings/nvidia-archive-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /" \
    > /etc/apt/sources.list.d/cuda.list

# Устанавливаем cuDNN
RUN apt-get update && apt-get install -y \
    libcudnn8=8.1.1.*-1+cuda11.2 \
    libcudnn8-dev=8.1.1.*-1+cuda11.2

# Устанавливаем Python и другие зависимости
RUN apt-get install -y \
    python3.8 \
    python3-pip \
    libssl1.1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libtesseract-dev \
    libgl1-mesa-glx \
    && apt-get clean

# Установка Tesseract-OCR
RUN add-apt-repository -y ppa:alex-p/tesseract-ocr && \
    apt-get update && \
    apt-get install -y tesseract-ocr-rus

# Создание символических ссылок для cuDNN
RUN ln -s /usr/lib/x86_64-linux-gnu/libcudnn* /usr/local/cuda/lib64/

# Добавление переменных окружения для CUDA
ENV PATH=/usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Обновление pip
RUN pip install --upgrade pip

# Создание рабочей директории
WORKDIR /app

# Копирование приложения
COPY app /app

# Установка зависимостей Python из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Открытие порта для FastAPI сервера
EXPOSE 8000

# Команда для запуска FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]