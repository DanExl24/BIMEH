# Logica de la implementacion:

Objetivo

Construir un historial anual de cada integrante del personal utilizando los reportes diarios almacenados en los archivos JSON generados previamente.

Flujo general
Procesar todos los meses disponibles.
Leer los reportes diarios correspondientes a cada mes.
Identificar de forma única a cada integrante mediante su número de cédula.
Consolidar todos los registros encontrados en una única estructura histórica por persona.
Ordenar cronológicamente los registros obtenidos.
Detectar días sin reporte o inconsistencias en la información.
Generar una estructura que permita consultar fácilmente la evolución del personal a lo largo del tiempo.

Resultado esperado

El sistema dispondrá de una base histórica donde cada persona contará con la totalidad de sus registros diarios, facilitando el cálculo de estadísticas, tendencias y reportes históricos.

# Stack para el desarrollo:

- Python
- FastApi
- Vue
- Vite
- Tailwind
- Typescript
- Vue router
- Pinia (manejar estados)
- Apache Echarts

# Guia de ayuda:

Los datos provienen de archivos JSON ubicados en la carpeta listadoMeses.

Estructura de datos
listadoMeses/
ENERO.json
FEBRERO.json
...

Cada JSON tiene esta estructura:

{
"2026-01-01": {
"1": {
"APELLIDOS Y NOMBRES": "...",
"CEDULA": "...",
"SUBNOVEDAD": "...",
"DESCRIPCION": "...",
"DESDE": "...",
"HASTA": "..."
}
}
}
Procesamiento

Al iniciar la aplicación:

Leer todos los JSON.
Recorrer todos los meses.
Recorrer todos los días.
Recorrer todas las personas.
Agrupar la información usando la cédula como identificador único.

La estructura final en memoria debe ser algo similar a:

cedula
nombre
historial[]

Cada elemento del historial contiene

fecha
subnovedad
descripcion
desde
hasta
También generar

Un log indicando:

Mes

    Días faltantes

    Días duplicados

    Fechas inválidas

    Reportes vacíos

# Estadísticas y Reportes del Sistema por Módulo

El sistema cuenta con un motor analítico y visual distribuido en cuatro módulos principales y un completo sistema de exportaciones.

---

## 📊 1. Módulo: Dashboard General
Diseñado para responder de manera instantánea a la pregunta: *¿Cómo está el estado de fuerza de la unidad hoy?*

### Estadísticas y Métricas Clave (KPIs)
* **Personal Registrado**: Número total de integrantes activos en la base de datos para la fecha seleccionada.
* **Integrantes Disponibles**: Cantidad de personal listo para el servicio activo (asociados a las subnovedades `"CDO UNIDAD"` y `"AREA OPERACIONES"`).
* **En Novedades**: Cantidad de integrantes no disponibles por motivos de salud, permisos, comisiones o licencias.
* **Porcentaje de Disponibilidad**: Relación porcentual entre disponibles y el total de personal, destacada visualmente con un anillo de progreso dinámico.
* **Novedades Médicas**: Total de novedades clasificadas como razones médicas (ej. incapacidades, citas médicas, hospitalizaciones).
* **Novedades Administrativas**: Total de novedades por motivos administrativos (ej. comisiones de servicio, licencias, permisos).

### Visualizaciones Gráficas
* **Evolución de Disponibilidad (Línea)**: Gráfico de líneas temporales de ECharts que muestra la fluctuación de la disponibilidad diaria a lo largo del mes seleccionado, facilitando la detección de caídas críticas de personal.
* **Distribución de Novedades (Dona)**: Gráfico circular que representa la proporción en porcentaje de cada subnovedad respecto al total diario.
* **Resumen de Cambios respecto al día anterior (Novedades Diarias)**: Listado automático que detecta variaciones del estado de fuerza entre el día de ayer y hoy:
  * Entradas a novedades (ej. ingresa a vacaciones).
  * Retornos al servicio activo (ej. vuelve a disponible).
  * Cambios de tipo de novedad.

---

## 📅 2. Módulo: Cronología (Bitácora Diario)
Permite inspeccionar a detalle y navegar a lo largo del tiempo de forma histórica en el estado operacional de toda la unidad.

### Funcionalidades
* **Navegador Temporal**: Un calendario dinámico que muestra cuáles fechas cuentan con reportes cargados en la base de datos.
* **Novedades de la Fecha**: Visualización tipo lista e interactiva de todos los integrantes que tuvieron una novedad registrada para esa fecha específica.
* **Filtros Operacionales**: Caja de búsqueda inteligente por Nombre/Cédula y filtro rápido por tipo de Subnovedad.

---

## 📈 3. Módulo: Estadísticas Generales
Entrega un panel consolidado de rankings históricos y distribuciones acumuladas para la toma de decisiones.

### Estadísticas y Rankings
* **Ranking de Subnovedades más Frecuentes**: Gráfico de barras horizontales interactivo que ordena de mayor a menor las novedades más recurrentes en el rango temporal seleccionado.
* **Promedio de Duración de Novedades**: Muestra el promedio de días que el personal permanece inactivo por cada tipo de novedad.
* **Comparativas Mensuales**: Tabla comparativa con la sumatoria de días-novedad y tasa de disponibilidad agregada mes a mes.

---

