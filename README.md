# OCR сервер с FastAPI (CPU и GPU)

Этот проект предоставляет API для распознавания текста с изображений с использованием различных OCR-движков: **EasyOCR**, **Tesseract**, **PaddleOCR**, **SuryaOCR**. Вы можете выбрать нужный движок через веб-интерфейс или API.

![Иллюстрация к проекту](https://github.com/UlianaDzhumok/triple-ocr-server/blob/main/example.jpg)

## Структура проекта

  ```csharp
  triple-ocr-server/
  ├── app/
  │   ├── templates/
  │   │   └── index.html      # Шаблон страницы для загрузки изображения
  │   ├── static/
  │   │   └── style.css       # Стиль для страницы
  │   ├── main.py             # Основной код сервера FastAPI
  │   ├── requirements.txt    # Список зависимостей
  ├── Dockerfile              # Dockerfile для создания Docker образа
  ├── environment.yml         # Список зависимостей в виде готового окружения Anaconda
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

Если Вы используете Anaconda можно восстановить окружение из файла:


```bash
conda env create -f environment.yml
```
или
```bash
conda create --name <имя_окружения> --file environment.yml
```
Эта команда создаст новое окружение с теми же зависимостями, что были в сохраненном файле.

## Запуск локально через Uvicorn
Если вы хотите запустить сервер локально, выполните следующие шаги:

1. Убедитесь, что у вас установлен Uvicorn:
```bash
pip install uvicorn
```
2. Запустите сервер:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
Сервер будет доступен по адресу http://0.0.0.0:8000.

3. Откройте в браузере страницу для загрузки изображения и выбора движка OCR:

```arduino
http://0.0.0.0:8000
```
## Запуск через Docker
### Создание Docker образа
1. Сначала создайте Docker образ выполнив команду из директории где находится Dockerfile:
```bash
docker build -t ocr-server .
```
2. Запустите контейнер (с использованием GPU с указанием HOST и PORT для развертки):
```bash
docker run --gpus all -e USE_GPU=true -e HOST=127.0.0.1 -e PORT=9000 ocr-server
```
Теперь сервер будет доступен по адресу http://127.0.0.1:9000.

### Запуск из уже готового Docker образа
Если у вас уже есть готовый Docker образ (например из пакетов этого проекта: [triple-ocr-server](https://github.com/UlianaDzhumok?tab=packages&repo_name=triple-ocr-server)), вы можете просто запустить его с использованием GPU:
```bash
docker run --gpus all -e USE_GPU=true triple-ocr-server
```
Или только для CPU:
```bash
docker run -e USE_GPU=false triple-ocr-server
```
## Пример работы с API
### Запрос на распознавание текста
С помощью метода POST вы можете отправить изображение и выбрать OCR-движок для обработки. 
Поддерживаемые движки: easyocr, tesseract, paddleocr.

Пример запроса через curl:
```bash
curl -X POST http://localhost:8000/GetOcr \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
-d '{
    "file": "<изображение в base64>",
    "engine": "easyocr"
}'
```
Ответ будет в формате JSON:

```json
{
  "result": {
    "engine": "easyocr",
    "execution_time": "59.95",
    "text": "Распознанный текст с изображением с использованием EasyOCR"
  }
}
```

### Получение списка доступных движков
С помощью метода GET вы можете получить список доступных OCR-движков.

Пример запроса через curl:
```bash
curl -X GET http://localhost:8000/GetOcrList
```
Ответ будет в формате JSON:

```json
{
  "available_engines": ["easyocr", "tesseract", "paddleocr", "suryaocr"]
}
```

### Тестирование API с использованием `test_API.py`
Вы можете протестировать API, используя скрипт `test_API.py`. 

#### Настройка:
1. Убедитесь, что файл `test_image.jpg` находится в той же папке, что и `test_API.py`.
2. Убедитесь, что сервер API запущен локально на `http://0.0.0.0:8000`.

#### Запуск теста:
```bash
python test_API.py
```

Скрипт выполняет следующие действия:
1. Отправляет запрос к `/GetOcrList` для получения списка доступных движков OCR.
2. Тестирует каждый движок (`easyocr`, `tesseract`, `paddleocr`) с изображением `test_image.jpg`.

Пример вывода:
```
Available OCR Engines: ['easyocr', 'tesseract', 'paddleocr']

Testing OCR with easyocr engine:
Engine: easyocr
Execution Time: 59.95 seconds
Recognized Text:
Распознанный текст с изображением с использованием EasyOCR

Testing OCR with tesseract engine:
Engine: tesseract
Execution Time: 3.16 seconds
Recognized Text:
Распознанный текст с изображением с использованием Tesseract

Testing OCR with paddleocr engine:
Engine: paddleocr
Execution Time: 1.00 seconds
Recognized Text:
Распознанный текст с изображением с использованием PaddleOCR
```

### Примечание
Убедитесь, что файл изображения правильно закодирован в Base64 перед отправкой в API.

### Доступ к веб-интерфейсу
Кроме того, для удобства предоставляется веб-интерфейс для загрузки изображений и выбора OCR-движка. Перейдите по следующему адресу в браузере:

```arduino
http://0.0.0.0:8000
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
