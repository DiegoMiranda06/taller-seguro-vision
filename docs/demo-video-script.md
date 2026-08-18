# Guion y prompts de contenido visual — video de postulación Premio UNITEC 2026

> Insumo para grabar el video/demo de la postulación de Taller Seguro Vision. Diseñado para producirse con lo que ya existe tras el PR #1 (MVP de EPP en Raspberry Pi + webcam) sin depender del kit completo.

## 0. Principio rector

**El metraje real es la prueba. La animación es apoyo, nunca sustituto.**

El jurado evalúa "innovación tecnológica" e "impacto social" con evidencia. Si el video se ve 100% animado, no hay nada que demuestre que el sistema funciona de verdad — y esta convocatoria explícitamente exige un prototipo "capaz de demostrar su operación básica". Regla dura para toda la producción:

- **Mínimo ~70% del tiempo de pantalla debe ser metraje real** (la Raspberry Pi, la webcam, la alerta disparando, el dueño del taller si es posible).
- La animación se usa solo para lo que la cámara no puede mostrar directamente: el costo del problema en México, el diagrama de arquitectura, el flujo de datos interno, la proyección de escalabilidad.
- Cada segmento animado debe rotularse visualmente (ej. un pequeño label "ilustrativo" o un estilo gráfico claramente distinto al metraje real) para que el jurado nunca confunda una animación conceptual con una demostración de funcionamiento.

## 1. Estructura recomendada (90–120 segundos)

| # | Escena | Duración | Tipo |
|---|---|---|---|
| 1 | Hook — el problema en una frase | 8s | Animación (dato) |
| 2 | El problema, con cifras | 15s | Animación (infografía) + metraje de apoyo si hay footage de un torno/taller |
| 3 | Presentación de la solución | 10s | Metraje real (hardware en mano: Pi + webcam) |
| 4 | **Demo en vivo** — detección funcionando | 30–40s | **Metraje real, sin cortes forzados** |
| 5 | Cómo funciona por dentro (arquitectura) | 12s | Animación (diagrama) |
| 6 | Impacto y escalabilidad | 10s | Animación (mapa/proyección) |
| 7 | Roadmap y ask | 10s | Metraje real (a cámara) + texto |
| 8 | Cierre / marca | 5s | Animación (logo/badge) |

## 2. Shot list — qué grabar literalmente

Todo esto se graba con lo que ya está disponible (Raspberry Pi + webcam USB) una vez completado el Step 4 del roadmap (`models/best.pt` cargado):

1. **Plano de establecimiento**: la Raspberry Pi conectada, la webcam apuntando a un puesto de trabajo simulado (o real si hay acceso al taller).
2. **Plano de operador**: alguien frente a la cámara, primero SIN lentes/casco (para disparar la detección), luego CON lentes/casco (para mostrar el estado "seguro").
3. **Plano de pantalla/consola**: la terminal mostrando el output de `app.py --mode demo` en tiempo real cuando detecta `no_glasses` / `no_helmet` — esto es la prueba dura de que el modelo corre.
4. **Plano del clip guardado**: mostrar el archivo `.mp4` + JSON sidecar generado en `clips/` — evidencia de que el sistema graba automáticamente, no es un mock de cámara.
5. (Opcional, si hay taller real) **Plano de contexto**: un torno o fresadora real de fondo, para anclar el problema visualmente sin tener que dramatizar un accidente.
6. **Plano a cámara**: quien postula hablando 8-10s sobre el roadmap (kit completo, near-miss) — humaniza la postulación.

No se necesita el kit completo (Coral, cámara CSI, torre Andon) para ningún plano de este shot list — todo corre con Pi + webcam según el estado actual del PR #1.

## 3. Guion / voiceover (español)

> Ajustar tiempos según ritmo real de grabación; esto es un borrador de arranque, no un texto rígido.

**[0:00–0:08] Hook**
> "Cada año, miles de trabajadores en talleres mexicanos pierden dedos o manos en tornos y fresadoras. El 80% de esos accidentes... avisan antes."

**[0:08–0:23] El problema**
> "Un solo accidente cuesta 380 mil pesos entre IMSS, multas y paro de máquina. Los sistemas de seguridad con visión artificial cuestan hasta 25 mil dólares por máquina — impagables para los 250 mil talleres PyME de México. Nadie mide sus 'casi accidentes'. Sin datos, no hay prevención."

**[0:23–0:33] La solución**
> "Taller Seguro Vision es un sistema de visión por computadora 100% offline que corre en hardware que cuesta menos de 400 dólares. Esto es todo lo que necesita hoy: una Raspberry Pi y una cámara web."

**[0:33–1:13] Demo en vivo**
> "Así se ve funcionando. [SIN NARRACIÓN o narración mínima — dejar que se vea/escuche la detección real] Cuando detecta que el operador no trae lentes o casco, el sistema alerta y guarda un clip de evidencia automáticamente, con toda la metadata para un reporte de seguridad."

**[1:13–1:25] Cómo funciona**
> "Por dentro, un pipeline simple: cámara, detección con IA, motor de reglas, alerta y grabación — todo corriendo local, sin nube, sin mensualidades."

**[1:25–1:35] Impacto y escalabilidad**
> "Es open-source y replicable: cualquier taller en México puede clonar el proyecto y montarlo con el mismo kit de bajo costo."

