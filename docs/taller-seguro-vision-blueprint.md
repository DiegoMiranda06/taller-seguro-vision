# Taller Seguro Vision — Blueprint

> Generado por The Architect el 2026-07-30
> Archetype: Edge AI / Computer Vision Device (híbrido: internal-tool + api-backend, sin frontend web)

---

## 1. Project Overview

### Vision
Taller Seguro Vision es un dispositivo de visión por computadora en el borde (edge AI), 100% offline, cuya visión de producto es detectar "casi accidentes" (near miss) en tornos y fresadoras de talleres metal-mecánicos: operación sin lentes de seguridad, guantes puestos cerca del husillo, manos entrando en la zona de peligro del mandril, y llave de mandril olvidada. Cuando detecta riesgo, enciende una torre de luz roja (o hoy, mientras no hay relay, una alerta en consola) y graba un clip local (7s antes + 8s después) a USB, con metadata para reporte STPS. Está pensado para talleres PyME mexicanos que no pueden pagar sistemas industriales de $10k-25k USD.

**Alcance actual (v1) — ya en marcha**: ya se cuenta con el hardware mínimo (una **Raspberry Pi + una webcam USB sencilla**), así que el pipeline corre hoy directamente sobre ese hardware, no solo en una laptop de desarrollo. El alcance de detección se redujo a **solo EPP** — operador con/sin lentes de seguridad (`no_glasses`) y con/sin casco (`no_helmet`) — porque son las dos clases con datasets públicos ya disponibles y sin dependencia de una zona roja calibrada por estación, un torno físico, ni un relay/torre de luz. Las clases de near-miss (`glove_on_lathe`, `hand_in_red_zone`, `chuck_key_visible`) quedan documentadas como **roadmap** (Sección 9) — se retoman cuando haya dataset propio y el kit físico completo (relay, torre Andon, cámara CSI cerca del husillo).

**Contexto estratégico**: el primer despliegue real es en el taller de un conocido (1 cámara, hasta 2 máquinas). Pero el objetivo de negocio es usar este repo como vehículo para levantar capital semilla (Fondeadora, Play Business, CONAHCYT, concursos) **antes** de comprar el kit físico completo (Coral, cámara CSI, torre Andon). Esto significa que la Fase 0 del build debe producir un demo convincente (GIF/video) corriendo en el hardware que ya se tiene — la Raspberry Pi + webcam USB —, sin depender de los componentes pendientes del kit final.

### Goals
- Pipeline de detección de EPP (lentes + casco) funcional en la Raspberry Pi + webcam ya disponibles, para grabar el demo de la campaña de fondeo.
- Mismo código, sin reescritura, corriendo con Coral USB Accelerator + cámara CSI + GPIO una vez financiado el resto del kit y retomadas las clases de near-miss.
- Piloto real de 1-2 semanas en el taller objetivo, primero validando EPP, luego con datos reales de near-miss.
- Repositorio GitHub replicable por otros talleres (Apache 2.0), con README fondeable.

### Success Metrics
- Demo GIF/video de detección de EPP grabado en la Raspberry Pi + webcam ya disponibles, embebido en README, antes de gastar en el resto del kit.
- FPS e inferencia validados en el hardware real disponible hoy (Pi + CPU `.pt`) y, más adelante, con Coral.
- Tasa de falsos positivos medida durante el piloto de EPP (< 1 falsa alarma/hora como meta inicial).
- Costo adicional para el kit completo (near-miss) ≤ $8,000 MXN (~$400 USD), replicable.

---

## 2. Tech Stack

