# HorarioUCJC — Sistema de Gestión de Horarios

Sistema web de planificación y gestión de horarios académicos para la **Escuela Politécnica de la Universidad Camilo José Cela (UCJC)**. Desarrollado con **Django 5.2**, Tailwind CSS y un motor de generación basado en **Algoritmo Genético**.

---

## Índice

1. [Descripción del proyecto](#descripción-del-proyecto)
2. [Arquitectura](#arquitectura)
3. [Roles y permisos](#roles-y-permisos)
4. [Motor de generación — Algoritmo Genético](#motor-de-generación--algoritmo-genético)
5. [Restricciones del sistema](#restricciones-del-sistema)
6. [Instalación y configuración](#instalación-y-configuración)
7. [Variables de entorno (.env)](#variables-de-entorno-env)
8. [Comandos de gestión](#comandos-de-gestión)
9. [Flujo de trabajo del horario](#flujo-de-trabajo-del-horario)
10. [Endpoints principales](#endpoints-principales)
11. [Modificación drag-and-drop](#modificación-drag-and-drop)
12. [Estructura del proyecto](#estructura-del-proyecto)

---

## Descripción del proyecto

HorarioUCJC permite al **Decanato** planificar automáticamente los horarios de cada titulación y nivel, teniendo en cuenta:

- Disponibilidad de aulas y profesores
- Restricciones académicas (sesiones por semana, turno tarde/mañana, semestres)
- Workflow de aprobación (Borrador → Revisión → Aprobado/Rechazado)
- Notificaciones in-app para profesores y alumnos
- Auditoría inmutable de todos los cambios

---

## Arquitectura

El proyecto sigue una arquitectura de apps Django bien separadas:

```
HorarioUCJC/          # Configuración principal del proyecto
core/                 # Modelos académicos + dashboard
  models.py           # Titulacion, Asignatura, Horario, Sesion, FranjaHoraria, Aula...
  views.py            # Dashboard, gestión de usuarios, gestión de grado de alumnos
  forms.py            # AlumnoGradoForm
login/                # Autenticación y perfiles de usuario
  models.py           # Usuario (AbstractUser), PerfilDecano, PerfilProfesor, PerfilAlumno
  views.py            # Login email/contraseña
  middleware.py       # LoginRequiredMiddleware
schedule/             # Lógica de horarios
  generator.py        # Motor de generación — Algoritmo Genético
  views.py            # Todas las vistas de horarios (33+ funciones)
  forms.py            # Formularios de horarios
  urls.py             # Rutas /schedule/
  audit.py            # Sistema de auditoría
theme/                # Configuración de Tailwind CSS
templates/            # Plantillas HTML (Tailwind, dark zinc theme)
```

**Base de datos:** SQLite3 (fácilmente migrable a PostgreSQL).

**Frontend:** Tailwind CSS (dark theme zinc-800/700, acento red-600), HTMX, HTML5 Drag & Drop API nativa.

---

## Roles y permisos

| Rol | Descripción | Permisos principales |
|-----|-------------|---------------------|
| **DECANO** | Dirección / Decanato | Crear/editar/aprobar horarios, gestionar usuarios, asignar grados a alumnos |
| **PROFESOR** | Docente | Ver su horario, registrar disponibilidad |
| **ALUMNO** | Estudiante | Ver su horario, detectar conflictos |
| **IT** | Soporte técnico | Acceso de solo lectura al sistema |

---

## Motor de generación — Algoritmo Genético

El fichero `schedule/generator.py` implementa un **Algoritmo Genético (AG)** que reemplaza el anterior algoritmo greedy CSP.

### Representación del cromosoma

Cada individuo es una lista de genes `(franja_pk, aula_pk)`, donde la posición `j` corresponde a la sesión `j` de la lista ordenada de todas las sesiones requeridas:

```
slots_to_fill = [(asig_id_1, 0), (asig_id_1, 1), (asig_id_2, 0), ...]
chromosome[j] = (franja_pk, aula_pk)
```

Un cromosoma completo representa **una asignación completa** de todas las sesiones del horario.

### Función de fitness (minimizar)

| Restricción | Penalización |
|-------------|-------------|
| RD-05: Profesor en dos franjas simultáneas | 1000 × repeticiones |
| RD-12: Aula con dos sesiones simultáneas | 1000 × repeticiones |
| RD-08 estudiantes: Misma franja, mismo semestre | 800 |
| RD-14: Asignatura repetida el mismo día | 300 |
| RD-08 profesor: Franja bloqueada (INDISPONIBLE) | 600 |
| RD-01: Sesión faltante (sin asignar) | 1500 |
| Soft: Franja preferida por el profesor (recompensa) | −60 |
| Soft: Dispersión días (RD-13) | 25 × span de días |

### Parámetros del AG

| Parámetro | Valor |
|-----------|-------|
| Tamaño de población | 80 individuos |
| Máximo de generaciones | 250 |
| Tasa de mutación | 12% |
| Élite (preservada) | 6 individuos |
| Selección por torneo | 5 candidatos |
| Parada por estancamiento | 40 generaciones sin mejora |

### Detección de disponibilidad por solapamiento

A diferencia del sistema anterior (que solo comparaba la hora de inicio), el nuevo sistema detecta solapamiento real entre la franja horaria del profesor (INDISPONIBLE/PREFERENTE) y cada `FranjaHoraria`:

```python
def _franja_overlaps_range(franja, dia, hora_ini, hora_fin):
    """True si franja.hora_inicio < hora_fin AND franja.hora_fin > hora_ini"""
    if franja.dia_semana != dia:
        return False
    return franja.hora_inicio < hora_fin and franja.hora_fin > hora_ini
```

Esto garantiza que si un profesor está bloqueado de 15:00 a 17:00, cualquier franja que solape ese rango (p.ej., 15:30–17:30, 14:00–16:00) queda excluida.

---

## Restricciones del sistema

### Hard constraints (RD)

| Código | Descripción |
|--------|-------------|
| RD-01 | Cada asignatura se imparte `sesiones_semanales` veces por semana |
| RD-05 | Ningún profesor imparte dos asignaturas en la misma franja |
| RD-07 | Cada asignatura tiene un único profesor titular |
| RD-08 | Las clases respetan las franjas disponibles del profesor (por solapamiento) |
| RD-08 | Los alumnos del mismo semestre no tienen dos asignaturas en la misma franja |
| RD-10 | Asignaturas transversales usan el mismo slot en todas las titulaciones vinculadas |
| RD-12 | Un aula no alberga dos clases simultáneamente |
| RD-14 | Una asignatura no se repite el mismo día |
| RD-17 | Solo se usan franjas activas predefinidas |
| RD-18 | Grados individuales: turno tarde (salvo último año si el grado lo permite) |

### Soft constraints

| Código | Descripción |
|--------|-------------|
| RD-13 | Sesiones de la misma asignatura en días distintos (compacidad) |
| — | Preferir franjas marcadas como PREFERENTE por el profesor |

---

## Instalación y configuración

### Requisitos

- Python 3.11+
- Node.js 18+ (para compilar Tailwind CSS)

### Pasos

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd HorarioUCJC

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Google OAuth

# 5. Migraciones
python manage.py migrate

# 6. Datos de prueba (opcional)
python manage.py seed_politecnica
python manage.py seed_profesores

# 7. Compilar Tailwind CSS
python manage.py tailwind install
python manage.py tailwind build

# 8. Servidor de desarrollo
python manage.py runserver
```

---

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
