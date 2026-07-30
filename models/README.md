# models/

Este directorio es donde vive el modelo entrenado — **nunca se commitea a
git** (`.gitignore` excluye `models/*.pt`, `models/*.tflite`,
`models/*.onnx`).

## Estado actual: placeholder

Todavía no existe un modelo custom entrenado para las 4 clases de riesgo
(`no_glasses`, `glove_on_lathe`, `hand_in_red_zone` → clase cruda `hand`,
`chuck_key_visible`). Eso corresponde a los **Steps 8-9** del build order
(`docs/taller-seguro-vision-blueprint.md`, Fase 1 — Dataset y modelo
propio), fuera del alcance de este build (Fase 0, Steps 1-6).

`YoloPtDetector` y `YoloOpenVINODetector` (`src/inference/`) están
implementados de forma genérica contra la API de Ultralytics: cargan
cualquier modelo cuya ruta se les indique en el `StationConfig`. No
asumen que el archivo ya existe — para correr el pipeline con detección
real hoy, usa un modelo YOLOv8n pre-entrenado (ej. `yolov8n.pt` de
Ultralytics) o un modelo público de PPE/lentes de seguridad de Roboflow
Universe (Step 4 del build order), y colócalo aquí:

```
models/
  best.pt                    # usado por YoloPtDetector (inference_backend: "pt")
  best_openvino_model/       # usado por YoloOpenVINODetector (inference_backend: "openvino")
                             #   generado con: model.export(format="openvino")
  best_edgetpu.tflite        # usado por YoloEdgeTPUDetector (inference_backend: "edgetpu", solo Pi)
```

## Cuando llegue el Step 9 (entrenamiento propio)

El notebook de Colab exportará el `.pt` fine-tuned; para el T480 (Intel,
sin GPU dedicada), expórtalo también a OpenVINO:

```bash
yolo export model=models/best.pt format=openvino
```

Y para producción en el Pi (Step 11), a Edge TPU vía
`scripts/export_to_edgetpu.sh` (no incluido en este build — Fase 2).