| Capa | Tecnología | Por qué |
|------|-----------|---------|
| Lenguaje | Python 3.11 | Ecosistema CV/ML maduro, corre igual en laptop y Pi |
| Visión / modelo | Ultralytics YOLOv8n (custom, multi-clase) | Un solo modelo; v1 solo 2 clases de EPP (`no_glasses`, `no_helmet`), export nativo a TFLite/EdgeTPU cuando se retomen las clases de near-miss |
| Runtime v1 (Raspberry Pi ya disponible) | `.pt` (PyTorch) vía Ultralytics, CPU (ARM) | Backend por default: corre directo en la Pi que ya se tiene, sin exportar nada ni comprar Coral. Más lento que con aceleración, pero suficiente para validar 2 clases de EPP. |
| Runtime demo optimizado (Intel, solo para laptop) | OpenVINO (export nativo de Ultralytics) | Tu ThinkPad T480 (i7-8650U + UHD 620) no tiene GPU NVIDIA — OpenVINO explota AVX2 y el iGPU Intel. Es x86-only: **no corre en la Raspberry Pi** (ARM). Úsalo solo si sigues grabando demos desde el T480. |
| Runtime roadmap (Pi + near-miss) | TFLite int8 compilado para Edge TPU vía `pycoral` | Cuando se sume el Coral USB Accelerator (todavía no comprado) y se retomen las clases de near-miss, para tiempo real con más clases |
| Captura de video | OpenCV (`cv2.VideoCapture`) en demo, `Picamera2` en producción | Abstraídas detrás de una interfaz común `CameraSource` |
| GPIO / alerta | `gpiozero` (RPi5) + relay 5V → torre Andon 12V | Path directo, más simple para primeras pruebas, como pediste |
| Config por estación | JSON + Pydantic (validación) | `torno_01.json` define zona roja, cámara, umbrales — sin nada hardcoded |
| Grabación de clips | Buffer circular en RAM + `cv2.VideoWriter` → USB | 7s pre + 8s post, JSON sidecar con metadata (evento, hora, confianza) |
| Dataset / etiquetado | Roboflow (free tier) | Empezamos con datasets públicos de PPE/lentes de seguridad para el modelo v0, luego etiquetado propio con footage real del taller |
| Entrenamiento | Google Colab (GPU gratis) + Ultralytics CLI | Sin costo, suficiente para YOLOv8n custom |
| Servicio en Pi | systemd (`taller-seguro.service`) | Auto-arranque y auto-restart, sobrevive cortes de luz |
| Testing | pytest | Lógica de zona/reglas se testea sin hardware ni modelo |
| CI | GitHub Actions (lint + pytest) | No requiere hardware, corre en cualquier runner |
| Licencia | Apache 2.0 | Ya definida, correcta para fondeo + replicación |
| Empaquetado | `pyproject.toml` con extras `[pi]` | Deps de hardware (gpiozero, picamera2, pycoral) opcionales — el repo instala limpio en cualquier laptop |

**No incluido a propósito**: base de datos relacional, autenticación, dashboard web, nube. Todo es un solo proceso Python offline por estación.

---

## 3. Directory Structure

```
taller-seguro-vision/
  app.py                          # Entry point: python app.py --mode demo|production --zona_config config/torno_01.json
  pyproject.toml                  # Deps base + extra [pi] para hardware (gpiozero, picamera2, pycoral, tflite-runtime)
  requirements.txt                # Pin de deps base (demo-friendly, sin libs de Pi)
  README.md                       # Pitch + instalación + demo GIF (ya tienes el borrador)
  LICENSE                         # Apache 2.0
  CLAUDE.md                       # Ver sección 15

  src/
    core/
      pipeline.py                 # Orquestador: capture -> detect -> rules -> alert + recorder
      rules_engine.py             # Evalúa detecciones contra config: v1 = no_glasses, no_helmet
      zone.py                     # Point-in-polygon, normalización de coordenadas (no usado por rules_engine en v1 — reservado para near-miss del roadmap)
      event.py                    # Dataclass Event + serialización JSON

    capture/
      base.py                     # Interfaz abstracta CameraSource (ABC)
      webcam_source.py            # cv2.VideoCapture — usado en modo demo (laptop)
      video_file_source.py        # Reproduce un .mp4 — para testear con footage público sin cámara
      picamera_source.py          # Picamera2 + Arducam IMX477 — SOLO se importa en modo production

    inference/
      base.py                     # Interfaz abstracta Detector (ABC)
      yolo_pt_detector.py         # Ultralytics .pt — fallback CPU/CUDA, portable a cualquier máquina
      yolo_openvino_detector.py   # OpenVINO — backend recomendado para laptops Intel sin GPU dedicada (ej. T480)
      yolo_edgetpu_detector.py    # TFLite + pycoral — SOLO se importa en modo production

    alert/
      base.py                     # Interfaz abstracta AlertOutput (ABC)
      mock_alert.py                # Log a consola ("🔴 ALERTA: sin_lentes") — modo demo
      gpio_alert.py                # gpiozero.LED/Relay — SOLO se importa en modo production

    recorder/
      ring_buffer.py               # Buffer circular de frames (pre-roll)
      clip_writer.py                # Flush pre+post roll a disco/USB + JSON sidecar

    config/
      schema.py                    # Modelos Pydantic: StationConfig, ZoneConfig
      loader.py                    # Carga y valida el JSON de estación

    tools/
      calibrate_zone.py             # CLI: click sobre un frame para dibujar el polígono de zona roja
      bench_inference.py            # Mide FPS/latencia del modelo actual en el hardware actual

  models/
    README.md                       # Dónde descargar/colocar pesos entrenados (NO se commitea a git)

  datasets/
    README.md                       # Flujo de recolección + etiquetado (Roboflow), datasets públicos usados en v0

  config/
    torno_01.json                   # Config de ejemplo, estación 1
    torno_02.json                   # Config de ejemplo, estación 2 (prototipo cubre hasta 2)

  scripts/
    install.sh                      # Instalador para RPi5: deps, udev rules del Coral, systemd
    export_to_edgetpu.sh            # yolov8n.pt -> tflite int8 -> edgetpu_compiler

  systemd/
    taller-seguro.service           # Unit file: auto-start, auto-restart, watchdog

  tests/
    test_zone.py                    # Geometría de polígonos (pure functions)
    test_rules_engine.py             # Reglas de negocio con detecciones sintéticas
    test_clip_writer.py               # Buffer + escritura de clip con video de prueba

  assets/
    demo_torno_sin_lentes.gif        # Demo de EPP generado en Fase 0 (Raspberry Pi + webcam ya disponibles)

  .github/
    workflows/ci.yml                 # Lint (ruff) + pytest en cada push
```

