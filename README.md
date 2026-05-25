# 🎓 HorarioUCJC — Sistema de Gestión Inteligente de Horarios Académicos

**Plataforma web integral para la planificación automática y gestión de horarios académicos** de la Escuela Politécnica de la Universidad Camilo José Cela (UCJC).

Desarrollado con **Django 5.2**, **Tailwind CSS** y un **motor de generación basado en Algoritmo Genético** que optimiza automáticamente la asignación de sesiones académicas respetando más de 10 restricciones complejas.

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características Principales](#-características-principales)
3. [Requisitos del Sistema](#-requisitos-del-sistema)
4. [Instalación](#-instalación)
5. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
6. [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
7. [Modelos de Base de Datos](#-modelos-de-base-de-datos)
8. [Sistema de Roles y Permisos](#-sistema-de-roles-y-permisos)
9. [Motor de Generación — Algoritmo Genético](#-motor-de-generación--algoritmo-genético)
10. [Restricciones del Sistema](#-restricciones-del-sistema)
11. [Endpoints Principales](#-endpoints-principales)
12. [Estructura de Carpetas](#-estructura-de-carpetas)
13. [Comandos de Gestión](#-comandos-de-gestión)
14. [Variables de Entorno](#-variables-de-entorno)
15. [Flujo de Trabajo del Horario](#-flujo-de-trabajo-del-horario)
16. [Funcionalidades de Drag & Drop](#-funcionalidades-de-drag--drop)
17. [Auditoría e Historial](#-auditoría-e-historial)

---

## 📊 Descripción General

**HorarioUCJC** es una solución integral que permite al **Decanato** de UCJC planificar automáticamente los horarios de cada titulación y nivel académico de forma inteligente y eficiente.

### Objetivos Principales:

- ✅ **Generación automática** de horarios respetando 10+ restricciones académicas
- ✅ **Gestión centralizada** de titulaciones, asignaturas, profesores y aulas
- ✅ **Workflow de aprobación** con trazabilidad completa (Borrador → Revisión → Aprobado/Rechazado)
- ✅ **Sistema de notificaciones** in-app para todos los actores (profesores, alumnos, decanato)
- ✅ **Auditoría inmutable** de cambios con timestamp y usuario responsable
- ✅ **Exportación en PDF y Excel** de horarios y reportes
- ✅ **Detección de conflictos** en tiempo real
- ✅ **Interfaz responsiva** con tema dark mode profesional

---

## ⭐ Características Principales

### 🔧 Para el Decanato:

- Crear y gestionar múltiples horarios por titulación y nivel
- Configurar franjas horarias (mañana/tarde), aulas disponibles
- Aprobar/rechazar horarios con comentarios
- Gestionar usuarios (profesores, alumnos, administradores)
- Visualizar auditoría completa de cambios
- Exportar horarios en PDF y Excel
- Configurar restricciones personalizadas antes de generar

### 👨‍🏫 Para los Profesores:

- Registrar disponibilidad horaria (INDISPONIBLE/PREFERENTE)
- Ver su horario personal asignado
- Recibir notificaciones de cambios
- Indicar preferencias de franjas

### 👨‍🎓 Para los Alumnos:

- Visualizar su horario según titulación y nivel
- Ver conflictos potenciales (sesiones simultáneas del mismo semestre)
- Recibir notificaciones de cambios
- Acceso de solo lectura

---

## 💻 Requisitos del Sistema

| Requisito | Versión Mínima |
|-----------|-----------------|
| **Python** | 3.11+ |
| **Node.js** | 18+ (para compilar Tailwind) |
| **pip** | Compatible con Python 3.11+ |
| **Base de Datos** | SQLite3 (por defecto), PostgreSQL compatible |
| **Navegador** | Chrome, Firefox, Edge, Safari (últimas 2 versiones) |

---

## 📦 Instalación

### Paso 1: Clonar el repositorio

```bash
git clone <repo-url>
cd HorarioUCJC
```

### Paso 2: Crear y activar entorno virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 3: Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus datos (credenciales OAuth, secrets, etc.)
```

### Paso 5: Ejecutar migraciones de base de datos

```bash
python manage.py migrate
```

### Paso 6: Cargar datos iniciales (opcional)

```bash
# Cargar estructura de la Escuela Politécnica
python manage.py seed_politecnica

# Cargar datos de profesores de ejemplo
python manage.py seed_profesores

# Cargar disponibilidad de ejemplo
python manage.py seed_disponibilidad
```

### Paso 7: Compilar Tailwind CSS

```bash
# Instalar dependencias de Node
python manage.py tailwind install

# Compilar Tailwind (modo desarrollo)
python manage.py tailwind build

# O compilar en watch mode
python manage.py tailwind build --watch
```

### Paso 8: Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### Paso 9: Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Acceder a `http://localhost:8000`

---

## 🛠️ Tecnologías Utilizadas

### Backend:
- **Django 6.0.5** — Framework web Python
- **Django Allauth 65.17.0** — Autenticación (email, OAuth Google/Microsoft)
- **Django HTMX 1.27.0** — Interactividad sin JavaScript
- **Django Debug Toolbar** — Debugging en desarrollo
- **SQLAlchemy** (indirecto) — ORM robusto

### Frontend:
- **Tailwind CSS 4.4.2** — Utility-first CSS framework
- **HTMX 1.27.0** — HTML5 Drag & Drop API nativa
- **JavaScript Vanilla** — Sin dependencias heavy
- **Bootstrap Icons** (potencial) — Iconografía

### Utilitarios:
- **python-dotenv** — Variables de entorno
- **openpyxl** — Exportación Excel
- **python-slugify** — Generación de URLs amigables
- **arrow** — Manipulación de fechas
- **requests** — Cliente HTTP

### DevOps:
- **honcho** — Gestor de procesos (como Foreman)
- **cookiecutter** — Generación de templates
- **pytest** (implícito) — Testing

---

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una **arquitectura modular de Django** con apps bien separadas por responsabilidad:

```
HorarioUCJC/                 # Raíz del proyecto
│
├── HorarioUCJC/             # Configuración principal
│   ├── settings.py          # Configuración de Django
│   ├── urls.py              # Rutas principales
│   ├── wsgi.py              # Servidor WSGI
│   ├── asgi.py              # Servidor ASGI
│   └── __init__.py
│
├── core/                    # App de modelos académicos
│   ├── models.py            # Titulacion, Asignatura, NivelCurso, Aula, etc.
│   ├── views.py             # Dashboard, gestión de usuarios
│   ├── forms.py             # Formularios de modelos
│   ├── admin.py             # Panel de administración Django
│   ├── urls.py              # Rutas de core (/users/, /dashboard/)
│   ├── management/          # Comandos personalizados
│   │   └── commands/        # seed_politecnica, seed_profesores, etc.
│   ├── migrations/          # Historial de cambios en BD
│   └── __init__.py
│
├── login/                   # App de autenticación
│   ├── models.py            # Usuario (AbstractUser), PerfilDecano, PerfilProfesor, PerfilAlumno
│   ├── views.py             # Login, logout, autenticación OAuth
│   ├── middleware.py        # LoginRequiredMiddleware
│   ├── forms.py             # Formularios de autenticación
│   ├── urls.py              # Rutas de autenticación
│   ├── migrations/          # Historial BD
│   └── __init__.py
│
├── schedule/                # App de gestión de horarios
│   ├── models.py            # Horario, Sesion, FranjaHoraria, Restriccion (vacío)
│   ├── views.py             # 33+ vistas (CRUD horarios, generación, etc.)
│   ├── forms.py             # Formularios de horarios
│   ├── generator.py         # Motor de Algoritmo Genético ⭐
│   ├── audit.py             # Sistema de auditoría
│   ├── context_processors.py# Contexto global para templates
│   ├── urls.py              # Rutas de schedule (/schedule/*)
│   ├── admin.py             # Admin de schedule
│   ├── migrations/          # Historial BD
│   ├── templatetags/        # Filtros y tags personalizados
│   │   └── schedule_tags.py
│   └── __init__.py
│
├── theme/                   # App de tema (Tailwind CSS)
│   ├── apps.py
│   ├── static/css/          # CSS personalizado
│   ├── static_src/src/      # Fuente de Tailwind
│   ├── templates/base.html  # Template base
│   └── __init__.py
│
├── templates/               # Plantillas HTML globales
│   ├── base.html            # Layout principal
│   ├── components/          # Componentes reutilizables
│   │   ├── header.html
│   │   ├── aside.html (sidebar)
│   │   └── toast.html
│   ├── core/                # Templates de core
│   ├── login/               # Templates de login
│   ├── schedule/            # Templates de horarios
│   │   ├── horario_pdf.html
│   │   ├── crear.html
│   │   ├── detalle.html
│   │   ├── generar.html
│   │   ├── restricciones.html
│   │   └── ... (15+ templates)
│   └── theme/
│
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
│   ├── css/                 # CSS compilado
│   ├── js/                  # JavaScript
│   │   ├── schedule_detalle.js    # Lógica de drag & drop
│   │   ├── restricciones.js
│   │   ├── login.js
│   │   ├── toast.js               # Sistema de notificaciones
│   │   └── ...
│   └── images/              # Imágenes y logos
│
├── manage.py                # Script de gestión Django
├── requirements.txt         # Dependencias Python
├── db.sqlite3              # Base de datos SQLite (no versionable)
├── README.md               # Este archivo
├── REQUISITOS.txt          # Especificación de requisitos (RF/RD/RNF)
└── .env.example            # Template de variables de entorno
```

---

## 📚 Modelos de Base de Datos

### Core — Estructuras Académicas

```
Titulacion
├── nombre (CharField)              # "Ingeniería Informática"
├── codigo (CharField)              # "INF"
├── tipo (ChoiceField)              # GRADO | DOBLE_GRADO
├── duracion_anios (PositiveSmallIntegerField)
├── permite_maniana (BooleanField)  # RD-18: si es doble grado
└── activa (BooleanField)

CursoAcademico
├── nombre (CharField)              # "2025-2026"
├── fecha_inicio (DateField)
├── fecha_fin (DateField)
├── estado (ChoiceField)            # PLANIFICACION | ACTIVO | CERRADO
└── matriculacion_abierta (BooleanField)

NivelCurso
├── titulacion (ForeignKey)         # Relación a Titulacion
├── anio (PositiveSmallIntegerField) # 1, 2, 3, 4, 5
└── es_ultimo (BooleanField)        # RD-18: solo tarde

Asignatura
├── codigo (CharField)              # "INF-101"
├── nombre (CharField)              # "Programación I"
├── titulaciones (ManyToMany)       # Varias titulaciones pueden compartir
├── sesiones_semanales (PositiveSmallIntegerField) # RD-01: 2
├── duracion_sesion_h (PositiveSmallIntegerField)  # RD-01: 2
├── tipo_grupo (ChoiceField)        # TEORIA | PRACTICAS | LABORATORIO
├── es_transversal (BooleanField)   # RF-13: comparten slot en titulaciones
└── semestre (PositiveSmallIntegerField) # 1 | 2
```

### Login — Autenticación y Perfiles

```
Usuario (extends AbstractUser)
├── rol (ChoiceField)               # DECANO | PROFESOR | ALUMNO | IT
├── email (EmailField, unique)      # USERNAME_FIELD
└── username

PerfilDecano
├── usuario (OneToOneField)
├── departamento (CharField)
└── puede_aprobar (BooleanField)    # RF-04: solo Decanato aprueba

PerfilProfesor
├── usuario (OneToOneField)
├── area_conocimiento (CharField)
├── es_suplente (BooleanField)      # RF-06: suplentes por área
└── asignaturas (ManyToMany)        # Asignaciones de profesor

PerfilAlumno
├── usuario (OneToOneField)
├── titulacion (ForeignKey)
├── nivel (ForeignKey)
└── grado (ManyToMany)              # Asignaturas que cursa
```

### Schedule — Gestión de Horarios

```
Horario
├── titulacion (ForeignKey)         # La titulación a la que pertenece
├── nivel (ForeignKey)              # El nivel (1º, 2º, 3º, etc.)
├── curso_academico (ForeignKey)    # Año académico
├── estado (ChoiceField)            # BORRADOR | REVISION | APROBADO | RECHAZADO
├── creado_por (ForeignKey → Usuario)
├── fecha_creacion (DateTimeField)
├── fecha_aprobacion (DateTimeField, null)
└── notas (TextField)               # Comentarios en rechazo

Sesion
├── horario (ForeignKey)            # El horario que contiene
├── asignatura (ForeignKey)         # Asignatura impartida
├── profesor (ForeignKey → Usuario) # Profesor responsable
├── franja (ForeignKey)             # FranjaHoraria asignada
├── aula (ForeignKey)               # Aula asignada
├── orden_semanal (PositiveSmallIntegerField) # 1ª, 2ª sesión de la semana
└── generada_automaticamente (BooleanField)

FranjaHoraria
├── nombre (CharField)              # "Lunes 9:00-11:00"
├── dia_semana (CharField)          # "LUNES", "MARTES", etc.
├── hora_inicio (TimeField)
├── hora_fin (TimeField)
├── es_maniana (BooleanField)       # RD-18: para distinguir turno
└── activa (BooleanField)           # RD-17: solo franjas activas

Aula
├── codigo (CharField)              # "A101", "LAB-02"
├── nombre (CharField)              # "Aula de Informática 1"
├── plazas (PositiveSmallIntegerField) # Capacidad
├── permite_practicas (BooleanField)  # ¿Tiene equipamiento?
└── activa (BooleanField)

Disponibilidad (Profesor)
├── profesor (ForeignKey → Usuario)
├── franja (ForeignKey)
├── tipo (ChoiceField)              # INDISPONIBLE | PREFERENTE
├── fecha_desde (DateField, optional)
├── fecha_hasta (DateField, optional)
├── periodo (CharField, optional)   # "2025-2026"
└── notas (TextField)

Restriccion (Custom constraints)
├── horario (ForeignKey)
├── tipo (CharField)                # Tipo de restricción personalizada
├── descripcion (TextField)
└── activa (BooleanField)

Notificacion
├── usuario (ForeignKey)
├── asunto (CharField)
├── mensaje (TextField)
├── tipo (ChoiceField)              # INFO | WARNING | ERROR
├── leida (BooleanField)
├── fecha_creacion (DateTimeField)
└── relacionado_con (GenericForeignKey, optional)

AuditoriaLog (Auditoría)
├── usuario (ForeignKey)
├── accion (CharField)              # "CREAR", "MODIFICAR", "ELIMINAR", "APROBAR"
├── modelo (CharField)              # "Horario", "Sesion", etc.
├── objeto_id (PositiveIntegerField)
├── cambios (JSONField)             # {old: {...}, new: {...}}
├── timestamp (DateTimeField)       # RNF-06, RNF-14: auditoría inmutable
└── ip_address (GenericIPAddressField, optional)
```

---

## 👥 Sistema de Roles y Permisos

El sistema implementa un **RBAC (Role-Based Access Control)** simple pero efectivo:

| Rol | Permisos | Vistas Accesibles |
|-----|----------|-------------------|
| **DECANO** | - Crear/editar/aprobar horarios<br/>- Gestionar usuarios<br/>- Configurar franjas y aulas<br/>- Ver auditoría completa<br/>- Exportar reportes | Dashboard admin, Horarios CRUD, Usuarios, Configuración, Auditoría, Curriculum |
| **PROFESOR** | - Ver su horario<br/>- Registrar disponibilidad<br/>- Ver notificaciones<br/>- Acceso de solo lectura | Mi Horario, Disponibilidad, Notificaciones, Dashboard básico |
| **ALUMNO** | - Ver su horario<br/>- Ver conflictos<br/>- Acceso de solo lectura | Mi Horario, Dashboard simple, Notificaciones |
| **IT** | - Acceso de lectura a todo<br/>- Sin permisos de edición | Auditoría, Dashboard, Reportes (solo lectura) |

**Implementación:**
- Campo `rol` en modelo `Usuario`
- Decoradores `@login_required` en vistas
- Checks de permiso en templates con `{% if user.rol == 'DECANO' %}`
- Middleware `LoginRequiredMiddleware` en [login/middleware.py](login/middleware.py)

---

## 🧬 Motor de Generación — Algoritmo Genético

El corazón del sistema se encuentra en [schedule/generator.py](schedule/generator.py). Implementa un **Algoritmo Genético (AG)** que optimiza automáticamente la asignación de sesiones académicas.

### ¿Por qué Algoritmo Genético?

Los horarios académicos son un problema **NP-completo**. El AG permite:
- ✅ Encontrar soluciones **cercanas al óptimo** en tiempo razonable
- ✅ Balancear múltiples restricciones (hard + soft)
- ✅ Adaptarse a cambios en restricciones
- ✅ Mejorar iterativamente la calidad

### Representación del Cromosoma

Cada individuo es una lista de genes `(franja_pk, aula_pk)`:

```python
# Ejemplo de cromosoma (individuos = 80)
slots_to_fill = [
    (asig_id_1, 0),  # 1ª sesión de Asignatura 1
    (asig_id_1, 1),  # 2ª sesión de Asignatura 1
    (asig_id_2, 0),  # 1ª sesión de Asignatura 2
    ...
]

chromosome[0] = (franja_pk=5, aula_pk=12)  # 1ª sesión → Franja 5, Aula 12
chromosome[1] = (franja_pk=3, aula_pk=8)   # 2ª sesión → Franja 3, Aula 8
```

### Función de Fitness (Minimizar)

| Restricción | Penalización | Crítica |
|-------------|-------------|---------|
| RD-05: Profesor en dos franjas simultáneas | 1000 × repeticiones | ❌ Hard |
| RD-12: Aula con dos sesiones simultáneas | 1000 × repeticiones | ❌ Hard |
| RD-08 (alumnos): Misma franja, mismo semestre | 800 | ❌ Hard |
| RD-08 (profesor): Franja bloqueada (INDISPONIBLE) | 600 | ❌ Hard |
| RD-14: Asignatura repetida el mismo día | 300 | ❌ Hard |
| RD-01: Sesión faltante (sin asignar) | 1500 | ❌ Hard |
| Soft: Franja PREFERENTE del profesor | −60 (recompensa) | ✅ Soft |
| Soft: Compacidad (RD-13) - Dispersión de días | 25 × span días | ✅ Soft |

**Objetivo:** Minimizar el fitness total (ideal = 0)

### Parámetros del Algoritmo

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| **Tamaño de población** | 80 individuos | Balance entre diversidad y cálculo |
| **Máximo de generaciones** | 250 | Límite de iteraciones (típico: 200-500) |
| **Tasa de mutación** | 12% | Exploración controlada |
| **Élite** | 6 individuos | Preserva mejores soluciones |
| **Selección por torneo** | k=5 candidatos | Presión de selección moderada |
| **Parada por estancamiento** | 40 generaciones sin mejora | Eficiencia (no converge indefinidamente) |

### Detección de Solapamiento

El sistema detecta **solapamiento real** de franjas (no solo comparación de hora de inicio):

```python
def _franja_overlaps_range(franja, dia, hora_ini, hora_fin):
    """Retorna True si la franja solapa con el rango [hora_ini, hora_fin] del día"""
    if franja.dia_semana != dia:
        return False
    # Solapamiento: franja.inicio < fin AND franja.fin > inicio
    return franja.hora_inicio < hora_fin and franja.hora_fin > hora_ini
```

**Ejemplo:**
- Profesor bloqueado: Martes 15:00–17:00
- Franja A: Martes 15:30–17:30 → ❌ Solapamiento (excluida)
- Franja B: Martes 14:00–16:00 → ❌ Solapamiento (excluida)
- Franja C: Martes 17:30–19:30 → ✅ Sin solapamiento (permitida)

---

## 🚫 Restricciones del Sistema

### Hard Constraints (RD) — Obligatorias

| Código | Descripción | Impacto |
|--------|-------------|--------|
| **RD-01** | Cada asignatura se imparte `sesiones_semanales` veces por semana | Todas las sesiones deben estar asignadas |
| **RD-05** | Ningún profesor imparte dos asignaturas en la misma franja (RD-05.1) | Evita conflictos horarios del profesor |
| **RD-07** | Cada asignatura tiene un único profesor titular | Garantía de responsabilidad |
| **RD-08 (profesor)** | Las clases respetan la disponibilidad del profesor (solapamiento) | Profesor no puede tener dos sesiones simultáneas |
| **RD-08 (alumnos)** | Alumnos del mismo semestre no tienen clase simultáneamente | Conflicto de asignaturas |
| **RD-10** | Asignaturas transversales usan el mismo slot en todas sus titulaciones | Consistencia para asignaturas compartidas |
| **RD-12** | Un aula no alberga dos clases simultáneamente | Evita sobrecarga de recursos |
| **RD-14** | Una asignatura no se repite el mismo día | Compacidad mínima |
| **RD-17** | Solo se usan franjas activas predefinidas | Control de horarios |
| **RD-18** | Grados individuales: turno tarde (salvo último año si el grado lo permite) | RF-02: Restricción de turno |

### Soft Constraints — Deseables

| Código | Descripción |
|--------|-------------|
| **RD-13** | Sesiones de la misma asignatura en días distintos (compacidad óptima) |
| **Preferencias** | Preferir franjas marcadas como PREFERENTE por el profesor |

---

## 🔌 Endpoints Principales

### Core — Dashboard y Usuarios

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| GET | `/` | Dashboard principal | Todos |
| GET | `/usuarios/` | Gestión de usuarios | DECANO |
| POST | `/usuarios/<id>/rol/` | Cambiar rol de usuario | DECANO |
| POST | `/usuarios/<id>/grado/` | Asignar grado a alumno | DECANO |

### Schedule — Horarios y Generación

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| GET | `/schedule/` | Home de horarios | DECANO |
| GET | `/schedule/horarios/` | Listar horarios | DECANO |
| POST | `/schedule/horarios/crear/` | Crear nuevo horario | DECANO |
| GET | `/schedule/horarios/<id>/` | Ver detalle de horario | DECANO |
| DELETE | `/schedule/horarios/<id>/eliminar/` | Eliminar horario | DECANO |
| POST | `/schedule/horarios/<id>/generar/` | Generar horario (AG) | DECANO |
| GET | `/schedule/horarios/<id>/log/` | Ver log de generación | DECANO |
| POST | `/schedule/horarios/<id>/workflow/` | Cambiar estado (workflow) | DECANO |

### Restricciones y Configuración

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| GET | `/schedule/horarios/<id>/restricciones/` | Listar restricciones | DECANO |
| DELETE | `/schedule/horarios/<id>/restricciones/eliminar/<rpk>/` | Eliminar restricción | DECANO |
| GET | `/schedule/config/` | Configuración (franjas, aulas) | DECANO |
| POST | `/schedule/config/franja/<id>/toggle/` | Activar/desactivar franja | DECANO |
| DELETE | `/schedule/config/franja/<id>/eliminar/` | Eliminar franja | DECANO |

### Sesiones (Edición Manual)

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| POST | `/schedule/horarios/<id>/sesion/crear/` | Crear sesión manual | DECANO |
| DELETE | `/schedule/sesiones/<id>/eliminar/` | Eliminar sesión | DECANO |
| POST | `/schedule/sesiones/<id>/mover/` | Mover sesión (drag-drop) | DECANO |
| GET | `/schedule/sesiones/<id>/conflictos/` | Detectar conflictos | DECANO |

### Disponibilidad del Profesor

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| GET | `/schedule/disponibilidad/` | Ver disponibilidades | PROFESOR |
| POST | `/schedule/disponibilidad/` | Registrar disponibilidad | PROFESOR |
| DELETE | `/schedule/disponibilidad/<id>/eliminar/` | Eliminar disponibilidad | PROFESOR |

### Personal

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| GET | `/schedule/mi-horario/` | Ver tu horario | PROFESOR, ALUMNO |
| GET | `/schedule/notificaciones/` | Ver notificaciones | Todos |
| POST | `/schedule/notificaciones/<id>/leer/` | Marcar notificación como leída | Todos |
| DELETE | `/schedule/notificaciones/<id>/eliminar/` | Eliminar notificación | Todos |

### Informes y Exportación

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| GET | `/schedule/informes/` | Página de informes | DECANO |
| GET | `/schedule/horarios/<id>/export/pdf/` | Exportar horario en PDF | DECANO |
| GET | `/schedule/horarios/<id>/export/excel/` | Exportar horario en Excel | DECANO |

### Curriculum (Titulaciones y Asignaturas)

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| GET | `/schedule/curriculum/` | Ver plan de estudios | DECANO |
| POST | `/schedule/curriculum/titulacion/crear/` | Crear titulación | DECANO |
| GET | `/schedule/curriculum/titulacion/<id>/` | Detalle titulación | DECANO |
| POST | `/schedule/curriculum/titulacion/<id>/editar/` | Editar titulación | DECANO |
| DELETE | `/schedule/curriculum/titulacion/<id>/eliminar/` | Eliminar titulación | DECANO |
| POST | `/schedule/curriculum/titulacion/<tit_id>/asignatura/crear/` | Crear asignatura | DECANO |
| POST | `/schedule/curriculum/asignatura/<id>/editar/` | Editar asignatura | DECANO |
| DELETE | `/schedule/curriculum/asignatura/<id>/eliminar/` | Eliminar asignatura | DECANO |

### Auditoría

| Método | Endpoint | Descripción | Rol |
|--------|----------|-------------|-----|
| GET | `/schedule/audit/` | Ver log de auditoría | DECANO, IT |

---

## 📁 Estructura de Carpetas

```
d:\Proyectos\HorarioUCJC/
│
├── 📄 manage.py                        # Script de gestión Django
├── 📄 db.sqlite3                       # Base de datos (no versionar)
├── 📄 requirements.txt                 # Dependencias Python
├── 📄 REQUISITOS.txt                   # Especificación (RF/RD/RNF)
├── 📄 README.md                        # Este archivo
├── 📄 .env.example                     # Template variables de entorno
│
├── 📂 HorarioUCJC/                     # Configuración principal
│   ├── __init__.py
│   ├── settings.py                     # Configuración de Django
│   ├── urls.py                         # Rutas principales
│   ├── asgi.py                         # Aplicación ASGI
│   └── wsgi.py                         # Aplicación WSGI
│
├── 📂 core/                            # App de modelos académicos
│   ├── __init__.py
│   ├── admin.py                        # Panel administrativo
│   ├── apps.py                         # Configuración de app
│   ├── models.py                       # Titulacion, Asignatura, etc. ⭐
│   ├── views.py                        # Dashboard, gestión de usuarios
│   ├── forms.py                        # Formularios
│   ├── urls.py                         # Rutas
│   ├── tests.py                        # Tests unitarios
│   ├── 📂 management/
│   │   ├── __init__.py
│   │   └── 📂 commands/
│   │       ├── __init__.py
│   │       ├── seed_politecnica.py     # Cargar datos de Politécnica
│   │       ├── seed_profesores.py      # Cargar profesores
│   │       └── seed_disponibilidad.py  # Cargar disponibilidades
│   ├── 📂 migrations/                  # Historial de BD
│   │   ├── 0001_initial.py
│   │   ├── 0002_initial.py
│   │   ├── 0003_restriccion_personalizada.py
│   │   ├── 0004_disponibilidad_add_periodo.py
│   │   └── 0005_sesion_remove_profesor_unique.py
│   └── __init__.py
│
├── 📂 login/                           # App de autenticación
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                       # Usuario, Perfil* ⭐
│   ├── views.py                        # Login, logout, OAuth
│   ├── forms.py                        # Formularios de auth
│   ├── middleware.py                   # LoginRequiredMiddleware
│   ├── urls.py                         # Rutas de auth
│   ├── tests.py
│   ├── 📂 migrations/
│   │   └── 0001_initial.py
│   └── __init__.py
│
├── 📂 schedule/                        # App de horarios ⭐
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                       # (vacío, modelos en core)
│   ├── views.py                        # 33+ vistas ⭐
│   ├── forms.py                        # Formularios
│   ├── generator.py                    # Algoritmo Genético ⭐
│   ├── audit.py                        # Sistema de auditoría
│   ├── context_processors.py           # Contexto global
│   ├── urls.py                         # Rutas ⭐
│   ├── tests.py
│   ├── 📂 migrations/
│   │   └── __init__.py
│   ├── 📂 templatetags/
│   │   ├── __init__.py
│   │   └── schedule_tags.py            # Filtros personalizados
│   └── __init__.py
│
├── 📂 theme/                           # App de Tailwind CSS
│   ├── __init__.py
│   ├── apps.py
│   ├── 📂 static/
│   │   └── 📂 css/                     # CSS compilado
│   ├── 📂 static_src/
│   │   └── 📂 src/
│   │       └── styles.css              # Fuente Tailwind
│   ├── 📂 templates/
│   │   └── base.html                   # Template base
│   └── __init__.py
│
├── 📂 templates/                       # Plantillas HTML globales
│   ├── base.html                       # Layout principal
│   ├── 📂 components/                  # Componentes reutilizables
│   │   ├── aside.html                  # Sidebar
│   │   ├── header.html                 # Encabezado
│   │   └── toast.html                  # Notificaciones (toast)
│   ├── 📂 core/
│   │   ├── alumno_grado_form.html
│   │   ├── base_dashboard.html
│   │   ├── dashboard.html
│   │   ├── user_management.html
│   │   └── 📂 schedule/
│   │       ├── _grid_partial.html      # Componente grid de sesiones
│   │       ├── _grid.html
│   │       ├── asignatura_form.html
│   │       ├── audit.html
│   │       ├── config.html
│   │       ├── crear.html
│   │       ├── curriculum.html
│   │       ├── detalle.html            # Detalle de horario
│   │       ├── disponibilidad.html
│   │       ├── generar.html            # Página de generación
│   │       ├── home.html
│   │       ├── horario_pdf.html
│   │       ├── informes.html
│   │       ├── list.html
│   │       ├── log.html
│   │       ├── mi_horario.html
│   │       ├── notificaciones.html
│   │       ├── restricciones.html
│   │       ├── sesion_form.html
│   │       └── titulacion_detalle.html
│   ├── 📂 login/
│   │   ├── login.html
│   │   ├── 📂 icons/
│   │   ├── 📂 partials/
│   │   │   └── login_form.html
│   │   └── ...
│   └── 📂 theme/
│
├── 📂 static/                          # Archivos estáticos
│   ├── 📂 css/                         # CSS compilado
│   ├── 📂 images/                      # Logos, imágenes
│   └── 📂 js/
│       ├── login.js                    # Lógica de login
│       ├── restricciones.js            # Restricciones drag-drop
│       ├── schedule_detalle.js         # Drag-drop de sesiones ⭐
│       ├── schedule_search.js
│       ├── toast.js                    # Sistema de notificaciones
│       ├── ucjc_search.js
│       ├── user_search.js
│       └── waves.js                    # Animación ripple
│
└── 📚 Documentación
    └── docs/ (opcional)                # Documentación completa
```

---

## ⚙️ Comandos de Gestión

### Migraciones y Base de Datos

```bash
# Mostrar migraciones pendientes
python manage.py showmigrations

# Aplicar todas las migraciones
python manage.py migrate

# Crear nueva migración (después de cambiar models.py)
python manage.py makemigrations

# Ver SQL de una migración sin ejecutarla
python manage.py sqlmigrate core 0001

# Revertir a una migración anterior
python manage.py migrate core 0001
```

### Datos Iniciales (Seeds)

```bash
# Cargar estructura de la Escuela Politécnica
python manage.py seed_politecnica

# Cargar profesores de ejemplo
python manage.py seed_profesores

# Cargar disponibilidades de ejemplo
python manage.py seed_disponibilidad
```

### Usuario Administrador

```bash
# Crear superusuario (admin)
python manage.py createsuperuser

# Cambiar contraseña de usuario
python manage.py changepassword <username>
```

### Tailwind CSS

```bash
# Instalar dependencias de Node (primera vez)
python manage.py tailwind install

# Compilar Tailwind (modo desarrollo)
python manage.py tailwind build

# Compilar en modo watch (se recompila al guardar)
python manage.py tailwind build --watch

# Compilar para producción (minificado)
python manage.py tailwind build --production
```

### Servidor de Desarrollo

```bash
# Ejecutar servidor en localhost:8000
python manage.py runserver

# Ejecutar en puerto específico
python manage.py runserver 0.0.0.0:8080

# Ejecutar con reloader automático
python manage.py runserver --autoreload
```

### Shell de Django

```bash
# Abrir shell Python con Django cargado
python manage.py shell

# Dentro del shell:
from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.all()
print(users)
```

### Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de una app específica
python manage.py test core

# Ejecutar un test específico
python manage.py test core.tests.TestHorario

# Ver cobertura (requiere coverage)
coverage run --source='.' manage.py test
coverage report
```

---

## 🔐 Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# ─── Django ───────────────────────────────────────────────────
DEBUG=True
SECRET_KEY=tu-clave-secreta-super-larga-y-aleatoria
ALLOWED_HOSTS=localhost,127.0.0.1

# ─── Base de Datos ────────────────────────────────────────────
DATABASE_URL=sqlite:///./db.sqlite3
# Alternativa PostgreSQL:
# DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/horaio_ucjc

# ─── Email (para notificaciones) ──────────────────────────────
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app

# ─── OAuth Google (django-allauth) ────────────────────────────
SOCIALACCOUNT_PROVIDERS_GOOGLE_APP_ID=
SOCIALACCOUNT_PROVIDERS_GOOGLE_SECRET=

# ─── OAuth Microsoft (django-allauth) ─────────────────────────
SOCIALACCOUNT_PROVIDERS_MICROSOFT_APP_ID=
SOCIALACCOUNT_PROVIDERS_MICROSOFT_SECRET=

# ─── Seguridad ─────────────────────────────────────────────────
SECURE_SSL_REDIRECT=False          # True en producción
SESSION_COOKIE_SECURE=False        # True en producción
CSRF_COOKIE_SECURE=False           # True en producción

# ─── Timezone ──────────────────────────────────────────────────
TIME_ZONE=Europe/Madrid
LANGUAGE_CODE=es-es

# ─── Configuración de Horarios ────────────────────────────────
# Parámetros del Algoritmo Genético
AG_POPULATION_SIZE=80
AG_MAX_GENERATIONS=250
AG_MUTATION_RATE=0.12
AG_ELITE_SIZE=6
```

---

## 🔄 Flujo de Trabajo del Horario

### Ciclo de Vida de un Horario

```
1. CREACIÓN (Decano)
   └─ Crear nuevo horario para Titulación X, Nivel Y, Curso 2025-2026

2. CONFIGURACIÓN (Decano)
   ├─ Definir franjas horarias disponibles
   ├─ Asignar aulas disponibles
   ├─ Registrar restricciones personalizadas
   └─ Verificar disponibilidad de profesores

3. GENERACIÓN AUTOMÁTICA (AG)
   ├─ Sistema genera 80 cromosomas aleatorios
   ├─ Evalúa fitness de cada uno (restricciones)
   ├─ Selecciona mejores padres
   ├─ Aplica crossover y mutación
   ├─ Itera hasta converger o alcanzar 250 generaciones
   └─ Genera resultado final

4. REVISIÓN (Decano)
   ├─ Ver horario generado
   ├─ Editar manualmente si es necesario (drag-drop)
   ├─ Detectar conflictos
   └─ Validar restricciones

5. APROBACIÓN (Decano)
   ├─ Estado: BORRADOR → REVISION → APROBADO/RECHAZADO
   ├─ Si APROBADO: notificar a profesores y alumnos
   └─ Si RECHAZADO: volver a generar con nuevas restricciones

6. DISTRIBUCIÓN (Sistema)
   ├─ Notificar a profesores (su horario)
   ├─ Notificar a alumnos (su horario)
   └─ Generar reportes y exportar (PDF/Excel)
```

### Cambios de Estado

```
BORRADOR ─────────────────► REVISION ─────────────► APROBADO
   │                            │                        │
   └───────── RECHAZADO ◄───────┴────────────────────────┘
   (volver a generar)
```

---

## 🎯 Funcionalidades de Drag & Drop

El sistema implementa **HTML5 Drag & Drop API nativa** (sin librerías externas).

### Archivo Principal: [static/js/schedule_detalle.js](static/js/schedule_detalle.js)

#### Funcionalidades:

1. **Arrastrar sesión de una celda a otra**
   - Cambiar franja y/o aula
   - Validación de conflictos en tiempo real
   - Revert automático si hay conflicto

2. **Detectar conflictos antes de soltar**
   - Profesor en dos franjas simultáneas
   - Aula ocupada
   - Alumno con clase simultánea

3. **Efecto visual feedback**
   - Resalte de celdas válidas al arrastrar
   - Zona de drop con borde punteado
   - Animación suave

4. **Historial de cambios**
   - Registra cada cambio en auditoría
   - Permite revertir

---

## 📋 Auditoría e Historial

### Modelo: [core/models.py](core/models.py) — `AuditoriaLog`

Cada acción crítica se registra con:
- **Usuario:** Quién realizó la acción
- **Acción:** CREATE, UPDATE, DELETE, APPROVE
- **Modelo:** Qué modelo fue afectado (Horario, Sesion, etc.)
- **Cambios:** JSON con valores anteriores y nuevos
- **Timestamp:** Cuándo ocurrió (con zona horaria)
- **IP Address:** De dónde (opcional)

### Vistas de Auditoría

**Endpoint:** `/schedule/audit/`

Permite al Decanato e IT:
- ✅ Ver log completo de cambios
- ✅ Filtrar por usuario, fecha, modelo
- ✅ Ver valores antes/después
- ✅ Exportar para compliance

**Ejemplo de entrada:**
```json
{
  "usuario": "Admin Decano",
  "accion": "APROBAR",
  "modelo": "Horario",
  "objeto_id": 5,
  "cambios": {
    "old": { "estado": "REVISION" },
    "new": { "estado": "APROBADO" }
  },
  "timestamp": "2025-05-25T14:30:45.123Z",
  "ip_address": "192.168.1.100"
}
```

---

## 🚀 Ejecución del Servidor

### Modo Desarrollo

```bash
# 1. Activar entorno virtual
.venv\Scripts\activate              # Windows
# source .venv/bin/activate         # Linux/macOS

# 2. Ejecutar servidor (auto-reload)
python manage.py runserver

# 3. Acceder en navegador
# http://localhost:8000
```

### Modo Producción

```bash
# 1. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 2. Compilar Tailwind para producción
python manage.py tailwind build --production

# 3. Ejecutar con gunicorn
gunicorn HorarioUCJC.wsgi:application --bind 0.0.0.0:8000

# O con honcho (Procfile)
honcho start
```

---

## 📞 Contacto y Soporte

- **Equipo de Desarrollo:** [correo-equipo]
- **Repositorio:** [URL del repositorio]
- **Issues y Bugs:** Usar el sistema de issues del repositorio
- **Documentación Completa:** Ver [REQUISITOS.txt](REQUISITOS.txt)

---

## 📄 Licencia

[Especificar licencia si aplica]

---

## 🎓 Créditos

Desarrollado para la **Escuela Politécnica de la Universidad Camilo José Cela (UCJC)**.

Sistema de generación automática de horarios académicos basado en Algoritmo Genético.

## Variables de entorno (.env)

Crea un fichero `.env` en la raíz del proyecto (nunca lo subas al repositorio):

```env
# Clave secreta de Django (cambia esto en producción)
SECRET_KEY=tu-clave-secreta-aqui

# Google OAuth (https://console.cloud.google.com/)
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-tu-client-secret

# Microsoft OAuth (opcional)
MICROSOFT_CLIENT_ID=tu-microsoft-client-id
MICROSOFT_CLIENT_SECRET=tu-microsoft-client-secret
```

El fichero `HorarioUCJC/settings.py` carga estas variables usando `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()

GOOGLE_CLIENT_ID     = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
SECRET_KEY           = os.getenv('SECRET_KEY', 'dev-insecure-key')
```

> **Importante:** Nunca hardcodear credenciales en el código. Usar siempre `.env`.

---

## Comandos de gestión

```bash
# Poblar datos de prueba de la Escuela Politécnica
python manage.py seed_politecnica

# Crear perfiles de profesores de prueba
python manage.py seed_profesores

# Compilar Tailwind en modo watch (desarrollo)
python manage.py tailwind start

# Compilar Tailwind para producción
python manage.py tailwind build
```

---

## Flujo de trabajo del horario

```
Crear horario (BORRADOR)
        │
        ▼
Hoja de restricciones ← Nueva: revisa RD-01..RD-18 antes de generar
        │
        ▼
Configurar generación (días, horas, duración de sesión)
        │
        ▼
Generar (Algoritmo Genético) → Vista de log con análisis por asignatura
        │
        ▼
Editar manualmente (arrastrar sesiones o añadir/eliminar)
        │
        ▼
Enviar a REVISIÓN
        │
        ├── APROBAR → Notificar profesores
        └── RECHAZAR (con motivo) → Volver a BORRADOR
```

---

## Endpoints principales

### Horarios (Decano)
| URL | Descripción |
|-----|-------------|
| `GET /schedule/horarios/` | Lista de horarios con filtros |
| `GET/POST /schedule/horarios/crear/` | Crear nuevo horario |
| `GET /schedule/horarios/<pk>/` | Detalle + cuadrícula drag-and-drop |
| `GET /schedule/horarios/<pk>/restricciones/` | **Hoja de restricciones** (nuevo) |
| `GET/POST /schedule/horarios/<pk>/generar/` | Configurar y ejecutar el AG |
| `POST /schedule/horarios/<pk>/workflow/` | Cambiar estado (revisión/aprobar/rechazar) |
| `GET /schedule/horarios/<pk>/log/` | Log de auditoría + análisis |

### Sesiones
| URL | Descripción |
|-----|-------------|
| `POST /schedule/sesiones/<pk>/mover/` | **Mover sesión** (drag-and-drop, AJAX) |
| `POST /schedule/sesiones/<pk>/eliminar/` | Eliminar sesión |
| `GET/POST /schedule/horarios/<pk>/sesion/crear/` | Añadir sesión manual |

### Gestión de usuarios (Decano)
| URL | Descripción |
|-----|-------------|
| `GET /dashboard/usuarios/` | Lista de usuarios |
| `POST /dashboard/usuarios/<pk>/rol/` | Cambiar rol |
| `GET/POST /dashboard/usuarios/<pk>/grado/` | **Asignar titulación al alumno** (nuevo) |

### Profesor
| URL | Descripción |
|-----|-------------|
| `GET/POST /schedule/disponibilidad/` | Registrar disponibilidad horaria |
| `GET /schedule/mi-horario/` | Ver horario personal aprobado |

---

## Modificación drag-and-drop

En la vista de detalle del horario (`/schedule/horarios/<pk>/`), cuando el estado es **BORRADOR**:

1. **Arrastrar** una tarjeta de sesión desde su posición actual.
2. **Soltar** sobre una celda vacía o sobre otro slot del horario.
3. El sistema valida automáticamente:
   - RD-05: Sin conflicto de profesor
   - RD-12: Sin conflicto de aula
   - RD-08: Sin conflicto de semestre en la misma franja
   - RD-14: Sin repetición del mismo día para la asignatura
4. Si la validación pasa, la sesión se mueve y se registra en el log de auditoría.
5. Si falla, aparece un toast con el motivo del conflicto.

**Identificación visual de semestres:**
- Borde y fondo **azul** → Semestre 1
- Borde y fondo **morado** → Semestre 2
- Badge `S1` / `S2` en cada tarjeta

---

## Estructura del proyecto

```
HorarioUCJC/
├── HorarioUCJC/            # Configuración Django
│   ├── settings.py         # Lee SECRET_KEY, Google OAuth desde .env
│   └── urls.py
├── core/                   # Modelos académicos
│   ├── models.py
│   ├── views.py            # Dashboard + gestión de alumnos
│   ├── forms.py            # AlumnoGradoForm
│   └── management/commands/
│       ├── seed_politecnica.py
│       └── seed_profesores.py
├── schedule/               # Motor de horarios
│   ├── generator.py        # Algoritmo Genético
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── audit.py
├── login/                  # Autenticación
│   ├── models.py           # Usuario, PerfilAlumno, PerfilProfesor...
│   ├── views.py
│   └── middleware.py
├── templates/
│   ├── core/
│   │   ├── schedule/
│   │   │   ├── detalle.html       # Cuadrícula drag-and-drop + badges semestre
│   │   │   ├── restricciones.html # Hoja de restricciones (nuevo)
│   │   │   ├── generar.html       # Wizard de configuración (paso 3/4)
│   │   │   └── ...
│   │   ├── alumno_grado_form.html # Asignar grado a alumno (nuevo)
│   │   └── user_management.html
│   └── login/login.html
├── .env                    # Variables de entorno (NO subir al repo)
├── .env.example            # Plantilla de variables de entorno
├── requirements.txt
└── README.md               # Este fichero
```

---

## Tecnologías utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Django | 5.2 | Framework web principal |
| django-allauth | latest | OAuth Google/Microsoft |
| django-tailwind | latest | Compilación Tailwind CSS |
| django-htmx | latest | Interacciones AJAX ligeras |
| Tailwind CSS | 3.x | Diseño UI (dark theme zinc) |
| HTML5 Drag & Drop API | nativa | Modificación de horarios |
| Algoritmo Genético | puro Python | Motor de generación |
| SQLite3 | — | Base de datos (dev) |

> El Algoritmo Genético está implementado en puro Python sin dependencias externas de ML/DL, lo que evita añadir pesos pesados como NumPy o scikit-learn para este caso de uso.

---

## Licencia

Proyecto de uso interno para la Universidad Camilo José Cela — Escuela Politécnica.
