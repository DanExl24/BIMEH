# BIMEH — Sistema de Gestión Operacional y Mapa de Calor del Personal

Este sistema automatiza la búsqueda, consolidación y visualización del historial de novedades y disponibilidad operacional del personal, eliminando los procesos de búsqueda y consolidación manual.

---

## 🏗️ Arquitectura del Proyecto

El sistema está construido bajo una arquitectura desacoplada y moderna que separa el backend y el frontend:

### 1. Backend (Python + FastAPI + PostgreSQL)
El núcleo de la API se encuentra estructurado de forma modular bajo el directorio `backend/`:

* **`backend/app/main.py`**: Punto de entrada de la aplicación FastAPI. Carga los middleware de CORS y monta los enrutadores.
* **`backend/app/database.py`**: Módulo de conexión y adaptador para la base de datos PostgreSQL.
* **`backend/app/dependencies.py`**: Dependencias inyectables compartidas (como `get_db` para la sesión de base de datos).
* **`backend/app/models.py`**: Definiciones de modelos y tipos auxiliares de Python.
* **`backend/app/routers/`**: Enrutadores independientes para organizar las operaciones de la API:
  * [`dashboard.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/dashboard.py): KPIs iniciales y métricas del panel principal.
  * [`personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py): Búsqueda, listado, detalles, autocompletado e historial del personal.
  * [`stats.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/stats.py): Estadísticas consolidadas y acumulados.
  * [`alertas.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/alertas.py): Notificaciones del estado operacional.
  * [`exportar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/exportar.py): Generación de reportes (Excel, CSV y PDF).

### 2. Frontend (Vue 3 + Vite + Tailwind CSS + Pinia)
El cliente web está localizado en el directorio `frontend/` y sigue una estructura altamente tipada:

* **[`frontend/src/services/api.ts`](file:///c:/Users/alejo/Downloads/automPYdrive/frontend/src/services/api.ts)**: Cliente API centralizado que expone los endpoints tipados del backend.
* **[`frontend/src/types/index.ts`](file:///c:/Users/alejo/Downloads/automPYdrive/frontend/src/types/index.ts)**: Centralización de interfaces y tipos TypeScript compartidos en todo el proyecto.
* **[`frontend/src/stores/appStore.ts`](file:///c:/Users/alejo/Downloads/automPYdrive/frontend/src/stores/appStore.ts)**: Estado global Pinia para persistir selecciones como el mes activo del sistema y configuración de URLs base.
* **`frontend/src/views/`**: Páginas de la interfaz:
  * `DashboardView.vue`: Vista principal con KPIs, gráficos de ECharts y novedades actuales.
  * `CronologiaView.vue`: Bitácora y flujo operacional diario.
  * `ReportesView.vue`: Módulo para exportar el Reporte Diario Operacional.
  * `PersonalView.vue`: Buscador y catálogo de perfiles del personal.
  * `PersonalDetalleView.vue`: Expediente individual de cada integrante.

---

## 🔌 Configuración de Base de Datos (PostgreSQL)

El backend consume una base de datos PostgreSQL llamada `bimeh` con los siguientes parámetros por defecto:
* **Host**: `localhost`
* **Puerto**: `5432`
* **Usuario**: `postgres`
* **Contraseña**: `postgres`

Si requieres cambiar los accesos, los puedes configurar en el archivo [`config.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/config.py).

---

## 🚀 Instrucciones de Inicio Rápido (Local)

> [!IMPORTANT]
> Arranca ambos servicios de forma independiente desde terminales diferentes en tu entorno de desarrollo local.

### 1. Iniciar el Servidor Backend
Navega a la carpeta del backend, activa el entorno virtual de la raíz y ejecuta el servidor FastAPI:
```bash
cd backend
..\.venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
La API estará disponible en `http://127.0.0.1:8000`.

### 2. Iniciar el Servidor Frontend
Navega al directorio `frontend/` del proyecto e inicia el servidor de desarrollo de Vite:
```bash
cd frontend
npm install
npm run dev
```
La interfaz web se cargará por defecto en `http://localhost:5173`.
