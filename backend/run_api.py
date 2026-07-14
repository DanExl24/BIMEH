import uvicorn
import os
import sys

from app.main import app  # Importación estática obligatoria para que PyInstaller compile el módulo 'app'

if __name__ == "__main__":
    # Si se ejecuta como ejecutable congelado (PyInstaller),
    # cambiamos el directorio de trabajo al directorio donde está el exe
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    
    # Iniciar FastAPI en puerto 8000 pasando el objeto de la aplicación directamente
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False, workers=1)