---

## 4. Data Model

No hay base de datos relacional — cada evento es un archivo JSON junto a su clip de video. Esto es intencional: el dispositivo es offline, single-station, y el volumen de eventos es bajo (near-miss, no cada frame).

### Entidades

**Event** (`clips/<station_id>/<fecha>/<timestamp>_<event_type>.json`)
| Campo | Tipo | Notas |
|-------|------|-------|
| event_id | str (uuid4) | Único por evento |
| station_id | str | Coincide con `station_id` del config |
| event_type | enum | v1: `no_glasses`, `no_helmet`. Roadmap (near-miss, no implementado): `glove_on_lathe`, `hand_in_red_zone`, `chuck_key_visible` |
| timestamp_utc | datetime ISO8601 | Momento del trigger (frame central del clip) |
| confidence | float 0-1 | Score del modelo en el frame de trigger |
| clip_path | str | Ruta relativa al .mp4 (mismo directorio) |
| duration_pre_s | float | Segundos de pre-roll incluidos (default 7) |
| duration_post_s | float | Segundos de post-roll incluidos (default 8) |
| resolved | bool | Reservado para revisión manual futura (default `false`) |

**StationConfig** (`config/torno_XX.json`, validado con Pydantic)
| Campo | Tipo | Notas |
|-------|------|-------|
| station_id | str | Ej. `torno_01` |
| mode | enum | `demo` \| `production` — determina qué adapters de capture/alert se instancian |
| inference_backend | enum | `pt` \| `openvino` \| `edgetpu` — independiente de `mode`. Default `pt`: corre en la Raspberry Pi (ARM) ya disponible sin exportar nada. `openvino` es exclusivo de CPU/iGPU Intel x86 (ej. el T480) — **no corre en la Pi**. `edgetpu` requiere el Coral USB Accelerator (roadmap, no comprado aún) |
| camera_source | enum | `webcam` \| `picamera` \| `video_file` — `webcam` (USB, vía OpenCV) es lo que usa la Raspberry Pi + webcam sencilla ya disponible; `picamera` (CSI) queda para cuando se sume esa cámara |
| camera_index_or_path | str/int | Índice de webcam, o ruta de video, o `None` para Picamera2 |
| zone | ZoneConfig \| None | Opcional en v1 (solo EPP, sin lógica de zona). Cuando se retomen las clases de near-miss del roadmap, `red_zone_polygon` (coordenadas normalizadas 0-1, generadas por `calibrate_zone.py`) vuelve a ser necesario |
| classes_enabled | list[str] | v1: subconjunto de `{no_glasses, no_helmet}` |
| confidence_thresholds | dict[str, float] | Umbral por clase, default 0.5 |
| alert_output | enum | `mock` \| `gpio` |
| gpio_pin | int \| null | Solo si `alert_output == gpio` |
| buffer_pre_seconds / buffer_post_seconds | float | Default 7 / 8 |
| usb_mount_path | str | Default `/media/usb0`, con fallback a carpeta local si no existe |