## 👤 4. Módulo: Personal y Expediente Individual
Ficha técnica detallada que reúne toda la hoja de vida operacional e histórico de novedades de un integrante.

### Métricas Individuales
* **Tasa de Disponibilidad Histórica**: Porcentaje total del tiempo en que el integrante ha estado disponible para el servicio.
* **Días Totales Registrados**: Historial de registros del miembro.
* **Días Acumulados por Novedad**: Sumatoria exacta del tiempo en que el usuario ha estado de permiso, vacaciones o incapacidad.

### Visualizaciones y Utilidades
* **Gráfico de Torta RoseType (ECharts)**: Un gráfico circular tipo rosa de áreas que ilustra de manera prémium la distribución acumulada de sus novedades.
* **Línea de Tiempo**: Flujo cronológico vertical scrollable de todas las novedades y estados registrados por fecha.
* **Heatmap Mensual Individual**: Grid interactivo de 31 columnas que colorea cada día del mes (Verde = Disponible, Naranja = Novedad, Gris = Sin Registro) para identificar rápidamente patrones individuales.
* **Heatmap Anual Individual**: Matriz unificada de 12 meses por 31 días que da una visión global de disponibilidad a lo largo del año.
* **Reporte Tabular Histórico Paginado**: Tabla de datos integrada con buscador predictivo de descripciones y filtro rápido por subnovedad para auditar los registros detallados de inicio, fin y justificación de cada estado.

---

## 📥 5. Módulo de Descargas y Exportaciones
El backend implementa un potente servicio de exportación modularizado en `exportar.py` para formatos **Excel, CSV y PDF**:

1. **Reporte Diario Operacional (Módulo Cronología)**:
   * Genera la lista oficial de novedades de la fecha seleccionada con columnas de identificación, novedad, descripción, fecha inicial y fecha final.
2. **Heatmap de Disponibilidad Mensual (Módulo Personal / Dashboard)**:
   * Genera una matriz de asistencia donde las filas representan el personal y las columnas representan los 31 días del mes. Marca visualmente los estados de disponibilidad y novedad.
3. **Historial Individual Filtrado (Módulo Perfil)**:
   * Exporta todo el historial de novedades de un integrante. Admite filtros opcionales de **Mes** y **Subnovedad**, permitiendo al usuario descargar, por ejemplo, únicamente las "Vacaciones" del integrante correspondientes al mes de "JULIO" en PDF, Excel o CSV.

---

## 🗄️ Esquema de Base de Datos (PostgreSQL)

El sistema utiliza un esquema relacional normalizado:

### 1. Tabla: `PERSONAL`
Representa al personal de la unidad.
* `id` (SERIAL PRIMARY KEY)
* `cedula` (INTEGER UNIQUE)
* `nombre` (VARCHAR)
* `fecha_retiro` (DATE, NULL si está activo)

### 2. Tabla: `SUB_NOVEDADES`
Catálogo de novedades y estados operacionales.
* `id` (SERIAL PRIMARY KEY)
* `nombre` (VARCHAR UNIQUE)

### 3. Tabla: `REPORTES`
Bitácoras diarias cargadas al sistema.
* `id` (SERIAL PRIMARY KEY)
* `fecha` (DATE UNIQUE)
* `archivo` (VARCHAR)

### 4. Tabla: `REGISTRO_PERSONAL`
La tabla pivote que consolida el estado de un integrante en un reporte específico.
* `id` (SERIAL PRIMARY KEY)
* `id_reporte` (INTEGER REFERENCES `REPORTES(id)`)
* `id_personal` (INTEGER REFERENCES `PERSONAL(id)`)
* `id_sub_novedad` (INTEGER REFERENCES `SUB_NOVEDADES(id)`)
* `descripcion` (TEXT)
* `fecha_inicio` (DATE)
* `fecha_final` (DATE)

---

## 🛠️ Stack Tecnológico de Desarrollo

El sistema está desarrollado con tecnologías modernas que garantizan escalabilidad, rendimiento y un diseño visual prémium:

### Backend
* **Python**: Lenguaje de programación principal.
* **FastAPI**: Framework web de alto rendimiento para exponer la API REST de forma asíncrona y autocompilada.
* **SQLAlchemy / Psycopg2**: ORM y driver nativo para operaciones con la base de datos.
* **ReportLab**: Motor de renderizado vectorial de documentos PDF para la generación de reportes oficiales de alta calidad.
* **OpenPyXL**: Manipulación y creación de hojas de cálculo de Excel (`.xlsx`).

### Frontend
* **Vue 3 (SFC - Single File Components)**: Framework reactivo utilizando la *Composition API* y `<script setup lang="ts">`.
* **TypeScript**: Tipado estático y robusto en todo el frontend.
* **Vite**: Herramienta de compilación rápida para desarrollo.
* **Tailwind CSS v4.0**: Framework CSS de utilidades para un diseño responsivo de alto impacto visual (modo oscuro profundo, tarjetas de tipo neumórfico y bordes degradados).
* **Pinia**: Gestor de estado global y reactivo.
* **Vue Router**: Sistema de navegación dinámica y SPA.
* **ECharts (Apache)**: Biblioteca para la visualización interactiva de gráficos estadísticos complejos en tiempo real.

### Base de Datos
* **PostgreSQL**: Motor de base de datos relacional para almacenamiento y consultas agregadas optimizadas.

