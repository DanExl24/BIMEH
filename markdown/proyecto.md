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

# Stats de la pagina web:

1. Dashboard general

La primera pantalla debería responder en menos de 10 segundos: "¿Cómo está la unidad hoy?"

Podrías tener tarjetas arriba:

📅 Fecha seleccionada: 2026-01-18

👥 Personal registrado
842

✅ Disponibles
615

🏥 En novedades
227

📈 Disponibilidad
73.0%

🔄 Cambios respecto a ayer
18

Es lo primero que miraría un comandante.

2. Evolución diaria

Una línea de tiempo.

Disponibles
850 ─────────────╮
830 ───────────╮ │
810 ───────╮ │ │
790 ────╮ │ │ │
770 ──╮ │ │ │ │
1 5 10 15 20 25 30

Así ves si la disponibilidad cayó.

3. Novedades más frecuentes

Un gráfico de barras.

VACACIONES ███████████
CITA MEDICA ███████
PERMISO █████
HOSPITALIZADO ███
CAPACITACIÓN ██ 4. Personal por estado

Otro grafico de barras

Disponible 74%
Vacaciones 12%
Médicas 7%
Permisos 5%
Otros 2%

Aunque personalmente prefiero barras. Los pasteles son bonitos, pero comparan mal cantidades.

5. Calendario de actividad

Algo tipo GitHub.

L M M J V S D

🟩🟩🟨🟥🟩🟩🟩
🟩🟩🟩🟩🟩🟨🟥

Color según porcentaje de disponibilidad.

6. Buscador

Escribes

1015413550

o

Ramírez

y aparece

Nombre:
RAMIREZ BOGOYA OMAR

Estado hoy
Disponible

Última novedad
CITA MEDICA

Desde
15/01

Hasta
17/01 7. Línea de tiempo individual

Aquí creo que está el mayor valor.

15 Enero
Disponible

16 Enero
Disponible

17 Enero
Cita médica

18 Enero
Cita médica

19 Enero
Disponible

20 Enero
Vacaciones

21 Enero
Vacaciones

Como un historial.

8. Tiempo acumulado

Por persona.

Disponible
318 días

Vacaciones
22 días

Citas médicas
5 días

Permisos
11 días 9. Ranking

No para señalar gente, sino para detectar patrones.

Ejemplo:

Subnovedades más frecuentes

Vacaciones
231

Cita médica
114

Permiso
87

Hospital
15 10. Cambios entre días

Esto me parece muy útil.

Hoy cambiaron:

- 8 personas entraron a vacaciones

- 4 volvieron disponibles

- 2 ingresaron hospitalizados

Eso evita revisar 800 registros manualmente.

11. Estadísticas por persona

Cuando abras un perfil:

Nombre

──────────────

Tiempo disponible
91%

Tiempo en novedades
9%

Total novedades
14

Última novedad
Vacaciones

Promedio duración novedades
4.3 días 12. Heatmap

Una tabla enorme.

            Enero

Persona 1 2 3 4 5 6

Juan 🟩🟩🟩🟨🟨🟩

Pedro 🟩🟥🟥🟥🟩🟩

Carlos 🟩🟩🟩🟩🟩🟩

Cada cuadro un día.

Verías patrones enseguida.

Organizacion por modulos:

# Modulos

📊 Dashboard
KPIs
Disponibilidad
Novedades
Evolución
Cambios diarios
👤 Personal

Buscador.

Perfil.

Historial.

📈 Estadísticas

Todos los gráficos.

Comparaciones.

Rankings.

Distribuciones.

📅 Cronología

Seleccionas una fecha.

Ves exactamente cómo estaba toda la unidad ese día.

- Exportacion PDF,EXCEL y CSV
- Reporte por personal
- Reporte por mes
- Reporte por dia
  La exportacion PDF debe incluir graficas interactivas

- SQLITE:

## PERSONAL

id
cedula UNIQUE
nombre
fecha_retiro

## SUB_NOVEDADES

id
nombre

## REPORTES

id
fecha
archivo

## REGISTRO_PERSONAL

id
id_reporte
id_personal
id_sub_novedad
descripcion
fecha_inicio
fecha_final

- Un personal puede tener muchas sub_novedades
- Una novedad puede estar en muchos registros
- un reporte puede estar en muchos registros
- Un personal solo puede tener una sub_novedad por dia
- Un personal puede tener muchas registros por mes

# Personal

La cédula es única.
Un registro pertenece a un único integrante del personal.

# Subnovedades

Una subnovedad puede asociarse a múltiples personas.
Cada registro solo puede tener una subnovedad.

# Reportes

Un reporte corresponde a una única fecha.
Una fecha solo puede tener un reporte oficial.

# Detalles

Un registro pertenece a una sola persona.
Un registro pertenece a un solo reporte.
Un registro tiene una única subnovedad.
Un mismo integrante no puede tener dos registros diferentes para la misma fecha de reporte.
