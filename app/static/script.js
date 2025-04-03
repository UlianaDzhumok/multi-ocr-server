// Добавляем обработчики событий для drag and drop
const dropZone = document.getElementById("dropZone");
const imageInput = document.getElementById("imageInput");
const ocrEngineSelect = document.getElementById("ocrEngine");
const API_URL = window.API_URL || `${window.location.protocol}//${window.location.hostname}:${window.location.port}`;

// Fetch available OCR engines and populate the dropdown
async function fetchEngines() {
    try {
        const response = await fetch(`${API_URL}/GetOcrList?nocache=${Date.now()}`);
        if (response.ok) {
            const data = await response.json();
            ocrEngineSelect.innerHTML = data.available_engines.map(engine => 
                `<option value="${engine}">${engine}</option>`
            ).join("");
        } else {
            alert("Ошибка при получении списка движков OCR");
        }
    } catch (error) {
        console.error("Ошибка при загрузке движков OCR:", error);
    }
}

// Инициализация списка движков при загрузке страницы
fetchEngines();

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
        imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100%; height: auto;" />`;
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

// Отправка изображения на сервер как FormData
async function uploadImage() {
    const fileInput = document.getElementById("imageInput");
    const file = fileInput.files[0];  // Получаем файл из input

    // Проверяем, что файл выбран
    if (!file) {
        alert("Пожалуйста, выберите изображение.");
        return;
    }

    const selectedEngine = ocrEngineSelect.value;  // Получаем выбранный движок OCR

    if (!selectedEngine) {
        alert("Пожалуйста, выберите движок OCR.");
        return;
    }

    showSpinner(); // Показываем спиннер

    try {
        // Используем FormData для отправки файла
        const formData = new FormData();
        formData.append("file", file);
        formData.append("engine", selectedEngine);

        // Отправляем запрос с `nocache`, чтобы избежать кеширования
        const response = await fetch(`${API_URL}/GetOcr?nocache=${Date.now()}`, {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data); // Проверим данные

            const result = data.result;
            document.getElementById("outputText").innerHTML = `
                <div>
                    <h3 style="margin: 0; color: #333; font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 8px;">
                        Движок: ${result.engine} - Время выполнения: ${result.execution_time} сек
                    </h3>
                    <p>${result.text || `<b>Ошибка:</b> ${result.error}`}</p>
                </div>
            `;
        } else {
            alert("Ошибка при распознавании текста");
        }
    } catch (error) {
        console.error("Ошибка при отправке изображения:", error);
    } finally {
        hideSpinner();
    }
}