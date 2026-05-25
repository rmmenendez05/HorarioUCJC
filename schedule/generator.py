"""
Motor de generación automática de horarios — Algoritmo Genético (AG).

Restricciones hard (penalizadas en fitness)
───────────────────────────────────────────
RD-01  Cada asignatura se imparte en sesiones_semanales sesiones de duracion_sesion_h horas.
RD-05  Ningún profesor imparte dos asignaturas al mismo tiempo.
RD-07  Cada asignatura tiene un único profesor titular.
RD-08  (profesores) Clases solo en franjas disponibles del profesor.
       La detección usa solapamiento de rangos horarios, no igualdad exacta de inicio.
RD-08  (estudiantes) Un alumno del mismo semestre no puede tener dos asignaturas solapadas.
RD-10  Asignaturas transversales → mismo slot en todas las titulaciones vinculadas.
RD-12  No puede haber dos sesiones en el mismo aula y franja.
RD-14  Una misma asignatura no puede repetirse el mismo día.
RD-17  Sólo franjas activas predefinidas.
RD-18  Grados individuales → sólo turno TARDE (salvo último año si el grado lo permite).

Soft constraints (rewards negativos en fitness)
────────────────────────────────────────────────
RD-13  Preferir sesiones compactas / dispersas en días distintos para el mismo curso.
       Preferencias del profesor (PREFERENTE) se recompensan.
"""
import random
from collections import defaultdict

from core.models import (
    Sesion, AsignaturaTitulacion,
    FranjaHoraria, AsignacionProfesor, DisponibilidadProfesor, Aula,
    RestriccionPersonalizada,
)

# ── Parámetros del Algoritmo Genético ────────────────────────────────────────
GA_POPULATION_SIZE  = 80
GA_MAX_GENERATIONS  = 250
GA_MUTATION_RATE    = 0.12
GA_ELITE_SIZE       = 6
GA_TOURNAMENT_SIZE  = 5
GA_STAGNATION_LIMIT = 40

# Pesos de penalización para la función de fitness (menor = mejor)
PENALTY_PROF_CONFLICT     = 1000
PENALTY_ROOM_CONFLICT     = 1000
PENALTY_STUDENT_CONFLICT  = 800
PENALTY_SAME_DAY          = 300
PENALTY_UNAVAILABLE       = 600
PENALTY_MISSING_SESSION   = 1500
REWARD_PREFERRED          = -60   # negativo = recompensa
PENALTY_DAY_SPAN          = 25    # dispersión entre sesiones de la misma asignatura
PENALTY_CUSTOM_BLOCKED    = 850   # franja bloqueada por restricción personalizada
PENALTY_CUSTOM_DIA_EXCL   = 700   # asignatura excluida de un día
REWARD_CUSTOM_DIA_PREF    = -50   # día preferido por restricción personalizada


# ── Punto de entrada ─────────────────────────────────────────────────────────

