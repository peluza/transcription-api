# API de Transcripción con WhisperX y Diarización

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![Docker](https://img.shields.io/badge/Docker-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-green.svg)

Una API de alto rendimiento para la transcripción de audio a texto con identificación de hablantes (diarización). El proyecto utiliza **WhisperX** para una transcripción precisa y una alineación de tiempo, y está completamente empaquetado con **Docker** y **Docker Compose** para un despliegue sencillo en cualquier entorno.

## ✨ Características Principales

* **Transcripción de Alta Precisión**: Utiliza el modelo `large-v2` de Whisper a través de `whisperx` para obtener transcripciones de máxima calidad.
* **Diarización de Hablantes**: Identifica y etiqueta quién habló y cuándo, gracias a la integración con `pyannote.audio`.
* **Optimizado para CPU y GPU**: Detecta automáticamente si hay una GPU con CUDA disponible para acelerar el proceso. En CPU, se optimiza para usar múltiples hilos.
* **Fácil de Desplegar**: Gracias a Docker, la configuración es mínima. Solo necesitas un comando para tener la API funcionando.
* **API Robusta**: Construida con FastAPI, ofrece una interfaz moderna, rápida y con documentación automática.
* **Manejo Eficiente de Memoria**: Los modelos se cargan una sola vez al iniciar la aplicación y se gestiona la memoria para un rendimiento estable.

## 🛠️ Stack Tecnológico

* **Backend**: Python, FastAPI
* **Transcripción**: WhisperX
* **Diarización**: Pyannote.audio
* **Contenerización**: Docker, Docker Compose
* **Inferencia de IA**: PyTorch, CTranslate2

## 🚀 Cómo Empezar

Sigue estos pasos para poner en marcha la API en tu máquina local.

### Prerrequisitos

* [Docker](https://www.docker.com/get-started) y [Docker Compose](https://docs.docker.com/compose/install/) instalados.
* [Git](https://git-scm.com/) para clonar el repositorio.
* **Un token de acceso de Hugging Face**: La diarización lo requiere para descargar el modelo de `pyannote`.
    1.  Crea una cuenta en [Hugging Face](https://huggingface.co/).
    2.  Ve a tu perfil -> **Settings** -> **Access Tokens**.
    3.  Crea un nuevo token con rol de `read`.
    4.  Copia el token.

### Instalación y Ejecución

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/transcription-api.git](https://github.com/tu-usuario/transcription-api.git)
    cd transcription-api
    ```

2.  **Configura tu token de Hugging Face:**
    Abre el archivo `docker-compose.yml` y reemplaza el valor `token_de_hugging_face` con tu token real.
    ```yaml
    services:
      transcription-api:
        build: .
        ports:
          - "8002:8000"
        restart: unless-stopped
        environment:
          # Pega aquí el token que copiaste de Hugging Face
          - HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx # <-- PÉGALO AQUÍ
    ```

3.  **Construye e inicia el contenedor:**
    Este comando construirá la imagen de Docker (puede tardar varios minutos la primera vez) e iniciará la API.
    ```bash
    docker-compose up --build
    ```
    Si quieres que se ejecute en segundo plano, añade el flag `-d`:
    ```bash
    docker-compose up --build -d
    ```

¡Listo! La API estará disponible en `http://localhost:8002`.

## 🎤 Cómo Usar la API

Envía una petición `POST` al endpoint `/transcribir/` con tu archivo de audio.

### Endpoint: `POST /transcribir/`

* **Descripción**: Recibe un archivo de audio y devuelve la transcripción con los segmentos y hablantes identificados.
* **Cuerpo de la Petición**: `multipart/form-data` con un campo `audio_file`.

### Ejemplo con `curl`

Abre tu terminal y ejecuta el siguiente comando, reemplazando `/ruta/a/tu/audio.mp3` con la ruta real de tu archivo de audio.

```bash
curl -X 'POST' \
  'http://localhost:8002/transcribir/' \
  -F 'audio_file=@/ruta/a/tu/audio.mp3'
```

### Ejemplo de Respuesta Exitosa (JSON)

Recibirás un objeto JSON con una clave `segments` que contiene una lista de los fragmentos de texto detectados. Cada segmento incluye el texto, el tiempo de inicio y fin, y el hablante identificado.

```json
{
  "segments": [
    {
      "start": 0.53,
      "end": 2.77,
      "text": " Hola, este es un audio de prueba.",
      "speaker": "SPEAKER_01"
    },
    {
      "start": 3.12,
      "end": 5.45,
      "text": " Y esta es una segunda intervención para verificar la diarización.",
      "speaker": "SPEAKER_00"
    }
  ]
}
```

## ⚙️ Configuración Avanzada

### Uso de GPU (NVIDIA)

Si tu máquina tiene una GPU NVIDIA compatible con CUDA y los drivers instalados, puedes acelerar enormemente el proceso.

1.  Asegúrate de tener instalado el [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
2.  En el archivo `docker-compose.yml`, descomenta la sección `deploy`:

    ```yaml
    # --- SECCIÓN OPCIONAL PARA GPU NVIDIA ---
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    ```
3.  Reinicia el contenedor: `docker-compose up --build -d`.

La aplicación detectará la GPU automáticamente y usará `float16` para un rendimiento óptimo.

### Estructura de Archivos

```
.
├── docker-compose.yml  # Orquesta el despliegue del contenedor.
├── Dockerfile          # Define la imagen de Docker para la aplicación.
├── main.py             # Lógica de la API con FastAPI y WhisperX.
└── requirements.txt    # Dependencias de Python.
```

## 📄 Licencia

Este proyecto está distribuido bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para ver los términos completos.