### Relaciones
Una `StationConfig` genera N `Event` a lo largo del tiempo. No hay relación inversa ni joins — cada evento es autocontenido (clip + JSON al lado).

### "Schema" (Pydantic, no SQL)
```python
class ZoneConfig(BaseModel):
    red_zone_polygon: list[tuple[float, float]]

class StationConfig(BaseModel):
    station_id: str
    mode: Literal["demo", "production"]
    inference_backend: Literal["pt", "openvino", "edgetpu"] = "pt"
    camera_source: Literal["webcam", "picamera", "video_file"]
    camera_index_or_path: str | int | None = None
    zone: ZoneConfig | None = None  # opcional en v1 (solo EPP, sin lógica de zona)
    classes_enabled: list[Literal["no_glasses", "no_helmet"]]
    confidence_thresholds: dict[str, float] = {}
    alert_output: Literal["mock", "gpio"]
    gpio_pin: int | None = None
    buffer_pre_seconds: float = 7.0
    buffer_post_seconds: float = 8.0
    usb_mount_path: str = "/media/usb0"
```

**Nota de crecimiento futuro**: si más adelante se agrega un dashboard multi-taller (pivote SaaS post-fondeo), estos JSON son el contrato de datos que se sincronizaría — no se necesita rediseñar el evento, solo agregar un paso de sync opcional.

---

## 5. Interfaces (CLI + Debug local — no hay API de red)

Este proyecto no expone servicios de red por diseño (100% offline). La única interfaz es la línea de comandos.

| Comando | Descripción |
|---------|-------------|
| `python app.py --mode demo --zona_config config/torno_01.json` | Corre el pipeline completo con webcam + modelo `.pt` + alerta mock (consola) |
| `python app.py --mode production --zona_config config/torno_01.json` | Corre con Picamera2 + modelo EdgeTPU + GPIO real |
| `python -m src.tools.calibrate_zone --source 0 --out config/torno_01.json` | Dibuja el polígono de zona roja sobre un frame en vivo |
| `python -m src.tools.bench_inference --model models/best.tflite` | Mide FPS/latencia en el hardware actual |
| `bash scripts/export_to_edgetpu.sh models/best.pt` | Exporta el modelo entrenado a TFLite int8 + compila para Edge TPU |

**Opcional (post-MVP, no v1)**: endpoint HTTP local (`Flask`, bind a `127.0.0.1` únicamente) con `/status` y `/last-event` para debug en sitio desde el celular en la misma red del taller. No es parte del build order v1 — anotado aquí para no perder la idea.

---

## 6. Arquitectura de Hardware y Software

### Diagrama de flujo
```
[Cámara: Webcam laptop | Arducam IMX477+Picamera2]
              │
              ▼
      CameraSource (interfaz)
              │  frame
              ▼
      Detector (interfaz)  ── modelo .pt (demo) o .tflite+EdgeTPU (producción)
              │  detecciones [clase, bbox, confianza]
              ▼
      rules_engine.py  ── combina detecciones + red_zone_polygon del config
              │  Event (si hay riesgo)
              ▼
      ┌───────┴────────┐
      ▼                ▼
AlertOutput        RingBuffer + ClipWriter
(mock: consola /    (siempre corriendo, guarda a
 gpio: relay+luz)    disco/USB solo si hay Event)
```

### Por qué esta arquitectura
El punto de diseño más importante del blueprint: **las tres interfaces (`CameraSource`, `Detector`, `AlertOutput`) son las únicas líneas donde el código "sabe" si está en una laptop o en un Raspberry Pi**. `pipeline.py` nunca importa `picamera2`, `gpiozero` ni `pycoral` directamente — los importa condicionalmente dentro de los adapters de producción, y solo si `config.mode == "production"`. Esto permite:
1. Grabar el demo de fondeo HOY en cualquier laptop, sin comprar nada.
2. Cuando llegue el capital, cambiar `mode: demo` → `mode: production` en el JSON y correr exactamente el mismo `pipeline.py` en el Pi.
3. Que cualquiera pueda clonar el repo y correr la demo sin tener el hardware — clave para que el proyecto sea creíble en una campaña de Fondeadora/Play Business.

### Wiring físico (modo producción, para cuando llegue el hardware)
```
Arducam IMX477 ── CSI ──> Raspberry Pi 5 ── USB 3.0 ──> Coral USB Accelerator
                              │
                              ├── GPIO (pin configurable) ──> Relay 5V ──> Torre Andon 12V (fuente externa 12V)
                              └── USB ──> USB drive (clips)
```