def generate(horario, franjas_override=None):
    """
    Genera las sesiones para *horario* usando un Algoritmo Genético.
    franjas_override: lista de FranjaHoraria a usar (viene del wizard).
    Devuelve (n_sesiones_creadas: int, errores: list[str]).
    """
    Sesion.objects.filter(horario=horario).delete()

    at_qs = list(
        AsignaturaTitulacion.objects
        .filter(titulacion=horario.titulacion, nivel=horario.nivel)
        .select_related('asignatura', 'titulacion', 'nivel')
        .order_by('asignatura__semestre', 'asignatura__codigo')
    )
    if not at_qs:
        return 0, ["No hay asignaturas en el plan de estudios para este nivel."]

    # Franjas candidatas
    if franjas_override is not None:
        franjas_todas = list(franjas_override)
    else:
        qs = FranjaHoraria.objects.filter(activa=True)
        if not horario.nivel.es_ultimo or not horario.titulacion.permite_maniana:
            qs = qs.filter(turno='TARDE')
        franjas_todas = list(qs.order_by('dia_semana', 'hora_inicio'))

    if not franjas_todas:
        return 0, ["No hay franjas horarias disponibles para la generación."]

    aulas_todas = list(Aula.objects.filter(activa=True))
    if not aulas_todas:
        return 0, ["No hay aulas activas para la generación."]

    # Construir info por asignatura
    asig_info = {}
    errores_prev = []
    for at in at_qs:
        asig = at.asignatura
        asignacion = (
            AsignacionProfesor.objects
            .filter(
                asignatura=asig,
                curso_academico=horario.curso_academico,
                tipo='TITULAR',
            )
            .select_related('profesor__usuario')
            .first()
        )
        if not asignacion:
            errores_prev.append(f"Sin profesor titular para «{asig.nombre}»")
            continue

        profesor = asignacion.profesor
        bloqueadas  = _franjas_bloqueadas_overlap(profesor, horario.curso_academico, franjas_todas, semestre_asig=asig.semestre)
        preferentes = _franjas_preferentes_overlap(profesor, horario.curso_academico, franjas_todas)

        franjas_candidatas = [f for f in franjas_todas if f.pk not in bloqueadas]
        if not franjas_candidatas:
            franjas_candidatas = list(franjas_todas)  # fallback si todo bloqueado

        asig_info[asig.pk] = {
            'asig':              asig,
            'profesor':          profesor,
            'bloqueadas':        bloqueadas,
            'preferentes':       preferentes,
            'franjas_candidatas': franjas_candidatas,
            'sesiones_needed':   asig.sesiones_semanales,
        }

    if not asig_info:
        return 0, errores_prev + ["No hay asignaturas con profesores asignados."]

    # Cargar restricciones personalizadas del decano
    restr_qs = RestriccionPersonalizada.objects.filter(horario=horario, activa=True)
    custom_franjas_bloqueadas = set(
        r.franja_id for r in restr_qs if r.tipo == 'FRANJA_BLOQUEADA' and r.franja_id
    )
    custom_asig_dia_excl = {}   # asig_id → set(dia_semana)
    custom_asig_dia_pref = {}   # asig_id → set(dia_semana)
    for r in restr_qs:
        if r.tipo == 'ASIG_DIA_EXCLUIDO' and r.asignatura_id and r.dia_semana is not None:
            custom_asig_dia_excl.setdefault(r.asignatura_id, set()).add(r.dia_semana)
        elif r.tipo == 'ASIG_DIA_PREFERIDO' and r.asignatura_id and r.dia_semana is not None:
            custom_asig_dia_pref.setdefault(r.asignatura_id, set()).add(r.dia_semana)

    # Correr el Algoritmo Genético
    best_chrom, franja_by_pk, aula_by_pk, slots_to_fill = _run_ga(
        asig_info=asig_info,
        franjas_todas=franjas_todas,
        aulas_todas=aulas_todas,
        horario=horario,
        custom_franjas_bloqueadas=custom_franjas_bloqueadas,
        custom_asig_dia_excl=custom_asig_dia_excl,
        custom_asig_dia_pref=custom_asig_dia_pref,
    )

    # Crear objetos Sesion a partir del mejor cromosoma
    n_creadas = 0
    errores    = list(errores_prev)
    asig_sesions_count = defaultdict(int)

    for j, (asig_id, session_idx) in enumerate(slots_to_fill):
        franja_pk, aula_pk = best_chrom[j]
        info    = asig_info[asig_id]
        franja  = franja_by_pk.get(franja_pk)
        aula    = aula_by_pk.get(aula_pk)

        if franja is None or aula is None:
            continue

        try:
            Sesion.objects.create(
                horario=horario,
                asignatura=info['asig'],
                profesor=info['profesor'],
                aula=aula,
                franja=franja,
                grupo=f"S{session_idx + 1}",
            )
            n_creadas += 1
            asig_sesions_count[asig_id] += 1
        except Exception:
            pass

    for asig_id, info in asig_info.items():
        asignadas  = asig_sesions_count.get(asig_id, 0)
        requeridas = info['sesiones_needed']
        if asignadas < requeridas:
            errores.append(
                f"«{info['asig'].nombre}»: {asignadas}/{requeridas} "
                f"sesiones asignadas (restricciones insuficientes)"
            )

    return n_creadas, errores


# ── Algoritmo Genético ────────────────────────────────────────────────────────

