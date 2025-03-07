# Usa la imagen oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /requestocs

# Copia los archivos del proyecto dentro del contenedor
COPY . /requestocs

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto donde se ejecutará la aplicación
EXPOSE 80

# Comando para iniciar el servidor Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
