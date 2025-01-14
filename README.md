# OCR сервер с FastAPI

Этот проект предоставляет API для распознавания текста с изображений с использованием различных OCR-движков: **EasyOCR**, **Tesseract**, **PaddleOCR**. 
Вы можете выбрать нужный движок через веб-интерфейс или API.
Пример использования графического интерфейса:

![Image alt](https://github.com/UlianaDzhumok/triple-ocr-server/raw/main/example.jpg)

## Структура проекта

  ```csharp
  triple-ocr-server/
  ├── app/
  │   ├── templates/
  │   │   └── index.html      # Шаблон страницы для загрузки изображения
  │   ├── static/
  │   │   └── style.css       # Стиль для страницы
  │   ├── main.py             # Основной код сервера FastAPI
  ├── Dockerfile              # Dockerfile для создания Docker образа
  ├── requirements.txt        # Список зависимостей
  └── README.md               # Этот файл
```
## Установка зависимостей

1. Клонируйте репозиторий:
```bash
git clone https://github.com/UlianaDzhumok/triple-ocr-server
cd triple-ocr-server
```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
В requirements.txt указаны все необходимые библиотеки для работы с сервером.

3. Tesseract-OCR необхожимо установить отдельно. Инструкции можно найти здесь: https://tesseract-ocr.github.io/tessdoc/Installation.html

## Запуск локально через Uvicorn
Если вы хотите запустить сервер локально, выполните следующие шаги:

1. Убедитесь, что у вас установлен Uvicorn:
```bash
pip install uvicorn
```
2. Запустите сервер из директории app:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
Сервер будет доступен по адресу http://127.0.0.1:8000.

3. Откройте в браузере страницу для загрузки изображения и выбора движка OCR:

```arduino
http://127.0.0.1:8000
```
## Запуск через Docker
### Создание Docker образа
1. Сначала создайте Docker образ выполнив команду из директории где находится Dockerfile:
```bash
docker build -t ocr-server-gpu .
```
2. Запустите контейнер:
```bash
docker run --gpus all -p 8000:8000 ocr-server-gpu
```
Теперь сервер будет доступен по адресу http://127.0.0.1:8000.

### Запуск из уже готового Docker образа
TO DO: Готовый образ будет находиться в разделе пакетов к этому проекту

## Пример работы с API
### Запрос на распознавание текста
С помощью метода POST вы можете отправить изображение и выбрать OCR-движок для обработки. Поддерживаемые движки: easyocr, tesseract, paddleocr.

Пример запроса через curl:
```bash
curl -X POST http://localhost:8000/ocr \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-H "Origin: http://localhost:8000" \
-d '{
    "file": изображение в base64,
    "engines": ["easyocr", "tesseract", "paddleocr"],
    "use_gpu": true
}'
```
Ответ будет в формате JSON:

```json
{
  "results": [
    {
      "engine": "easyocr",
      "text": "Распознанный текст с изображением с использованием EasyOCR на GPU"
    },
    {
      "engine": "tesseract",
      "text": "Распознанный текст с изображением с использованием Tesseract"
    },
    {
      "engine": "paddleocr",
      "text": "Распознанный текст с изображением с использованием PaddleOCR на GPU"
    }
  ]
}
```
### Доступ к веб-интерфейсу
Кроме того, для удобства предоставляется веб-интерфейс для загрузки изображений и выбора OCR-движка. Перейдите по следующему адресу в браузере:

```arduino
http://127.0.0.1:8000
```
Вы можете выбрать движок OCR, загрузить изображение и получить результат распознавания текста.

## Список зависимостей
Проект использует следующие библиотеки:

- FastAPI — для создания веб-сервера и API.
- Uvicorn — ASGI сервер для FastAPI.
- EasyOCR — движок OCR для распознавания текста.
- Tesseract — классический движок OCR.
- PaddleOCR — ещё один мощный движок OCR.
- OpenCV — для обработки изображений.
- Pytesseract — Python интерфейс для Tesseract.

## Примечания
- Поддержка GPU возможна только для некоторых движков (например, EasyOCR и PaddleOCR). В случае с Tesseract GPU не поддерживается.
- Для успешной работы с PaddleOCR необходимо установить специальную версию библиотеки, поддерживающую CUDA.