def _run_ga(asig_info, franjas_todas, aulas_todas, horario,
            custom_franjas_bloqueadas=None, custom_asig_dia_excl=None, custom_asig_dia_pref=None):
    """
    Ejecuta el AG y devuelve (best_chrom, franja_by_pk, aula_by_pk, slots_to_fill).

    Representación del cromosoma:
      - Lista de (franja_pk, aula_pk) de longitud = total sesiones requeridas.
      - La posición j corresponde a slots_to_fill[j] = (asig_id, session_idx).
    """
    custom_franjas_bloqueadas = custom_franjas_bloqueadas or set()
    custom_asig_dia_excl      = custom_asig_dia_excl or {}
    custom_asig_dia_pref      = custom_asig_dia_pref or {}

    franja_by_pk = {f.pk: f for f in franjas_todas}
    aula_by_pk   = {a.pk: a for a in aulas_todas}
    franja_pks   = [f.pk for f in franjas_todas]
    aula_pks     = [a.pk for a in aulas_todas]

    # Slots a rellenar (uno por sesión requerida)
    slots_to_fill = []
    for asig_id in sorted(asig_info.keys()):
        for i in range(asig_info[asig_id]['sesiones_needed']):
            slots_to_fill.append((asig_id, i))
    n_slots = len(slots_to_fill)

    # Pre-cargar conflictos cross-horario del curso académico.
    # Clave: (prof_id, franja_id, semestre) — dos sesiones del mismo profesor en la
    # misma franja NO son conflicto si pertenecen a semestres distintos (S1 y S2
    # transcurren en periodos diferentes del año académico).
    existing_prof_franjas = set(
        Sesion.objects.filter(horario__curso_academico=horario.curso_academico)
        .exclude(horario=horario)
        .values_list('profesor_id', 'franja_id', 'asignatura__semestre')
    )
    existing_aula_franjas = set(
        Sesion.objects.filter(horario__curso_academico=horario.curso_academico)
        .exclude(horario=horario)
        .values_list('aula_id', 'franja_id')
    )

    # Franjas válidas por asignatura (sin bloqueos de prof, sin cross-horario)
    valid_fpks = {}
    for asig_id, info in asig_info.items():
        prof_id = info['profesor'].pk
        cands = [
            f.pk for f in info['franjas_candidatas']
            if (prof_id, f.pk) not in existing_prof_franjas
        ]
        valid_fpks[asig_id] = cands if cands else franja_pks

    # ── Funciones del AG ─────────────────────────────────────────────────────

    def make_random_chrom():
        return [
            (random.choice(valid_fpks[asig_id]), random.choice(aula_pks))
            for asig_id, _ in slots_to_fill
        ]

    def fitness(chrom):
        penalty = 0
        prof_franja_seen   = {}   # (prof_id, fpk) -> count
        aula_franja_seen   = {}   # (aula_pk, fpk) -> count
        sem_franja_asigs   = {}   # (sem, fpk) -> set of asig_ids
        asig_days_seen     = {}   # asig_id -> set of dia_semana
        asig_count         = {}   # asig_id -> int

        for j, (asig_id, _) in enumerate(slots_to_fill):
            fpk, aula_pk = chrom[j]
            info   = asig_info[asig_id]
            franja = franja_by_pk.get(fpk)
            if franja is None:
                penalty += PENALTY_MISSING_SESSION
                continue

            prof_id = info['profesor'].pk
            sem     = info['asig'].semestre
            asig_count[asig_id] = asig_count.get(asig_id, 0) + 1

            # RD-05: conflicto de profesor (dentro del horario).
            # Solo cuenta si hay otra sesión del MISMO semestre — un profesor puede
            # tener S1 y S2 en la misma franja porque transcurren en periodos distintos.
            pk5 = (prof_id, fpk, sem)
            cnt5 = prof_franja_seen.get(pk5, 0)
            if cnt5 > 0:
                penalty += PENALTY_PROF_CONFLICT * cnt5
            prof_franja_seen[pk5] = cnt5 + 1

            # RD-05: conflicto cross-horario (mismo semestre)
            if (prof_id, fpk, sem) in existing_prof_franjas:
                penalty += PENALTY_PROF_CONFLICT

            # RD-12: conflicto de aula (dentro del horario)
            pk12 = (aula_pk, fpk)
            cnt12 = aula_franja_seen.get(pk12, 0)
            if cnt12 > 0:
                penalty += PENALTY_ROOM_CONFLICT * cnt12
            aula_franja_seen[pk12] = cnt12 + 1

            # RD-12: conflicto cross-horario
            if (aula_pk, fpk) in existing_aula_franjas:
                penalty += PENALTY_ROOM_CONFLICT

            # RD-08 estudiantes: misma franja, mismo semestre
            sk = (sem, fpk)
            sem_set = sem_franja_asigs.get(sk)
            if sem_set is None:
                sem_franja_asigs[sk] = {asig_id}
            elif asig_id not in sem_set:
                penalty += PENALTY_STUDENT_CONFLICT
                sem_set.add(asig_id)

            # RD-14: misma asignatura, mismo día
            days = asig_days_seen.get(asig_id)
            if days is None:
                asig_days_seen[asig_id] = {franja.dia_semana}
            elif franja.dia_semana in days:
                penalty += PENALTY_SAME_DAY
            else:
                days.add(franja.dia_semana)

            # RD-08 profesor: franja bloqueada
            if fpk in info['bloqueadas']:
                penalty += PENALTY_UNAVAILABLE

            # Soft: franja preferida por el profesor
            if fpk in info['preferentes']:
                penalty += REWARD_PREFERRED

            # Restricciones personalizadas del decano
            if fpk in custom_franjas_bloqueadas:
                penalty += PENALTY_CUSTOM_BLOCKED
            excl_dias = custom_asig_dia_excl.get(asig_id)
            if excl_dias and franja.dia_semana in excl_dias:
                penalty += PENALTY_CUSTOM_DIA_EXCL
            pref_dias = custom_asig_dia_pref.get(asig_id)
            if pref_dias and franja.dia_semana in pref_dias:
                penalty += REWARD_CUSTOM_DIA_PREF

        # RD-01: sesiones faltantes
        for asig_id, info in asig_info.items():
            deficit = info['sesiones_needed'] - asig_count.get(asig_id, 0)
            if deficit > 0:
                penalty += deficit * PENALTY_MISSING_SESSION

        # Soft: compacidad (RD-13) — días distintos por asignatura
        for asig_id, days in asig_days_seen.items():
            if len(days) > 1:
                penalty += (max(days) - min(days)) * PENALTY_DAY_SPAN

        return penalty

    def tournament_select(pop, scores):
        candidates = random.sample(range(len(pop)), min(GA_TOURNAMENT_SIZE, len(pop)))
        best_i = min(candidates, key=lambda i: scores[i])
        return pop[best_i][:]

    def crossover(p1, p2):
        if n_slots < 2:
            return p1[:], p2[:]
        pt = random.randint(1, n_slots - 1)
        return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]

    def mutate(chrom):
        for j, (asig_id, _) in enumerate(slots_to_fill):
            if random.random() < GA_MUTATION_RATE:
                fpk    = random.choice(valid_fpks[asig_id])
                aula_pk = random.choice(aula_pks)
                chrom[j] = (fpk, aula_pk)
        return chrom

    # ── Bucle evolutivo ──────────────────────────────────────────────────────
    population = [make_random_chrom() for _ in range(GA_POPULATION_SIZE)]
    scores     = [fitness(c) for c in population]

    best_score = min(scores)
    best_chrom = population[scores.index(best_score)][:]
    stagnation = 0

    for _ in range(GA_MAX_GENERATIONS):
        if best_score == 0:
            break   # solución perfecta

        sorted_idx  = sorted(range(len(population)), key=lambda i: scores[i])
        new_pop     = [population[i][:] for i in sorted_idx[:GA_ELITE_SIZE]]

        while len(new_pop) < GA_POPULATION_SIZE:
            p1  = tournament_select(population, scores)
            p2  = tournament_select(population, scores)
            c1, c2 = crossover(p1, p2)
            new_pop.append(mutate(c1))
            if len(new_pop) < GA_POPULATION_SIZE:
                new_pop.append(mutate(c2))

        population = new_pop
        scores     = [fitness(c) for c in population]
        gen_best   = min(scores)

        if gen_best < best_score:
            best_score = gen_best
            best_chrom = population[scores.index(gen_best)][:]
            stagnation = 0
        else:
            stagnation += 1

        if stagnation >= GA_STAGNATION_LIMIT:
            break

    return best_chrom, franja_by_pk, aula_by_pk, slots_to_fill