---

## 7. Repo & Presentación (para fondeo)

Dado que el objetivo es levantar capital antes de comprar hardware, el repo mismo es un activo de fondeo. No hay "design system" de UI tradicional (no hay frontend), pero sí hay estándares de presentación:

- **README.md**: mantener la estructura que ya tienes (badges, problema cuantificado, demo GIF, tabla de hardware, instalación). Actualizar el GIF en cuanto exista el demo de EPP de Fase 0 (Raspberry Pi + webcam ya disponibles).
- **assets/demo_torno_sin_lentes.gif**: grabado en Fase 0 con el hardware ya disponible (Raspberry Pi + webcam) — es el activo más importante para Fondeadora/Kickstarter.
- **docs/pitch-one-pager.md** (nuevo, opcional): resumen de 1 página — problema, solución, costo, tracción (GitHub stars, talleres piloto), ask. Reutiliza el copy del README.
- **Badges**: mantener status, hardware, license, "Hecho en México" — coherencia visual en Shields.io.
- **Naming**: "Taller Seguro Vision" consistente en README, CLAUDE.md, systemd service name, y config `station_id` prefix.

---

## 8. Seguridad y Config (no hay auth — dispositivo single-tenant offline)

No hay usuarios, cuentas ni sesiones — es un dispositivo físico por estación, sin red expuesta.

- **Config**: los JSON de estación no contienen secretos (no hay API keys — todo es offline). Permisos de archivo estándar, sin necesidad de cifrado.
- **USB**: opcional a futuro, cifrar el drive USB si el taller lo requiere por política de datos (fuera de scope v1).
- **Fail-safe de alerta**: si el proceso principal truena, el relay debe caer a un estado seguro conocido (documentado en Reglas No Negociables, sección 16).

---

## 9. Build Order

**Fase 0 — MVP de EPP en el hardware ya disponible (para la campaña de fondeo)**

**Nota: hardware y logística de pruebas**
Ya se cuenta con una **Raspberry Pi + una webcam USB sencilla** — el pipeline de Fase 0 corre directo ahí, no solo en una laptop. Esto define las decisiones de esta fase:

- **Backend de inferencia**: usar `inference_backend: "pt"` en la Pi — corre en su CPU ARM sin exportar nada ni comprar Coral. Es más lento que con aceleración, pero suficiente para validar 2 clases (lentes, casco) en tiempo casi real. Si se sigue usando el Lenovo ThinkPad T480 (Windows, Intel i7-8650U, 32GB RAM, iGPU Intel UHD 620) para grabar demos o iterar más rápido, ahí sí conviene `inference_backend: "openvino"` — pero es exclusivo de CPU/iGPU Intel x86, **nunca uses `openvino` en la Pi** (ARM).
- **No se necesita comprar una GPU ni un acelerador para esta fase.** El entrenamiento (Step 9) está planeado en Google Colab (GPU gratuita). Un Coral USB Accelerator es mejora opcional para el roadmap de near-miss, no un bloqueante del MVP de EPP.
- **Alcance de detección reducido a EPP**: `no_glasses` (sin lentes) y `no_helmet` (sin casco) — ambas clases existen en datasets públicos de PPE (Roboflow Universe), así que no se necesita grabar footage propio para arrancar. Las clases de near-miss (`glove_on_lathe`, `hand_in_red_zone`, `chuck_key_visible`) y la calibración de zona roja se mueven al roadmap (Fase 2), porque dependen de dataset propio y del kit físico completo (torno real, relay, torre Andon).
- **Quién graba el footage de prueba**: para el demo no necesitas el torno real — tú mismo frente a la webcam conectada a la Pi es suficiente. Grábate poniéndote y quitándote los lentes de seguridad y el casco. Si puedes, pide a 1-2 personas más que aparezcan brevemente frente a cámara — variar cara ayuda a que el modelo público de PPE generalice mejor y el GIF no se vea como "una sola toma casera". Esto no reemplaza el piloto real (Step 15) — es solo para el activo de fondeo.

**Step 1: Scaffolding del repo**
`pyproject.toml`, estructura de carpetas de la sección 3, `.gitignore` (excluir `models/*.pt`, `models/*.tflite`, `datasets/raw/`, `clips/`), `LICENSE` Apache 2.0, GitHub Actions CI (`ruff check` + `pytest`). README con la estructura que ya existe.

