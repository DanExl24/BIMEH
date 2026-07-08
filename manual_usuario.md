# MANUAL DE USUARIO

## BIMEH: Sistema de Control Operacional y Disponibilidad de Personal

---

## 1. Portada

- **Nombre del sistema**: BIMEH (Gestión y Mapa de Calor del Personal)
- **Versión**: 2.1
- **Autor**: Equipo de Desarrollo BIMEH (Pair Programming con Antigravity)
- **Fecha**: Julio de 2026

---

## 2. Introducción

### Objetivo del sistema

BIMEH es una aplicación web diseñada para centralizar, analizar y consultar de forma automatizada el estado operacional y el historial de novedades de la unidad. Facilita la toma de decisiones al responder de forma instantánea a la pregunta: _¿Con qué personal disponible contamos hoy?_

### A quién va dirigido

Este sistema está dirigido a comandantes de unidad, secretarios de personal, directores de instrucción y administradores de talento humano encargados de supervisar el estado de fuerza diario de la unidad.

### Alcance

- Monitoreo diario en tiempo real de la disponibilidad de la unidad.
- Registro cronológico (bitácora) y buscador dinámico de integrantes.
- Expediente individual interactivo con líneas de tiempo y mapas de calor (heatmaps) de disponibilidad.
- Exportación y descarga de reportes detallados en formatos Excel, CSV y PDF.

---

## 3. Requisitos Mínimos de Uso

Para acceder y usar la aplicación correctamente, el dispositivo del usuario final solo requiere:

- **Sistema Operativo**: Windows 10, macOS, Linux, Android o iOS.
- **Navegador Web**: Google Chrome (recomendado), Microsoft Edge, Safari o Mozilla Firefox (versiones actualizadas).
- **Resolución de Pantalla**: Mínima de 1280x720 píxeles para una visualización correcta de los gráficos estadísticos.
- **Conexión de Red**: Conectividad a la red de la unidad (Intranet) o acceso local al servidor donde esté desplegado el backend.

---

## 4. Inicio del Sistema

### Acceso a la Aplicación

1. Abra su navegador web.
2. Ingrese la dirección URL del sistema en la barra de direcciones (ej. `http://localhost:5173` o la dirección IP provista por el administrador del sistema).
3. Presione **Enter**. La interfaz del **Dashboard General** se cargará de inmediato.

> [!NOTE]
> Para simplificar los procesos operacionales dentro de la red local, esta versión de la aplicación no requiere inicio de sesión con contraseña ni configuraciones de recuperación de cuentas.

---

## 5. Interfaz Principal

La pantalla está dividida en tres áreas clave:

1. **Barra Lateral de Navegación**: Menú de acceso directo a los módulos del sistema:
   - **Dashboard**: Panel de control general y KPIs rápidos.
   - **Cronología**: Bitácora de reportes de novedades diarias.
   - **Estadísticas**: Gráficos analíticos agregados.
   - **Reportes**: Generación de reportes consolidados oficiales por día.
   - **Personal**: Catálogo y buscador del personal.
2. **Barra Superior**: Contiene el indicador de la fecha actual seleccionada y el selector global de **Mes Activo** del sistema, el cual condiciona la información mostrada.
3. **Panel Principal**: El área central donde se interactúa con las tablas, formularios y gráficos de cada módulo.

---

## 6. Uso del Sistema (Módulo por Módulo)

### 📊 Módulo 1: Dashboard

Es la pantalla de bienvenida. Le indica el estado general de la unidad.

- **KPIs Rápidos (Tarjetas)**:
  - **Personal Registrado**: Número de personas totales en la base de datos.
  - **Disponibles**: Miembros listos para el servicio activo (estados `"CDO UNIDAD"` o `"AREA OPERACIONES"`).
  - **En Novedades**: Miembros inactivos temporalmente.
  - **Porcentaje de Disponibilidad**: Estado porcentual del personal de servicio.
  - **Novedades Médicas/Administrativas**: Desglose rápido del tipo de novedades vigentes hoy.
