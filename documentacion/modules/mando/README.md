# Módulo 10: Centro de Mando S-1 & Inteligencia Preventiva (`mando`)

El módulo de **Centro de Mando S-1 & Inteligencia Preventiva** proporciona herramientas de supervisión proactiva del talento humano y estado de fuerza operacional del **Batallón de Infantería N° 12 "GR. ALFONSO MANRIQUE REYES" (BIMEJ 12)**. Su propósito es anticipar vulnerabilidades en la disponibilidad de la unidad, controlar la fatiga de combate en primera línea, realizar seguimiento a contingencias médicas críticas y consolidar el boletín diario oficial de comando conocido como **"El Parte de las 06:00"**.

---

## 🏛️ Propósito y Alcance

Tradicionalmente, la Sección de Personal (S-1) consolida novedades de forma reactiva a partir de planillas y libros de guardia. Este módulo transforma esa información en **inteligencia de mando preventiva** mediante:
1. **Radar de Fatiga Operacional**: Detección de efectivos que acumulan períodos prolongados continuos de servicio en el terreno sin haber gozado de descansos reglamentarios (permisos o vacaciones).
2. **Alertas de Sanidad y Junta Médica**: Auditoría de ausentismos médicos reiterados o prolongados (incapacidades médicas, hospitalizaciones, tratamiento de leishmaniasis) para sugerir la remisión oportuna ante la Junta Médico-Laboral Militar.
3. **Proyección de Fuerza Disponible (Horizontes a 7, 15 y 30 días)**: Estimación analítica del pie de fuerza disponible a futuro basada en las fechas de término y retorno de novedades activas.
4. **"El Parte de las 06:00" & Radiograma Castrense**: Generación automática del boletín diario de situación operacional en formato militar oficial y texto listo para radiograma o mensaje institucional.
5. **Exportación Oficial en PDF**: Emisión de documentos ejecutivos con tipografía institucional, cuadros de operatividad y bloques reglamentarios de firma de comandancia.

---

## 🏗️ Arquitectura y Componentes Técnicos

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vue 3 + TailwindCSS)                  │
├────────────────────────────────────────────────────────────────────────┤
│  • MandoS1View.vue (/mando-s1)       → Vista integral de Centro Mando  │
│  • CommandBriefingModal.vue          → Modal interactivo del Parte     │
│  • DashboardFatigueRadar.vue         → Widget de Radar de Fatiga       │
│  • DashboardForceProjection.vue      → Widget de Proyección de Fuerza  │
│  • alertas.service.ts                → Cliente HTTP de Alertas & Mando │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ HTTP REST
┌────────────────────────────────────▼───────────────────────────────────┐
│                     BACKEND (FastAPI + ReportLab + Python)             │
├────────────────────────────────────────────────────────────────────────┤
│  • app/routers/alertas.py            → Endpoints analíticos de mando   │
│  • app/routers/exportar.py           → Generador ReportLab PDF Parte   │
│  • app/models.py                     → Esquemas Pydantic de Mando      │
│  • app/dependencies.py               → Filtros temporales y estados    │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ SQL Queries
┌────────────────────────────────────▼───────────────────────────────────┐
│                    BASE DE DATOS (PostgreSQL / DuckDB)                  │
│    • REPORTES, REGISTRO_PERSONAL, PERSONAL, SUB_NOVEDADES               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 Endpoints del Módulo

| Método | Endpoint | Descripción | Parámetros Principales |
|---|---|---|---|
| `GET` | `/api/alertas/fatiga` | Lista de personal con fatiga operacional por días continuos en servicio | `umbral` (def: 30), `mes`, `dia`, `fecha` |
| `GET` | `/api/alertas/sanidad` | Detección de personal con novedades médicas acumuladas y recomendación de Junta Médica | `dias_min` (def: 15), `mes`, `dia`, `fecha`, `anio` |
| `GET` | `/api/alertas/proyeccion` | Proyección de fuerza disponible a horizontes de 7, 15 y 30 días y reincorporaciones | `dias` (def: 30), `mes`, `dia`, `fecha` |
| `GET` | `/api/alertas/parte-diario` | Estado de fuerza diario consolidado, desglose por categorías y radiograma oficial | `mes`, `dia`, `fecha` |
| `GET` | `/api/exportar/pdf/parte-diario` | Generación y descarga del Boletín Oficial en formato PDF institucional | `mes`, `dia`, `fecha` |
| `GET` | `/api/alertas/inconsistencias` | Registro de anomalías o discrepancias de procesamiento detectadas | Ninguno |

---

## 📦 Estructura de Archivos del Módulo

```
BIMEH/
├── backend/
│   └── app/
│       ├── routers/
│       │   ├── alertas.py             # Endpoints del Centro de Mando
│       │   └── exportar.py            # Generación de PDF oficial del parte (Línea 2196)
│       └── models.py                  # Pydantic: AlertaFatigaItem, ParteDiarioData, etc.
└── frontend/
    └── src/
        ├── features/
        │   ├── mando/
        │   │   └── views/
        │   │       └── MandoS1View.vue          # Vista principal /mando-s1
        │   └── dashboard/
        │       ├── components/
        │       │   ├── CommandBriefingModal.vue # Modal interactivo de radiograma militar
        │       │   ├── DashboardFatigueRadar.vue# Widget visual de radar de fatiga
        │       │   └── DashboardForceProjection.vue # Widget visual de proyección de fuerza
        │       └── services/
        │           └── alertas.service.ts       # Servicio HTTP con métodos del módulo
        └── router/
            └── index.ts                         # Ruta /mando-s1 con guard de autenticación
```