**Step 2: Interfaces abstractas**
Implementar `CameraSource`, `Detector`, `AlertOutput` como ABCs en `capture/base.py`, `inference/base.py`, `alert/base.py`. Implementar `WebcamSource`, `VideoFileSource`, `MockAlertOutput` (solo imprime a consola). Sin modelo real todavía — usar detecciones fake para probar el cableado.

**Step 3: Rules Engine (lógica pura, testeable sin modelo ni hardware)**
`rules_engine.py` (combina detecciones de EPP + config → `Event | None`, evaluando solo `no_glasses`/`no_helmet` contra `classes_enabled` y `confidence_thresholds`). Tests unitarios con fixtures sintéticas de detecciones — esto se puede testear 100% en CI sin GPU ni cámara. `zone.py` (point-in-polygon) se implementa igual como utilidad pura, pero no lo usa `rules_engine` en v1 — queda listo para cuando se retomen las reglas de near-miss del roadmap.

**Step 4: Detector real con modelo público (sin entrenar nada propio todavía)**
Usar un modelo YOLOv8n pre-entrenado + un dataset público de PPE (lentes/casco) de Roboflow Universe (existen varios: `safety-glasses`, `hard-hat-detection`, `PPE-detection`) para tener detección real de `no_glasses`/`no_helmet` funcionando HOY. `YoloPtDetector` corre en CPU — de la Pi o de la laptop.

**Step 5: Pipeline end-to-end en modo demo**
`pipeline.py` conecta `WebcamSource` → `YoloPtDetector` → `rules_engine` → `MockAlertOutput`. Correr `python app.py --mode demo` en la Raspberry Pi (o la laptop): debe imprimir "🔴 ALERTA: no_glasses" o "🔴 ALERTA: no_helmet" en consola al quitarse los lentes o el casco frente a la webcam.

**Step 6: Ring buffer + clip writer**
`ring_buffer.py` (deque de frames con timestamps) + `clip_writer.py` (al disparar un Event, escribe pre+post roll a `clips/` local con `cv2.VideoWriter` + JSON sidecar). Probar localmente, generar los primeros clips de prueba.

**Step 7: Grabar el demo y pulir el README**
Grabar `assets/demo_torno_sin_lentes.gif` con el pipeline de EPP real corriendo en la Raspberry Pi + webcam ya disponibles (no un mockup). Embeber en el README. Este es el entregable clave antes de lanzar la campaña de fondeo — no depende de comprar el resto del kit (Coral, cámara CSI, torre Andon).

**Fase 1 — Dataset y modelo propio de EPP (en paralelo al fondeo)**

**Step 8: Plan de dataset**
`datasets/README.md`: documentar qué datasets públicos de PPE se usan para bootstrap de `no_glasses` y `no_helmet` (ya cubren ambas clases sin grabar nada propio). El plan de recolección propia para las clases de near-miss (`glove_on_lathe`, `hand_in_red_zone`, `chuck_key_visible`) queda documentado como roadmap — no existen en datasets públicos y requieren grabar en el taller real cuando se retomen.

**Step 9: Entrenamiento inicial**
Notebook de Colab: fine-tune YOLOv8n sobre el dataset combinado de EPP (público + lo que se pueda recolectar). Exportar `.pt` para seguir iterando el modo demo con mejor precisión, corriendo directo en la Pi.

**Fase 2 — Kit físico completo + near-miss (roadmap, después de asegurar capital)**

Esta fase retoma las clases de near-miss (`glove_on_lathe`, `hand_in_red_zone`, `chuck_key_visible`) y el resto del kit físico (Coral, cámara CSI, relay, torre Andon) — no es parte del MVP de EPP que ya corre en la Raspberry Pi + webcam.

**Step 10: Bring-up de hardware adicional por separado**
`install.sh` para Raspberry Pi OS Lite: dependencias, udev rules del Coral USB Accelerator. Scripts de prueba aislados: captura de cámara (Picamera2), toggle de GPIO/relay, benchmark de inferencia EdgeTPU — cada componente se valida solo, antes de integrar.

**Step 11: Export a EdgeTPU**
`scripts/export_to_edgetpu.sh`: `.pt` → TFLite int8 → `edgetpu_compiler`. Validar con `bench_inference.py` que el FPS real en el Pi+Coral es aceptable (ajustar expectativas de 20 FPS si no se alcanza con el modelo multi-clase).

