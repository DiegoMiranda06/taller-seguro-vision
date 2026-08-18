# Taller Seguro Vision 🦺🤖 - Detección de EPP y Near Miss en Tornos y Fresadoras

> Un sistema open-source de bajo costo con IA que evita amputaciones y accidentes en talleres metal-mecánicos. 100% offline, < $400 USD por estación.

![Status](https://img.shields.io/badge/status-MVP%20de%20EPP%20en%20Raspberry%20Pi-yellow)
![Hardware](https://img.shields.io/badge/hardware-Raspberry%20Pi%20%2B%20webcam%20USB-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Hecho en México](https://img.shields.io/badge/Hecho%20en-M%C3%A9xico-red)

### 🎥 Demo - 15 segundos
> *Pendiente: GIF del MVP (Raspberry Pi + webcam USB) detectando falta de lentes/casco y prendiendo la alerta.*
> `assets/demo_torno_sin_lentes.gif`

### El Problema es Gigante y Nadie lo Mide
- **1 accidente en torno/fresadora cuesta en México $380,000 MXN** (IMSS + multa STPS + paro de máquina).
- El 80% de los accidentes avisan antes: operar sin lentes, sin casco, manos cerca del chuck girando, llave de chuck olvidada.
- Los sistemas industriales de seguridad con visión cuestan $10k - $25k USD por máquina. Impagable para 250,000 talleres PyME en México.
- **Ningún taller mide sus "casi accidentes" (Near Miss).** Sin datos, no hay prevención.

### La Solución: Open Core + Hardware de Borde
Hardware de borde que solo graba y alerta, no detiene la máquina. Sin nube, sin mensualidades de internet.

**Alcance actual (v1) — detección de EPP en tiempo real:**
1. ✅ / ❌ Operador con / sin lentes de seguridad (`no_glasses`)
2. ✅ / ❌ Operador con / sin casco (`no_helmet`)

Corre hoy con lo que ya tenemos: una **Raspberry Pi + una webcam USB sencilla** — sin necesidad de cámara CSI, acelerador Coral, ni torre de luz todavía.

**Roadmap (near-miss, requiere hardware/dataset adicional — no es v1):**
- ⚠️ Mano entrando en ZONA ROJA (calibrada por estación, cerca del chuck/husillo girando)
- ⛔ Uso de guantes en torno (causa #1 de atrapamiento)
- 🔑 Llave de chuck visible cerca del husillo

**Cuando detecta riesgo:** Alerta (consola hoy; torre de luz ROJA cuando se sume el relay) + guarda clip de 15s (7s antes + 8s después) para reporte STPS.

### 🛠️ Hardware

Este proyecto es 100% independiente y no está afiliado a ninguna empresa. Diseñado para ser replicable.

**Ya disponible — con esto corre el MVP de EPP hoy:**

| Componente | Detalle |
| :--- | :--- |
| Cómputo | Raspberry Pi (ya disponible) |
| Cámara | Webcam USB sencilla (ya disponible) |
| Alerta | Consola (`alert_output: "mock"`) — sin torre de luz todavía |

**Kit completo (roadmap, ~$8,000 MXN, para near-miss + alerta física):**

| Componente | Modelo Recomendado | Costo MX aprox |
| :--- | :--- | :--- |
| Cómputo | Raspberry Pi 5 8GB | $2,160 MXN |
| Acelerador IA | Google Coral USB Accelerator | $5,205 MXN |
| Cámara | Arducam IMX477 12MP + Lente 6mm CS | $1,587 MXN |
| Alerta | Torre Andon 12V Verde/Rojo + Relay | $800 - $1,200 MXN |
| **TOTAL** | | **~$8,000 MXN (~$400 USD)** |

> Alternativa Pro: NVIDIA Jetson Orin Nano Super Dev Kit (~$5,380 MXN) en vez del combo Pi + Coral, si se necesita más potencia por estación.

### 📍 Estado actual del proyecto

**Hardware mínimo: ✅ confirmado.** Ya se cuenta con una **Raspberry Pi + una webcam USB sencilla** — el pipeline apunta a ese hardware por default (`camera_source: "webcam"`, `inference_backend: "pt"`, corre en la CPU ARM de la Pi, sin necesitar OpenVINO ni el Coral USB Accelerator).

**Resultados actuales (Fase 0, en curso):**
- Pipeline end-to-end implementado y probado: `CameraSource → Detector → rules_engine → AlertOutput + ClipWriter`, con las interfaces (`webcam`, `video_file`, alerta de consola) corriendo sin depender de ningún componente pendiente del kit.
- Alcance de detección fijado a **2 clases de EPP**: `no_glasses` (sin lentes) y `no_helmet` (sin casco) — evaluadas con umbral de confianza configurable por estación.
- Config de estación (`config/torno_01.json`, `torno_02.json`) validado con Pydantic para la Raspberry Pi + webcam ya disponibles.
- Cada evento genera su clip (7s antes + 8s después) y su JSON sidecar con el contrato de datos para reporte STPS.
- 27 tests unitarios/integración en verde (`pytest`) + lint limpio (`ruff check .`), corriendo en CI en cada push.
- Pendiente para detección real en vivo: cargar un modelo público de EPP (Roboflow) en `models/best.pt` — hoy el pipeline se valida con detecciones simuladas en los tests, todavía no hay pesos de modelo (a propósito: nunca se commitean a git).

**Próximas etapas:**
1. **Step 4 (inmediato):** bajar un modelo YOLOv8n pre-entrenado de PPE (lentes + casco) de Roboflow Universe a `models/best.pt` y correr `python app.py --mode demo` con la webcam real de la Pi.
2. **Step 7:** grabar `assets/demo_torno_sin_lentes.gif` con el pipeline real corriendo en la Raspberry Pi + webcam.
3. **Fase 1:** documentar y entrenar un modelo propio de EPP (fine-tune en Colab) con datasets públicos combinados.
4. **Fase 2 (roadmap):** sumar el resto del kit (Coral USB Accelerator, cámara CSI, relay + torre Andon) y retomar las reglas de near-miss (guante en torno, mano en zona roja, llave de mandril).

El diseño completo — arquitectura, orden de build, y las decisiones técnicas — vive en:

- [`CLAUDE.md`](./CLAUDE.md) — guía de arquitectura y reglas del proyecto para desarrollo asistido por IA.
- [`docs/taller-seguro-vision-blueprint.md`](./docs/taller-seguro-vision-blueprint.md) — blueprint técnico completo (stack, modelo de datos, build order paso a paso).

### 🚀 Instalación (una vez implementado el pipeline de demo)

```bash
git clone https://github.com/diegomiranda06/taller-seguro-vision.git
cd taller-seguro-vision
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py --mode demo --zona_config config/torno_01.json
```

## Licencia

Apache 2.0 — ver [`LICENSE`](./LICENSE).
