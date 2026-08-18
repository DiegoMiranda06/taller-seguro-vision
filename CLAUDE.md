# Taller Seguro Vision

Dispositivo edge AI offline que graba clips locales de evidencia en tornos/fresadoras. **Alcance actual (v1): detección de EPP (sin lentes, sin casco) corriendo en la Raspberry Pi + webcam USB sencilla que ya se tienen.** Las reglas de near-miss (guantes, mano en zona roja, llave de mandril) son roadmap — requieren hardware/dataset adicional, no forman parte del v1.

## Commands

- `python app.py --mode demo --zona_config config/torno_01.json` — Corre el pipeline con webcam + modelo .pt + alerta en consola (sin hardware)
- `python app.py --mode production --zona_config config/torno_01.json` — Corre con Picamera2 + EdgeTPU + GPIO real (solo en Raspberry Pi)
- `python -m src.tools.calibrate_zone --source 0 --out config/torno_01.json` — Calibra el polígono de zona roja
- `python -m src.tools.bench_inference --model models/best.tflite` — Mide FPS/latencia en el hardware actual
- `pytest` — Corre los tests unitarios (zona, reglas, clip writer)
- `ruff check .` — Lint
- `bash scripts/export_to_edgetpu.sh models/best.pt` — Exporta modelo entrenado a TFLite/EdgeTPU

## Tech Stack

Python 3.11 + Ultralytics YOLOv8n (`.pt` en CPU — backend por default, corre en la Raspberry Pi (ARM) que ya se tiene; OpenVINO como alternativa solo en laptops Intel x86 sin GPU dedicada, nunca en la Pi; TFLite/EdgeTPU cuando se sume el Coral USB Accelerator) + OpenCV + Pydantic (config) + gpiozero/Picamera2/pycoral (solo modo producción, deps opcionales `[pi]`) + systemd (producción). Hardware ya disponible: Raspberry Pi + webcam USB sencilla → `inference_backend: "pt"`, `camera_source: "webcam"`. Dev machine de referencia para autoría de demo/entrenamiento: ThinkPad T480 (Windows, i7-8650U, 32GB RAM, sin GPU NVIDIA) → usar `inference_backend: openvino` ahí, nunca en la Pi.

## Architecture

### Estructura de directorios
- `src/core/` — pipeline orquestador, motor de reglas, geometría de zona, modelo de evento
- `src/capture/` — fuentes de cámara intercambiables (webcam, video file, picamera) detrás de una interfaz común
- `src/inference/` — detectores intercambiables (.pt en CPU/GPU, TFLite+EdgeTPU) detrás de una interfaz común
- `src/alert/` — salidas de alerta intercambiables (consola mock, GPIO real) detrás de una interfaz común
- `src/recorder/` — buffer circular de frames + escritura de clips con metadata JSON
- `src/config/` — schema Pydantic y loader del JSON por estación
- `config/*.json` — un archivo por estación física (torno_01.json, torno_02.json)

### Flujo de datos
`CameraSource.read_frame()` → `Detector.detect(frame)` → `rules_engine.evaluate(detections, station_config)` → si hay riesgo: `AlertOutput.trigger(event_type)` + `ClipWriter.flush(event)`. El buffer circular corre siempre; solo se vuelca a disco cuando hay un Event.

### Patrones clave
- **Todo es intercambiable por config, nunca por rama de código.** `pipeline.py` instancia `CameraSource`/`Detector`/`AlertOutput` según `StationConfig.mode` y `.camera_source`/`.alert_output` — nunca hay un `if is_raspberry_pi()` disperso en la lógica de negocio.
- **Imports de hardware son locales al adapter.** `picamera2`, `gpiozero`, `pycoral` se importan SOLO dentro de `picamera_source.py`, `gpio_alert.py`, `yolo_edgetpu_detector.py` respectivamente — nunca en `pipeline.py` ni en `rules_engine.py`. Esto permite que el repo instale y corra en modo demo en cualquier laptop sin esas dependencias.
- **La lógica de negocio es pura y se testea sin hardware.** `zone.py` y `rules_engine.py` no importan nada de `capture/`, `inference/` ni `alert/` — reciben datos ya extraídos (detecciones, config) y regresan un `Event | None`. `zone.py` (point-in-polygon) no lo usa `rules_engine` en el alcance actual (solo EPP) — queda listo para las reglas de near-miss del roadmap.

## Code Organization Rules

1. **Interfaces primero.** `CameraSource`, `Detector`, `AlertOutput` son ABCs en sus respectivos `base.py`. Cualquier implementación nueva hereda de la interfaz, no se agregan métodos ad-hoc.
2. **Un adapter por archivo.** `webcam_source.py`, `picamera_source.py`, etc. — no mezclar dos implementaciones de una interfaz en el mismo archivo.
3. **Type hints obligatorios** en toda función pública (proyecto Python 3.11, usar `from __future__ import annotations` si hace falta).
4. **Config es la única fuente de variación entre estaciones.** Ningún índice de cámara, pin GPIO o umbral hardcodeado en código — todo vive en el JSON de estación.
5. **Nunca commitear pesos de modelo, datasets crudos o clips grabados.** `.gitignore` cubre `models/*.pt`, `models/*.tflite`, `datasets/raw/`, `clips/`.

## Design / Repo Presentation

- Sin frontend — no aplica sistema de diseño de UI.
- README mantiene estructura de badges + demo GIF + tabla de hardware ya definida por el proyecto original.
- `assets/demo_torno_sin_lentes.gif` es el activo de fondeo — debe regenerarse cada vez que el pipeline de demo mejore visiblemente.

## Environment Variables

| Variable | Descripción |
|----------|-------------|
| `LOG_LEVEL` | `INFO` por default, `DEBUG` para diagnóstico |
| `STATION_CONFIG_PATH` | Override opcional de la ruta de config (útil en systemd) |

## Reglas No Negociables

1. El mismo `pipeline.py` debe correr en modo demo (laptop/webcam/mock) y producción (Pi/Picamera/GPIO) cambiando solo el config — jamás código hardware-específico fuera de `capture/` y `alert/`.
2. Nunca commitear pesos de modelo, datasets crudos, ni clips grabados a git.
3. Toda la lógica de `zone.py` y `rules_engine.py` debe ser pura y tener tests unitarios que corran sin cámara, modelo ni GPIO.
4. El output de alerta debe fallar seguro: si el proceso truena, el relay/torre de luz debe quedar en un estado visible de falla (ej. parpadeo o quedarse en rojo), nunca silenciosamente en verde.
5. Cada evento grabado DEBE producir su JSON sidecar con `station_id`, `timestamp_utc`, `event_type`, `confidence` — es el contrato de datos para el reporte STPS, no es opcional.
6. `requirements.txt` base NUNCA debe forzar dependencias de Raspberry Pi (`gpiozero`, `picamera2`, `pycoral`, `tflite-runtime`) — van en el extra `[pi]` de `pyproject.toml`.

## Referencia

El blueprint técnico completo (stack, modelo de datos, build order de 16 pasos, testing strategy) está en [`docs/taller-seguro-vision-blueprint.md`](./docs/taller-seguro-vision-blueprint.md). Este CLAUDE.md es el resumen operativo; el blueprint es la fuente completa si falta contexto.