- **Gráficos**:
  - **Evolución**: Línea temporal mensual que sube o baja de acuerdo al porcentaje de disponibles día con día.
  - **Distribución de Novedades**: Anillo de dona para ver qué tipo de novedad está restando más fuerza a la unidad en la fecha actual.
- **Novedades Diarias (Cambios)**: En la parte inferior, este panel lista de forma automática los integrantes que entraron a una novedad hoy o que volvieron a estar disponibles en comparación con el día de ayer, evitando buscar en cientos de registros manualmente.

---

### 📅 Módulo 2: Cronología

Permite revisar de forma retrospectiva el reporte de novedades oficiales de cualquier fecha seleccionada.

- **Cómo usarlo**:
  1. Utilice el selector de fecha del calendario.
  2. El sistema listará en una tabla detallada a todos los integrantes que registraron una novedad ese día.
  3. Puede usar el buscador superior para escribir un nombre o una cédula para verificar si ese integrante estuvo de novedad en esa fecha.
  4. También puede filtrar el listado seleccionando una subnovedad en específico (ej. "VACACIONES").

---

### 📈 Módulo 3: Estadísticas

Muestra análisis acumulativos ideales para planes de vacaciones y asignación de personal.

- **Ranking de Subnovedades**: Barra interactiva que muestra cuáles han sido las novedades más solicitadas y registradas históricamente.
- **Historico Mensual**: Cuadrante comparativo de los promedios mensuales de disponibilidad del personal.

---

### 📥 Módulo 4: Centro de Reportes

Permite descargar reportes consolidados diarios.

- **Cómo generar un reporte**:
  1. Ingrese a la pestaña **Reportes**.
  2. En la tarjeta "Reporte Diario de Personal", seleccione la fecha exacta en el selector del calendario.
  3. Haga clic en el botón del formato deseado: **Exportar CSV**, **Exportar Excel** o **Exportar PDF** para descargar el documento oficial a su ordenador.

---

### 👤 Módulo 5: Personal (Catálogo y Perfil)

Permite buscar un integrante y auditar su hoja de ruta operacional completa.

- **Búsqueda**: Ingrese al módulo **Personal** y escriba el nombre o cédula en la barra de búsqueda predictiva. Seleccione el integrante en la lista de resultados para abrir su ficha.
- **Ficha Técnica**:
  - Muestra sus datos básicos e índices de disponibilidad histórica.
  - El gráfico de torta indica qué porcentaje del tiempo ha estado disponible frente a sus novedades totales.
  - La **Línea de tiempo** muestra de forma secuencial descendente sus últimos movimientos operacionales.
- **Mi Historial Operacional y Mapa de Calor**:
  - **Vista Mensual**: Muestra una cuadrícula de 31 celdas para el mes seleccionado. Cada celda indica si el integrante estuvo **Disponible (D, verde)**, de **Novedad (N, naranja)** o si **no había reporte (-, gris)**.
  - **Vista Anual**: Muestra el mapa de calor completo de los 12 meses del año en una sola pantalla, facilitando la detección de patrones de inactividad de un solo vistazo.
  - **Reporte Detallado (Tabla)**: Reemplaza la vista del día único por una grilla interactiva paginada que reúne todos los registros del integrante. Puede escribir en el buscador de la tabla o filtrar por subnovedad para localizar un registro rápidamente.
  - **Generar Reporte (Modal)**: Ubicado en la esquina superior del perfil. Al presionarlo, se abre un popup que le permite descargar la información del integrante personalizando el reporte:
    1. Elija el formato: **EXCEL**, **CSV** o **PDF**.
    2. Seleccione el rango: **Historial Completo** (todas las fechas) o **Heatmap Mensual** (matriz del mes).
    3. Especifique el mes del reporte.
    4. **Filtrar por Subnovedad (Opcional)**: Si desea exportar solo un tipo de novedad específico (ej. exportar solo sus días de "INCAPACIDAD MÉDICA").
    5. Presione **Descargar**.