# ── Helpers de disponibilidad con solapamiento de rangos ─────────────────────

def _franja_overlaps_range(franja, dia, hora_ini, hora_fin):
    """True si la franja se solapa con [hora_ini, hora_fin) en el mismo día."""
    if franja.dia_semana != dia:
        return False
    return franja.hora_inicio < hora_fin and franja.hora_fin > hora_ini


def _franjas_bloqueadas_overlap(profesor, curso_academico, franjas_todas, semestre_asig=None):
    """
    PKs de franjas que solapan con rangos INDISPONIBLES del profesor.
    Si se pasa semestre_asig, aplica la excepción T1/S2: las restricciones
    exclusivas de T1 no bloquean asignaturas del segundo semestre.
    """
    bloqueos = DisponibilidadProfesor.objects.filter(
        profesor=profesor,
        curso_academico=curso_academico,
        tipo='INDISPONIBLE',
    )
    bloqueadas = set()
    for b in bloqueos:
        if semestre_asig is not None and not b.aplica_a_semestre(semestre_asig):
            continue
        for f in franjas_todas:
            if _franja_overlaps_range(f, b.dia_semana, b.hora_inicio, b.hora_fin):
                bloqueadas.add(f.pk)
    return bloqueadas


def _franjas_preferentes_overlap(profesor, curso_academico, franjas_todas):
    """PKs de franjas que solapan con rangos PREFERENTES del profesor."""
    prefs = DisponibilidadProfesor.objects.filter(
        profesor=profesor,
        curso_academico=curso_academico,
        tipo='PREFERENTE',
    )
    preferentes = set()
    for p in prefs:
        for f in franjas_todas:
            if _franja_overlaps_range(f, p.dia_semana, p.hora_inicio, p.hora_fin):
                preferentes.add(f.pk)
    return preferentes


