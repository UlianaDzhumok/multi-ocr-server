// Добавляем обработчики событий для drag and drop
const dropZone = document.getElementById("dropZone");
const imageInput = document.getElementById("imageInput");

dropZone.addEventListener("dragover", function(event) {
    event.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", function(event) {
    event.preventDefault();
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", function(event) {
    event.preventDefault();
    dropZone.classList.remove("dragover");
    
    const file = event.dataTransfer.files[0];
    imageInput.files = event.dataTransfer.files;
    previewImage(file);
    document.getElementById("recognizeButton").disabled = false;
});

imageInput.addEventListener("change", function() {
    const file = this.files[0];
    previewImage(file);
    document.getElementById("recognizeButton").disabled = false;
});

function previewImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const imagePreview = document.getElementById("imagePreview");
        imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview" />`;
    };
    reader.readAsDataURL(file);
}

// Показывает спиннер
function showSpinner() {
    document.getElementById('spinner').classList.remove('hidden');
}

// Скрывает спиннер
function hideSpinner() {
    document.getElementById('spinner').classList.add('hidden');
}

// Отправка изображения на сервер
async function uploadImage() {
    const fileInput = document.getElementById("imageInput");
    const file = fileInput.files[0];  // Получаем файл из input

    // Проверяем, что файл выбран
    if (!file) {
        alert("Пожалуйста, выберите изображение.");
        return;
    }

    const engines = [];
    if (document.getElementById("easyocr").checked) engines.push("easyocr");
    if (document.getElementById("tesseract").checked) engines.push("tesseract");
    if (document.getElementById("paddleocr").checked) engines.push("paddleocr");

    // Преобразуем файл в строку Base64
    const reader = new FileReader();
    reader.onloadend = async function() {
        const base64Image = reader.result.split(',')[1];  // Получаем только Base64 часть
        const requestData = {
            request: {
                file: base64Image,
                engines: engines
            }
        };

        showSpinner(); // Показываем спиннер

        // Отправка данных на сервер
        const response = await fetch("http://localhost:8000/ocr", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                file: base64Image,
                engines: engines
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data); // Проверим данные
        
            document.getElementById("outputText").innerHTML = data.results.map(result => {
                console.log(result.execution_time); // Проверим значение execution_time
                return `
                    <div>
                        <h3 style="margin: 0; color: #333; font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
                            Движок: ${result.engine} -  Время выполнения: ${result.execution_time} сек
                        </h3>
                        <p>${result.text || `<b>Ошибка:</b> ${result.error}`}</p>
                    </div>
                `;
            }).join("");
        } else {
            alert("Ошибка при распознавании текста");
        }
        hideSpinner();
    };

    reader.readAsDataURL(file);  // Чтение файла как Base64
}