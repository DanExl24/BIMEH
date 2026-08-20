import uvicorn
import os
import sys

from app.main import app  # Importación estática obligatoria para que PyInstaller compile el módulo 'app'

if __name__ == "__main__":
    # Si se ejecuta como ejecutable congelado (PyInstaller),
    # cambiamos el directorio de trabajo al directorio donde está el exe
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    
    # Iniciar FastAPI en puerto 3000 escuchando en todas las interfaces de red (0.0.0.0)
    uvicorn.run(app, host="0.0.0.0", port=3000, reload=False, workers=1)

