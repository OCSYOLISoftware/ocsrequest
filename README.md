# Crear entorno virtual 
python3 -m venv env 
# Activar entorno
source env/bin/activate
# Instalar dependencias 
pip install fastapi jinja2 python-multipart uvicorn werkzeug uvicorn
# Puedes utilizar requirements.txt
pip install -r requirements.txt

# Ejecutar proyecto
uvicorn main:app --reload
