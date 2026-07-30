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

## Plan a documentar en Step 8

Cuando se ejecute el Step 8, este archivo debe documentar:

1. **Datasets públicos de bootstrap** (Roboflow Universe): datasets
   existentes de `safety-glasses` / `PPE-detection` para arrancar las
   clases `no_glasses` y `glove_on_lathe` sin grabar nada propio primero.
2. **Plan de recolección propia**: las clases específicas de este
   proyecto (`hand_in_red_zone`, `chuck_key_visible`) no existen en
   datasets públicos — requieren grabar footage real en el taller
   objetivo y etiquetarlo en Roboflow (free tier).
3. **Combinación y split** para el fine-tune de YOLOv8n en Colab (Step 9).

Usar `/deep-research` (per blueprint Sección 14) antes de comprometerse a
datasets específicos, para confirmar que siguen vigentes en Roboflow
Universe.