**Step 12: Adapters de producción**
Implementar `PicameraSource`, `YoloEdgeTPUDetector`, `GpioAlertOutput`. Cambiar `mode: production` en el config y correr el mismo `pipeline.py` sin tocar `rules_engine.py` ni `clip_writer.py`. Reintroducir en `rules_engine.py` el matching basado en `zone.py`/`bbox_in_zone` para `hand_in_red_zone`, análogo al que existía antes del pivote a solo-EPP.

**Step 13: Calibración de zona en sitio**
Correr `calibrate_zone.py` en el taller real, sobre el torno real, para generar el `red_zone_polygon` correcto de `torno_01.json` (campo `zone`, opcional desde el pivote a EPP-only, vuelve a poblarse aquí).

**Step 14: systemd + robustez**
`taller-seguro.service`: auto-start, auto-restart on crash, verificación de montaje de USB al boot, rotación/alerta de espacio en disco.

**Step 15: Piloto de campo**
1-2 semanas en el taller real. Primero valida EPP (ya corriendo desde Fase 0); luego, con el kit completo, mide falsos positivos de near-miss y ajusta `confidence_thresholds` por clase. Recolectar clips reales para re-entrenar el modelo con datos propios.

**Step 16: Repo v2 + replicación**
Actualizar README con métricas reales del piloto. Generalizar `install.sh` y la documentación de config para que un segundo taller pueda replicar sin ayuda directa. `CONTRIBUTING.md` para colaboradores externos.

---

## 10. Environment Setup

### Prerequisitos
- **MVP de EPP (`mode: "demo"`, hardware ya disponible)**: Python 3.11+, la Raspberry Pi (Raspberry Pi OS) + webcam USB sencilla ya en mano, `inference_backend: "pt"`. También corre igual en cualquier laptop con Python 3.11+ y webcam — confirmado para el Lenovo ThinkPad T480 (Windows, i7-8650U, 32GB RAM, UHD 620) con `inference_backend: "openvino"`, útil para grabar demos o entrenar.
- **Roadmap — Modo producción completo**: además de la Pi ya disponible, requiere Google Coral USB Accelerator, Arducam IMX477 + lente 6mm CS, relay 5V + torre Andon 12V con fuente externa — ninguno comprado todavía.

### Variables de entorno
No hay secretos ni API keys (proyecto 100% offline). Únicas variables opcionales:

| Variable | Descripción |
|----------|-------------|
| `LOG_LEVEL` | `INFO` por default, `DEBUG` para diagnóstico |
| `STATION_CONFIG_PATH` | Override del `--zona_config` vía env var (útil en systemd) |

### Comandos de setup inicial

```bash
# MVP de EPP — Raspberry Pi + webcam USB ya disponibles (Raspberry Pi OS)
git clone https://github.com/<tu-usuario>/taller-seguro-vision.git
cd taller-seguro-vision
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # sin extras — "pt" corre en la CPU ARM de la Pi
python app.py --mode demo --zona_config config/torno_01.json
```

```powershell
# Alternativa — Windows (ThinkPad T480 u otra laptop Windows, para grabar demos/entrenar)
git clone https://github.com/<tu-usuario>/taller-seguro-vision.git
cd taller-seguro-vision
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install .[intel]              # OpenVINO — recomendado sin GPU NVIDIA (caso T480). NO usar en la Pi (ARM).
python app.py --mode demo --zona_config config/torno_01.json
```

```bash
# Roadmap — modo producción (Raspberry Pi + Coral/GPIO/CSI, después de sumar el resto del kit)
bash scripts/install.sh
sudo systemctl enable taller-seguro.service
sudo systemctl start taller-seguro.service
```

**Nota Windows**: OpenCV en Windows a veces abre la webcam más rápido/estable forzando el backend DirectShow. Si `webcam_source.py` tarda en abrir o da timeout en el T480, usar `cv2.VideoCapture(0, cv2.CAP_DSHOW)` en vez de `cv2.VideoCapture(0)`.

---

## 11. Dependencies

### Core (todas las plataformas)
| Paquete | Propósito |
|---------|-----------|
| ultralytics | Entrenamiento e inferencia YOLOv8 (.pt) |
| opencv-python | Captura de video, VideoWriter, dibujo de overlays |
| numpy | Manipulación de frames/arrays |
| pydantic | Validación de config JSON por estación |

### Extra `[intel]` (recomendado para tu T480 y cualquier laptop Intel sin GPU dedicada, `pip install .[intel]` — **no instalar en la Raspberry Pi, es x86-only**)
| Paquete | Propósito |
|---------|-----------|
| openvino | Runtime de inferencia optimizado para CPU/iGPU Intel (AVX2 + UHD 620) |

