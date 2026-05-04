# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias primero (para aprovechar caché de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Puerto que expone la app
EXPOSE 5000

# Variable de entorno para producción
ENV FLASK_ENV=production

# Comando para iniciar la app
CMD ["python", "app.py"]
