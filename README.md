# Taller Seguro Vision 🦺🤖 - Detección de Near Miss en Tornos y Fresadoras

> Un sistema open-source de bajo costo con IA que evita amputaciones y accidentes en talleres metal-mecánicos. 100% offline, < $400 USD por estación.

![Status](https://img.shields.io/badge/status-en%20dise%C3%B1o%20(blueprint)-yellow)
![Hardware](https://img.shields.io/badge/hardware-Jetson%20Orin%20Nano%20%2F%20Raspberry%20Pi%205-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Hecho en México](https://img.shields.io/badge/Hecho%20en-M%C3%A9xico-red)

### 🎥 Demo - 15 segundos
> *Pendiente: GIF del prototipo (Fase 0, sin hardware) detectando sin lentes y prendiendo la alerta.*
> `assets/demo_torno_sin_lentes.gif`

### El Problema es Gigante y Nadie lo Mide
- **1 accidente en torno/fresadora cuesta en México $380,000 MXN** (IMSS + multa STPS + paro de máquina).
- El 80% de los accidentes avisan antes: operar sin lentes, manos cerca del chuck girando, llave de chuck olvidada.
- Los sistemas industriales de seguridad con visión cuestan $10k - $25k USD por máquina. Impagable para 250,000 talleres PyME en México.
- **Ningún taller mide sus "casi accidentes" (Near Miss).** Sin datos, no hay prevención.

### La Solución: Open Core + Hardware de Borde
Hardware de borde que solo graba y alerta, no detiene la máquina. Sin nube, sin mensualidades de internet.

**Detecta en tiempo real:**
1. ✅ / ❌ Operador con / sin lentes de seguridad
2. ⚠️ Mano entrando en ZONA ROJA (calibrada por estación, cerca del chuck/husillo girando)
3. ⛔ Uso de guantes en torno (causa #1 de atrapamiento)
4. 🔑 Llave de chuck visible cerca del husillo

**Cuando detecta riesgo:** Torre de luz ROJA + guarda clip de 15s (7s antes + 8s después) para reporte STPS.

### 🛠️ Hardware - Kit de ~$8,000 MXN

Este proyecto es 100% independiente y no está afiliado a ninguna empresa. Diseñado para ser replicable.

| Componente | Modelo Recomendado | Costo MX aprox |
| :--- | :--- | :--- |
| Cómputo | Raspberry Pi 5 8GB | $2,160 MXN |
| Acelerador IA | Google Coral USB Accelerator | $5,205 MXN |
| Cámara | Arducam IMX477 12MP + Lente 6mm CS | $1,587 MXN |
| Alerta | Torre Andon 12V Verde/Rojo + Relay | $800 - $1,200 MXN |
| **TOTAL** | | **~$8,000 MXN (~$400 USD)** |

> Alternativa Pro: NVIDIA Jetson Orin Nano Super Dev Kit (~$5,380 MXN) en vez del combo Pi + Coral, si se necesita más potencia por estación.

### 📍 Estado actual del proyecto

Este repo arranca en **Fase 0**: un pipeline de detección corriendo en laptop (webcam, sin hardware físico) para validar el concepto y producir el demo antes de invertir en el kit. El diseño completo — arquitectura, orden de build, y las decisiones técnicas — vive en:

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
