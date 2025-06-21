import os
import shutil
import uuid
import torch
import whisperx
from fastapi import FastAPI, File, UploadFile, HTTPException
from contextlib import asynccontextmanager
import traceback
import gc

# --- Configuración Inicial Optimizada ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"
MODEL_NAME = "large-v2"

print("--- Configuración de la API de Transcripción ---")
print(f"Dispositivo de cómputo: {DEVICE}")
print(f"Tipo de cómputo: {COMPUTE_TYPE}")
print(f"Modelo de transcripción: {MODEL_NAME}")

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("ADVERTENCIA: La variable de entorno HF_TOKEN no está configurada. La diarización fallará.")

models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Cargando modelos de IA en memoria...")
    try:
        # 1. Modelo de Transcripción (Whisper)
        models['asr_model'] = whisperx.load_model(
            MODEL_NAME,
            DEVICE,
            compute_type=COMPUTE_TYPE,
            # Optimización para CPU: usa más hilos.
            # CORRECCIÓN: El parámetro es 'threads', no 'cpu_threads'.
            threads=16
        )

        # 2. Modelo de Diarización (Pyannote)
        models['diarize_model'] = whisperx.diarize.DiarizationPipeline(
            use_auth_token=HF_TOKEN,
            device=DEVICE
        )
        print("Modelos cargados exitosamente.")
    except Exception as e:
        print(f"Error fatal al cargar los modelos: {e}")
        raise e
    
    yield
    
    print("Liberando modelos de la memoria.")
    models.clear()
    gc.collect()

app = FastAPI(
    title="API de Transcripción con Diarización (WhisperX)",
    lifespan=lifespan
)

@app.post("/transcribir/")
async def transcribir_audio(audio_file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    temp_audio_path = f"/tmp/{task_id}_{audio_file.filename}"

    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        audio = whisperx.load_audio(temp_audio_path)

        asr_model = models['asr_model']
        result = asr_model.transcribe(audio, batch_size=4)
        language_code = result["language"]
        print(f"[{task_id}] Idioma detectado: {language_code}")
        
        print(f"[{task_id}] Alineando transcripción...")
        model_a, metadata = whisperx.load_align_model(language_code=language_code, device=DEVICE)
        aligned_result = whisperx.align(result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False)
        del model_a, metadata
        gc.collect()

        print(f"[{task_id}] Realizando diarización de hablantes (puede ser lento en CPU)...")
        diarize_model = models['diarize_model']
        diarize_segments = diarize_model(audio)

        print(f"[{task_id}] Asignando hablantes a las palabras...")
        result_with_speakers = whisperx.assign_word_speakers(diarize_segments, aligned_result)
        
        print(f"[{task_id}] Proceso completado.")
        return {"segments": result_with_speakers["segments"]}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en el proceso de transcripción: {str(e)}")
    
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        gc.collect()