### Extra `[pi]` (solo Raspberry Pi, instalado con `pip install .[pi]`)
| Paquete | Propósito |
|---------|-----------|
| gpiozero | Control de GPIO/relay |
| picamera2 | Captura con el módulo de cámara CSI |
| pycoral / tflite-runtime | Inferencia en Edge TPU |

### Dev
| Paquete | Propósito |
|---------|-----------|
| pytest | Tests unitarios |
| ruff | Lint + formato |

---

## 12. Deployment Strategy

No hay hosting en la nube. El "deployment" es una instalación física por estación:
- **Demo**: correr `app.py --mode demo` localmente, sin instalación permanente.
- **Producción**: `install.sh` deja el Pi listo con systemd; `taller-seguro.service` arranca el pipeline al boot y lo reinicia si truena.
- **Entornos**: `demo` (laptop, desarrollo/marketing) vs `production` (estación real) — se diferencian únicamente por el campo `mode` del config JSON, nunca por ramas de código distintas.
- **Versionado**: releases de GitHub por versión de modelo + código; cada `StationConfig` puede pinnear qué versión de modelo usa.

---

## 13. Testing Strategy

### Unit tests
`zone.py` (geometría de polígonos) y `rules_engine.py` (combinación de detecciones + config → eventos) son funciones puras — se testean con `pytest` sin cámara, sin modelo, sin hardware. Correr en CI en cada push.

### Integration tests
`test_clip_writer.py`: correr el pipeline completo contra un `VideoFileSource` con un video de prueba fijo, verificar que se generan los clips y JSON sidecar esperados.

### Hardware-in-the-loop (manual, no automatizable en CI)
Checklist a correr en sitio: captura de cámara real, toggle de relay/torre de luz, benchmark de FPS con `bench_inference.py` en el hardware final. Documentar resultados en `docs/hardware-validation.md`.

No aplica E2E de navegador (no hay UI web).

---

## 14. Skills a Usar Durante el Build

| Skill | Cuándo | Por qué |
|-------|--------|---------|
| `/deep-research` | Step 8-9 (dataset/modelo), Step 11 (export EdgeTPU) | Confirmar datasets públicos vigentes en Roboflow Universe y compatibilidad actual YOLOv8→EdgeTPU antes de comprometerse |
| `/deep-research` | Antes de Step 10 (compra de hardware) | Revalidar precios/disponibilidad de Coral USB Accelerator (descontinuado por Google en el pasado — confirmar stock vigente) y alternativas si no hay stock |
| `/find-skills` | Step 1 | Buscar skills específicas de Python/embedded/edge-AI que puedan no estar en este listado |

**Nota**: no aplican `/frontend-design`, `/ui-ux-pro-max`, `/shadcn-ui` — no hay frontend web en este proyecto.

---

## 15. CLAUDE.md para el Proyecto Target

```markdown
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
```

---

## 16. Reglas No Negociables (nivel blueprint)

1. **Abstracción de hardware primero.** `CameraSource`, `Detector` y `AlertOutput` deben existir como interfaces desde el Step 2 del build order — no se implementa nada concreto antes de tener la interfaz, porque el modo demo (Fase 0) depende de esto para no bloquearse esperando el hardware.
2. **El repo debe instalar y correr en modo demo sin ningún paquete de Raspberry Pi instalado.** Esto es un requisito de negocio (fondeo), no solo técnico — cualquiera debe poder clonar y ver el demo funcionar.
3. **Nunca commitear pesos de modelo, datasets crudos, ni clips de video** — son artefactos grandes y potencialmente sensibles (video de un taller real).
4. **Toda regla de detección de riesgo se testea sin hardware.** Si una regla nueva no se puede testear con datos sintéticos, está mal diseñada.
5. **Fail-safe en la alerta.** Ante cualquier excepción no manejada en el loop principal, el sistema debe preferir quedarse en un estado visiblemente "fallando" antes que en verde silencioso — es un sistema de seguridad, no un feature de producto.
6. **El JSON sidecar de cada evento es el contrato de datos para el reporte STPS y para cualquier futura sincronización a un dashboard multi-taller** — no se simplifica ni se omite ningún campo definido en la sección 4.
7. **No agregar nube, autenticación, ni multi-tenant en v1.** Si surge la conversación de un dashboard central (pivote SaaS post-fondeo), es un proyecto nuevo que consume estos JSON — no se mete en este repo.