---

### 🔄 Módulo 6: Sincronizar Reportes (Carga de Datos)

Permite subir nuevos reportes operacionales a la base de datos de manera interactiva para solventar vacíos de información o días que aparezcan sin registro (N/A).

- **Cómo usarlo**:
  1. Diríjase a la sección **Sincronizar Reportes** en el menú de navegación.
  2. Seleccione el **Modo de Carga**:
     - **Por Día Operativo**: Permite subir la asistencia de una fecha en concreto seleccionando el calendario (acepta formatos Excel `.xlsx` y JSON `.json`).
     - **Por Mes Completo**: Permite subir un archivo consolidado con múltiples días de un mes seleccionando el mes en la lista desplegable (requiere formato JSON `.json`).
  3. **Descarga de Plantillas**: Si no conoce la estructura o columnas necesarias, haga clic en los botones superiores **PLANTILLA EXCEL** o **PLANTILLA JSON** para descargar el archivo base.
  4. Seleccione o arrastre su archivo en la zona punteada **Drag & Drop**.
  5. Si desea sobreescribir reportes de fechas que ya se encuentran guardadas en la base de datos (por ejemplo, si desea corregir un reporte diario ya subido), marque la opción **"Sobreescribir reporte si ya existe"**.
  6. Presione **Sincronizar Reporte**. El sistema validará la presencia de las columnas obligatorias (`CEDULA`, `APELLIDOS Y NOMBRES`, `SUBNOVEDAD`) y actualizará automáticamente todos los módulos de estadísticas y dashboards.

---

## 7. Mensajes y Errores Frecuentes

| Mensaje en Pantalla                                         | Significado                                                 | Acción Sugerida                                                                               |
| :---------------------------------------------------------- | :---------------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| **Error al conectar con la API**                            | El frontend no se puede comunicar con el backend.           | Verifique que el servidor backend (`uvicorn`) esté encendido en la terminal.                  |
| **No se encontraron registros para los filtros ingresados** | La búsqueda en la tabla no arroja coincidencias.            | Revise la ortografía de la búsqueda o limpie el filtro de subnovedades seleccionando "Todas". |
| **- (Celda en Gris en Heatmap)**                            | No existe reporte operacional para esa fecha en el sistema. | El día consultado no cuenta con reporte cargado en la base de datos de la unidad.             |

---

## 8. Preguntas Frecuentes

### ¿Cómo cambio el mes del sistema?

En la esquina superior derecha de la aplicación verá un selector que indica el mes activo. Haga clic y elija un mes diferente; toda la información de la aplicación se actualizará para coincidir con el mes seleccionado.

### ¿Qué significan las letras "D", "N" y "-" en los Heatmaps del perfil?

- **D (Fondo Verde)**: Integrante **Disponible** para el servicio.
- **N (Fondo Naranja)**: Integrante en situación de **Novedad** (vacaciones, permiso, médica, etc.).
- **- (Fondo Gris oscuro)**: **Sin registro** en el sistema para esa fecha.

### ¿Por qué mi descarga de PDF o Excel no inicia?

Compruebe si su navegador web tiene bloqueada la descarga automática de archivos múltiples. De ser así, permita las descargas provenientes del sitio del sistema en la barra de direcciones del navegador.

---

## 9. Contacto y Soporte

Si experimenta fallos de conexión persistentes, problemas con la base de datos o desea solicitar nuevas funciones para la herramienta, comuníquese con:

- **Oficina de Tecnologías de la Información (TI)**
- **Responsable de Soporte del Sistema BIMEH**
- **Correo de contacto**: `soporte.bimeh@unidad.mil.co` (o contacto directo en la sección de sistemas de su unidad).
