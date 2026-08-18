# Premio UNITEC 2026 — Puntos clave para la postulación

> Documento de referencia rápida para preparar la postulación de **Taller Seguro Vision** al Premio UNITEC a la Innovación Tecnológica para el Desarrollo Social 2026. Complementa el análisis de probabilidad hecho fuera de este repo; aquí solo viven los datos verificables de la convocatoria y su cruce con el estado real del proyecto tras el PR #1 (pivote a MVP de EPP en Raspberry Pi + webcam).
>
> Fuente primaria: [Convocatoria oficial (PDF)](https://www.unitec.mx/hubfs/01.UNITEC/pdfs/2026/03/Convocatoria_Premio_Unitec_2026.pdf) · [unitec.mx/premio](https://www.unitec.mx/premio/). El PDF no es accesible por herramientas automatizadas de este entorno (bloqueo de red) — los datos aquí vienen de fuentes secundarias verificadas por búsqueda web; si algo cambió en la versión oficial, esta tabla queda subordinada al PDF.

## 1. Qué es y quién puede participar

- Nombre oficial: **Premio UNITEC a la Innovación Tecnológica para el Desarrollo Social 2026**.
- Elegibilidad: 18–29 años, fundador o cofundador del proyecto (debe tener los derechos de la innovación), individual o en equipo.
- No aplica si ya ganaste una edición anterior del Premio UNITEC, o si fuiste declarado ganador en convocatorias de International Youth Foundation (IYF) o Laureate International Universities.
- No es exclusivo de estudiantes UNITEC — ediciones pasadas premiaron a fundadores de otras instituciones (ej. Universidad de Chapingo, ITESM).

## 2. Categorías y premios

| Categoría | Requisito de madurez | Premio | Ganadores |
|---|---|---|---|
| **Prototipo** | Solución tecnológica funcional + validación inicial (no requiere usuarios reales en producción) | $30,000 MXN c/u | 3 |
| **Proyecto** | Emprendimiento en operación o implementación con usuarios reales | $100,000 MXN c/u | 3 |

## 3. Fechas críticas

| Hito | Fecha |
|---|---|
| Cierre de registro | **23 de agosto de 2026, 23:59 h (CDMX)** |
| Comunicación de resultados | Septiembre de 2026 |
| Presentación final de semifinalistas | Previa a la ceremonia |
| Ceremonia de premiación + capacitación | 3–9 de octubre de 2026, CDMX |
| Plataforma de registro | https://premiounitec.charly.io/spar/programs/PremioUNITEC26 |

Proceso: registro abierto → comité evalúa → **6 semifinalistas por categoría** → presentación final → **3 ganadores por categoría**.

## 4. Criterios de evaluación oficiales

1. Innovación tecnológica
2. Impacto social
3. Viabilidad del modelo de negocio
4. Escalabilidad
5. Claridad del problema que atienden

(No hay ponderación pública por criterio — se evalúan de forma cualitativa por un comité de especialistas.)

## 5. Cómo mapea Taller Seguro Vision a cada criterio (post-PR #1)

El PR #1 pivotó el alcance a un MVP de EPP (`no_glasses`, `no_helmet`) corriendo en Raspberry Pi + webcam USB — el hardware que ya está disponible, sin depender del kit completo (Coral, cámara CSI, torre Andon). Esto cambia el análisis respecto a la primera revisión: **ya no hace falta comprar nada para tener algo funcional que mostrar.**

| Criterio | Estado actual | Qué falta cerrar antes del cierre |
|---|---|---|
| Claridad del problema | Fuerte — $380,000 MXN por accidente, 250,000 talleres PyME sin cobertura, dato cuantificado en el README | Nada crítico, solo pulir redacción para el formulario |
| Impacto social | Fuerte — seguridad laboral, prevención de amputaciones, enfoque en PyME desatendida | Nada crítico |
| Innovación tecnológica | Media-alta — visión por computadora edge, 100% offline, sin mensualidades | Nada crítico |
| Escalabilidad | Media — historia de replicabilidad (<$400 USD, open-source) existe pero no está articulada como go-to-market | Escribir 1 párrafo de distribución/adopción (¿cómo llega a otros 250,000 talleres?) |
| Viabilidad de modelo de negocio | **Débil** — el repo es 100% técnico, no hay pricing ni modelo de ingresos documentado | Escribir modelo de negocio explícito (venta de kit, licencia, suscripción de soporte, etc.) — es el hueco más grande |
| Evidencia funcional (implícito en Prototipo) | **Resuelto por el PR #1** — pipeline end-to-end probado (27 tests en verde), corre en el hardware ya disponible | Falta: cargar modelo público de EPP en `models/best.pt` y grabar el demo real (Steps 4 y 7 del roadmap del README) |

## 6. Clasificación recomendada: Prototipo vs Proyecto

**Prototipo.** El proyecto tiene pipeline funcional y validación técnica inicial, pero no usuarios reales en producción todavía. Postular en Proyecto sin un piloto real corrido en un taller sería forzar el encaje y arriesgar la credibilidad ante el jurado.

Si en los días que quedan antes del cierre se alcanza a correr un piloto corto (aunque sea 2–3 días) en un taller real con la Raspberry Pi + webcam, reevaluar Proyecto — es 3.3x más premio ($100k vs $30k) — pero solo si hay evidencia real y honesta de uso, no simulada.

## 7. Checklist antes del cierre (23 de agosto)

- [ ] Cargar modelo público de EPP (lentes + casco) en `models/best.pt` (Roboflow Universe) — Step 4 del roadmap
- [ ] Correr `python app.py --mode demo` con la webcam real en la Raspberry Pi y confirmar detección en vivo
- [ ] Grabar `assets/demo_torno_sin_lentes.gif` / video corto con el pipeline real (ver segundo documento: `docs/demo-video-script.md`)
- [ ] Redactar sección de modelo de negocio (el hueco más grande del scoring)
- [ ] Redactar sección de escalabilidad/distribución
- [ ] Confirmar categoría (Prototipo por defecto, salvo piloto real completado)
- [ ] Firmar y adjuntar carta compromiso
- [ ] Registrar en https://premiounitec.charly.io/spar/programs/PremioUNITEC26 con margen antes de las 23:59 del 23 de agosto

## 8. Estimación de probabilidad — metodología y límites

No existe un dataset público de postulantes con features y resultado (ganó/no ganó) de esta edición ni de anteriores — una regresión estadística real **no es posible** con la información disponible. Lo que sigue es una tasa base histórica más un ajuste cualitativo, no la salida de un modelo.

**Tasa base (2024–2025):**

| Edición | Inscritos | Completaron registro | Finalistas (2 categorías) | Ganadores |
|---|---|---|---|---|
| 2024 | 316 | 121 | 20 | 6 (3+3) |
| 2025 | 212 | 139 | ~20 | 6 (3+3) |

- P(llegar a semifinales) ≈ 9–10% (6 semifinalistas / ~60–70 postulantes completos por categoría)
- P(ganar \| semifinalista) = 50% (3 de 6)
- **P(ganar top-3, tasa base) ≈ 4–6%**

**Ajuste cualitativo:** con el hueco de modelo de negocio cerrado y el demo real grabado (checklist arriba), el proyecto tiene una narrativa de impacto social e innovación por encima del postulante promedio. Estimación ajustada razonable: **10–18% de probabilidad de llegar a semifinales**, sujeta a mucha incertidumbre — no es una cifra derivada de datos de competidores reales, es un juicio informado.

**Dato importante:** el jurado no premia sofisticación de hardware. Ganadores pasados incluyen proyectos de software puro corriendo "sobre cámara común sin acelerador dedicado" (traductor de LSM, 2025). El MVP de EPP en Raspberry Pi + webcam del PR #1 es, técnicamente, suficiente para competir — no hace falta el kit completo para el registro.

## Fuentes

- [Convocatoria oficial (PDF)](https://www.unitec.mx/hubfs/01.UNITEC/pdfs/2026/03/Convocatoria_Premio_Unitec_2026.pdf)
- [¿Qué es Premio UNITEC?](https://www.unitec.mx/premio/)
- [El Universal — Premio Unitec: postula tu proyecto](https://www.generacionuniversitaria.com.mx/oferta-academica/premio-unitec-postula-tu-proyecto-emprendedor-y-gana-hasta-100-mil-pesos/)
- [Premio UNITEC 2024 (blogs.unitec.mx)](https://blogs.unitec.mx/premio-2024-innovacion-tecnologica)
- [La Crónica de Hoy — edición 2024](https://www.cronica.com.mx/nacional/2024/11/03/entregan-premio-unitec-a-la-innovacion-tecnologica-para-desarrollo-social/)
- [Generación Universitaria — ganadores 2025](https://www.generacionuniversitaria.com.mx/campus/estos-son-los-proyectos-ganadores-del-premio-unitec-2025)
- [Valor Compartido — ganadores 2025](https://valor-compartido.com/dan-a-conocer-a-ganadores-del-premio-unitec-a-la-innovacion-tecnologica-para-el-desarrollo-social/)
