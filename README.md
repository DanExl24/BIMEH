Automatizacion en busqueda de datos informativos

Problema: Busqueda manual de novedades y fechas de novedad para las personas dentro de BIMEj

Objetivo: Crear una aplicacion que permita listar todo el personal recuperando datos especificos sobre su novedad por meses y por los dias de mes.

Logica actual:

- Traer todas las carpetas de google drive que contenga un mes en su nombre
- Extraer todos los archivos excel dentro de cada carpeta, excluyendo otro tipo de formato
- Leer la hoja "DEMOSTRATIVO" de cada archivo
- Obtener todo el personal dentro de la tabla insertada
- Extraer campos:
  - Nombre
  - Cedula
  - Subnovedad
  - Rango de fechas (DESDE/HASTA)
    Crear archivo .json con la informacion recolectada
- Crear app web
  Debe contener:
- Filtros
  - Nombre
  - Cedula
  - Mes
  - Dia del mes
- Busqueda
- Todos los campos
- Exportacion PDF,EXCEL y CSV
- Estatisticas
  - Por personal
  - Por mes
  - por rango de fechas
  - Por novedad

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

Un pastel.

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

Muy visual.

6. Buscador

Este sería el fuerte.

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