# ── Validación post-generación (RF-02.1) ─────────────────────────────────────

def validate_horario(horario):
    """
    Valida que el horario cumple las horas lectivas y no tiene conflictos.
    Devuelve lista de errores (vacía = OK).
    """
    errores  = []
    sesiones = list(
        Sesion.objects.filter(horario=horario)
        .select_related('asignatura', 'profesor', 'franja', 'aula')
    )

    # RF-02.1: horas asignadas vs. requeridas
    sesiones_por_asig = defaultdict(int)
    for s in sesiones:
        sesiones_por_asig[s.asignatura_id] += 1

    for at in AsignaturaTitulacion.objects.filter(
        titulacion=horario.titulacion, nivel=horario.nivel,
    ).select_related('asignatura'):
        a         = at.asignatura
        reales    = sesiones_por_asig.get(a.id, 0)
        requeridas = a.sesiones_semanales
        if reales < requeridas:
            errores.append(
                f"«{a.nombre}»: {reales}/{requeridas} sesiones semanales asignadas"
            )

    # RD-05: solapamiento de profesor — solo conflicto si son del mismo semestre
    prof_franja = defaultdict(list)
    for s in sesiones:
        prof_franja[(s.profesor_id, s.franja_id, s.asignatura.semestre)].append(s.pk)
    for _, ids in prof_franja.items():
        if len(ids) > 1:
            errores.append(f"Conflicto RD-05: profesor con {len(ids)} sesiones en la misma franja")

    # RD-08 estudiantes: solapamiento dentro del mismo semestre
    franja_sem = defaultdict(list)
    for s in sesiones:
        franja_sem[(s.franja_id, s.asignatura.semestre)].append(s.asignatura.nombre)
    for (fid, sem), asigs in franja_sem.items():
        if len(asigs) > 1:
            errores.append(
                f"Conflicto RD-08 (sem{sem}): {len(asigs)} asignaturas simultáneas "
                f"({', '.join(asigs[:2])}…)"
            )

    # RD-12: solapamiento de aula
    aula_franja = defaultdict(list)
    for s in sesiones:
        aula_franja[(s.aula_id, s.franja_id)].append(s.pk)
    for _, ids in aula_franja.items():
        if len(ids) > 1:
            errores.append(f"Conflicto RD-12: aula con {len(ids)} sesiones en la misma franja")

    return errores