**[1:35–1:45] Roadmap y cierre**
> "Hoy detectamos falta de lentes y casco. El siguiente paso es sumar detección de manos en zona de riesgo y alerta física con torre de luz. [nombre] — Taller Seguro Vision."

## 4. Dónde insertar animación generada por IA (y dónde NO)

**SÍ usar animación para:**
- Escena 1-2 (hook + cifras del problema): infografía animada con el dato de 380,000 MXN y 250,000 talleres.
- Escena 5 (arquitectura): diagrama animado del pipeline (Cámara → Detector → Reglas → Alerta/Grabación).
- Escena 6 (escalabilidad): mapa de México con puntos apareciendo en distintos estados, simbolizando replicación.
- Escena 8 (cierre): badge/logo animado.

**NUNCA usar animación para:**
- La demo en sí (escena 4). Generar una animación de "cómo se vería" la detección funcionando sería presentar como evidencia algo que no ocurrió — además de ser fácilmente detectable por el jurado y dañar la credibilidad del proyecto.
- Cualquier plano que pretenda sustituir hardware que no se tiene (torre Andon, cámara CSI). Si el kit completo no existe todavía, no se anima como si existiera — se menciona como roadmap (escena 7), con lenguaje explícito de "próximo paso".

## 5. Prompts listos para generación de contenido visual

Prompts pensados para herramientas de generación de imagen/video por IA (adaptar a la herramienta disponible: Runway, Pika, Sora, Kling, o un generador de imágenes + animación en After Effects/Remotion). Todos están en español para consistencia con el voiceover; traducir si la herramienta lo requiere.

**Escena 1-2 — Infografía del problema:**
```
Animación de motion graphics, estilo infografía corporativa minimalista, fondo blanco con acentos en rojo y negro. Un ícono de una mano cerca de un torno industrial se transforma en un ícono de alerta roja. Aparece el texto grande "$380,000 MXN" con contador animado subiendo desde cero. Debajo, texto secundario "costo promedio de un accidente en torno/fresadora en México". Estilo plano (flat design), sin fotorrealismo, 2D, transiciones suaves, 8 segundos, loop limpio.
```

**Escena 2 (alternativa) — Talleres desatendidos:**
```
Animación 2D flat design, mapa esquemático de México con puntos amarillos apareciendo progresivamente representando talleres PyME (objetivo: transmitir "250,000 talleres"). Contador numérico animado subiendo hasta 250,000. Paleta: blanco, gris oscuro, un acento rojo de alerta. Sin texto largo, tipografía sans-serif grande y limpia. 6-7 segundos.
```

**Escena 5 — Diagrama de arquitectura del pipeline:**
```
Diagrama técnico animado, estilo flowchart minimalista sobre fondo blanco. Cuatro nodos conectados por flechas que se dibujan en secuencia: "Cámara" -> "Detección IA" -> "Motor de reglas" -> "Alerta + Grabación". Cada nodo es un ícono simple dentro de un rectángulo redondeado, línea negra fina, acento de color al activarse (verde a rojo cuando llega a "Alerta"). Estilo limpio tipo diagrama de producto SaaS, sin elementos 3D, 10-12 segundos.
```

**Escena 6 — Escalabilidad / replicación:**
```
Animación 2D, silueta del mapa de México, puntos de luz (estilo "nodo de red") encendiéndose uno por uno en distintos estados, conectados por líneas delgadas, sugiriendo una red creciente de talleres equipados. Paleta consistente con las escenas anteriores (blanco/gris/rojo de acento). Texto breve superpuesto al final: "Open-source. Replicable. <$400 USD por estación." 8-10 segundos.
```

**Escena 8 — Cierre/marca:**
```
Animación simple de cierre: el nombre "Taller Seguro Vision" con ícono de casco/lentes de seguridad estilizado, aparición suave (fade + slight scale), fondo blanco, acento rojo, tipografía bold sans-serif. 4-5 segundos, apto como outro de video corporativo/pitch.
```

**Nota sobre estilo:** mantener paleta y tipografía consistentes entre todos los clips animados (blanco/gris/rojo de acento) para que se lean como una sola pieza de motion graphics y se distingan claramente del metraje real de cámara — ese contraste visual es justamente lo que evita que el jurado confunda animación con demo real.

## 6. Checklist técnico de grabación y edición

- [ ] Cargar `models/best.pt` (modelo público de EPP) antes de grabar — sin esto no hay detección real que filmar
- [ ] Grabar en buena luz, encuadre estable (trípode o superficie fija para la webcam)
- [ ] Capturar audio limpio del voiceover por separado si es posible (mejor que audio ambiente de la habitación)
- [ ] Exportar el video final en formato horizontal 16:9 (estándar para revisión de jurado) salvo que la plataforma de registro pida vertical
- [ ] Duración total entre 90 y 120 segundos — los comités de evaluación revisan decenas de postulaciones, la brevedad juega a favor
- [ ] Revisar que ningún segmento animado se pueda confundir con metraje real antes de exportar la versión final

## 7. Nota de honestidad ante el jurado

Todo lo animado en este guion es explícitamente ilustrativo y está separado del único bloque que debe ser 100% real: la demo en vivo (escena 4). Esta separación no es solo ética — es estratégica: un jurado de innovación reconoce con facilidad contenido generado por IA presentado como funcionamiento real, y eso pone en riesgo la credibilidad de toda la postulación, incluida la parte que sí es genuina y sólida.
