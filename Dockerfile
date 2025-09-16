# Usamos una imagen de Python. 3.10 es muy estable para estas librerías.
FROM python:3.10-slim

# Instalar dependencias del sistema como git, ffmpeg y la herramienta para el fix.
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    execstack \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar e instalar requerimientos.
# Esto tomará tiempo la primera vez.
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# --- FIX PARA EL ERROR DE CTRANSLATE2 ---
# Eliminamos la necesidad de un "executable stack" en las librerías compiladas.
RUN find /usr/local/lib/python3.10/site-packages/ctranslate2/ -name "*.so*" -exec execstack -c {} \;

# Copiar el código de la aplicación
COPY . /app

# Exponer el puerto
EXPOSE 8000

# Comando para iniciar la API con un timeout largo (1 hora)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "3600"]