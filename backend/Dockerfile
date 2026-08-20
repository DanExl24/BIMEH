# Imagen base de Python
FROM python:3.13-slim

# Evita archivos .pyc y fuerza salida inmediata de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar primero las dependencias
COPY requirements.txt .

# Instalarlas
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Puerto donde escuchará FastAPI
EXPOSE 8000

# Ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]