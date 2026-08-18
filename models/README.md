# models/

Este directorio es donde vive el modelo entrenado — **nunca se commitea a
git** (`.gitignore` excluye `models/*.pt`, `models/*.tflite`,
`models/*.onnx`).

## Estado actual: placeholder

Todavía no existe un modelo custom entrenado. El alcance v1 son 2 clases
de EPP: `no_glasses` (sin lentes/gafas) y `no_helmet` (sin casco). Eso
corresponde a los **Steps 8-9** del build order
(`docs/taller-seguro-vision-blueprint.md`, Fase 1 — Dataset y modelo
propio), fuera del alcance de este build (Fase 0, Steps 1-6).

`YoloPtDetector` y `YoloOpenVINODetector` (`src/inference/`) están
implementados de forma genérica contra la API de Ultralytics: cargan
cualquier modelo cuya ruta se les indique en el `StationConfig`. No
asumen que el archivo ya existe — para correr el pipeline con detección
real hoy, usa un modelo público de PPE (casco + lentes) de Roboflow
Universe (Step 4 del build order), y colócalo aquí:

```
models/
  best.pt                    # usado por YoloPtDetector (inference_backend: "pt")
                              #   backend recomendado en la Raspberry Pi (ARM) que ya se tiene
  best_openvino_model/       # usado por YoloOpenVINODetector (inference_backend: "openvino")
                             #   solo CPU/iGPU Intel x86 (ej. el T480) — NO corre en la Pi
                             #   generado con: model.export(format="openvino")
  best_edgetpu.tflite        # usado por YoloEdgeTPUDetector (inference_backend: "edgetpu")
                             #   requiere el Coral USB Accelerator — todavía no comprado
```

## Cuando llegue el Step 9 (entrenamiento propio)

El notebook de Colab exportará el `.pt` fine-tuned para las 2 clases de
EPP (`no_glasses`, `no_helmet`). Para el T480 (Intel, sin GPU dedicada),
expórtalo también a OpenVINO si se sigue usando para grabar demos:

```bash
yolo export model=models/best.pt format=openvino
```

En la Raspberry Pi ya disponible, el `.pt` corre directamente en CPU
(ARM) sin exportar nada — más lento que con aceleración, pero suficiente
para validar las 2 clases de EPP hoy. Cuando se sume un Coral USB
Accelerator (roadmap), exportar a Edge TPU vía
`scripts/export_to_edgetpu.sh` (no incluido en este build — Fase 2).
