# datasets/

Este directorio es donde vive el dataset de entrenamiento — **nunca se
commitea a git** (`.gitignore` excluye `datasets/raw/`).

## Estado actual: placeholder

Todavía no hay un plan de dataset documentado ni un modelo propio
entrenado. Eso corresponde a los **Steps 8-9** del build order
(`docs/taller-seguro-vision-blueprint.md`, Fase 1 — Dataset y modelo
propio, en paralelo al fondeo), fuera del alcance de este build (Fase 0,
Steps 1-6).

Lo que sí está listo para consumir ese dataset una vez exista: los
detectores en `src/inference/` (`YoloPtDetector`, `YoloOpenVINODetector`)
no tienen ninguna suposición hardcoded sobre clases o rutas — cargan
cualquier modelo YOLOv8 exportado que apunte el config.

## Alcance actual (v1): solo EPP

El MVP que corre hoy en la Raspberry Pi + webcam simple que ya se tiene
detecta únicamente dos clases:

- `no_glasses` — operador sin lentes/gafas de seguridad
- `no_helmet` — operador sin casco

Las clases de near-miss del blueprint original (`glove_on_lathe`,
`hand_in_red_zone`, `chuck_key_visible`) quedaron en el roadmap — no
forman parte del dataset ni del modelo v1 (ver Sección 9 del blueprint).

## Plan a documentar en Step 8

Cuando se ejecute el Step 8, este archivo debe documentar:

1. **Datasets públicos de bootstrap** (Roboflow Universe): ya existen
   datasets públicos de PPE que cubren ambas clases directamente —
   `safety-glasses` / `PPE-detection` para `no_glasses`, y
   `hard-hat-detection` / `PPE-detection` (muchos datasets de "hard hat"
   incluyen tanto casco como lentes) para `no_helmet`. No se necesita
   grabar footage propio para arrancar el v1.
2. **Plan de recolección propia (roadmap, no v1)**: las clases de
   near-miss específicas de este proyecto (`hand_in_red_zone`,
   `chuck_key_visible`, `glove_on_lathe`) no existen en datasets
   públicos — requerirán grabar footage real en el taller objetivo y
   etiquetarlo en Roboflow (free tier) cuando se retomen.
3. **Combinación y split** para el fine-tune de YOLOv8n en Colab (Step 9).

Usar `/deep-research` (per blueprint Sección 14) antes de comprometerse a
datasets específicos, para confirmar que siguen vigentes en Roboflow
Universe.
