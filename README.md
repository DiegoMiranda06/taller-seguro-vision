# Taller Seguro Vision 🦺🤖 - Detección de Near Miss en Tornos y Fresadoras

> Sistema open-source de visión por computadora que registra los "casi accidentes" en tornos y fresadoras de talleres metal-mecánicos. Corre 100% offline sobre hardware de borde: el video nunca sale del dispositivo.

![Status](https://img.shields.io/badge/status-Fase%201%3A%20dataset%20%2F%20modelo-yellow)
![Hardware](https://img.shields.io/badge/hardware-Raspberry%20Pi%20%2B%20webcam%20USB-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Hecho en México](https://img.shields.io/badge/Hecho%20en-M%C3%A9xico-red)

### 🎥 Demo - 15 segundos
📹 [Video del prototipo funcionando](https://www.youtube.com/watch?v=D5mMzkzEC_s) — Raspberry Pi + webcam USB detectando y alertando en vivo.

> *Pendiente: GIF del prototipo corriendo en la Raspberry Pi + webcam USB (hardware mínimo ya disponible) detectando sin lentes y prendiendo la alerta.*
> `assets/demo_torno_sin_lentes.gif`

### El problema

- En 2024 el IMSS registró **418,514 accidentes de trabajo en jornada**, con 859 defunciones, sobre una población de 22,065,677 trabajadores asegurados en el Seguro de Riesgos de Trabajo. <sup>[1](#fuentes)</sup>
- Las **amputaciones traumáticas de muñeca y mano son la segunda causa nacional de incapacidad permanente** derivada de accidente de trabajo. <sup>[2](#fuentes)</sup>
- El accidente registrado es solo la parte visible: un estudio con información de las 27 delegaciones del IMSS estimó un **subregistro promedio nacional de 26.3%**, con delegaciones de hasta 68%. <sup>[3](#fuentes)</sup> Si los accidentes consumados se subregistran así, los *casi accidentes* —operar sin lentes, acercar la mano al mandril girando, usar guantes en el torno, dejar la llave puesta— sencillamente no existen como dato.
- El problema se concentra donde menos capacidad hay: México tiene **78,328 establecimientos de fabricación de productos metálicos**, y **74,197 de ellos (94.7%) tienen de 0 a 10 personas ocupadas**. <sup>[4](#fuentes)</sup>

**Sin registro no hay prevención.** Un taller no puede corregir lo que no puede ver, y hoy ningún taller pequeño mide sus near-miss.

### La solución

Dispositivo de borde que **observa, alerta y registra**. No detiene la máquina ni sustituye las guardas físicas que exige la NOM-004-STPS-1999 <sup>[6](#fuentes)</sup> — agrega una capa de detección de conducta de riesgo y de evidencia. Sin nube, sin suscripción, sin conexión a internet.

**Detecta en tiempo real:**
1. ✅ / ❌ Operador con / sin lentes de seguridad
2. ⚠️ Mano entrando en ZONA ROJA (polígono calibrado por estación, cerca del mandril/husillo girando)
3. ⛔ Uso de guantes en torno — práctica prohibida en operación de torno por riesgo de atrapamiento
4. 🔑 Llave de mandril visible cerca del husillo

**Cuando detecta riesgo:** enciende la torre de luz roja y guarda un clip de 15 s (7 s antes + 8 s después) con un JSON sidecar que registra `station_id`, `timestamp_utc`, `event_type` y `confidence`.

### Por qué le conviene al taller

Más allá de evitar una lesión, hay un incentivo económico con base legal.

El **artículo 72 de la Ley del Seguro Social** calcula la prima del Seguro de Riesgos de Trabajo multiplicando la siniestralidad de la empresa por un factor de **2.3**. Los centros de trabajo que cuenten con un **Sistema de Administración de Seguridad y Salud en el Trabajo acreditado por la STPS** pueden aplicar un factor de **2.2** en su lugar. <sup>[5](#fuentes)</sup> Es una reducción directa y permanente de una cuota que el patrón ya paga sobre toda su nómina.

Los clips con metadata que genera este dispositivo sirven como **evidencia documental** para sostener ese sistema de gestión y para las funciones de evaluación periódica que exige la NOM-030-STPS-2009. <sup>[7](#fuentes)</sup> El cumplimiento deja de ser un trámite aparte y pasa a ser un subproducto de tener el equipo encendido.

### 🛠️ Hardware

Este proyecto es 100% independiente y no está afiliado a ninguna empresa. Diseñado para ser replicable con componentes de catálogo.

**Hardware mínimo: ✅ ya disponible.** Ya se cuenta con una Raspberry Pi + una webcam USB sencilla — con esto el pipeline corre hoy en modo demo (`camera_source: "webcam"`), sin necesitar todavía el acelerador, la cámara CSI ni la torre de luz física del kit completo.

| Componente | Modelo de referencia |
| :--- | :--- |
| Cómputo | Raspberry Pi 5 8GB |
| Acelerador IA | Google Coral USB Accelerator |
| Cámara | Arducam IMX477 12MP + lente 6mm CS |
| Alerta | Torre Andon 12V verde/rojo + relay |

> Alternativa: NVIDIA Jetson Orin Nano Super Dev Kit en vez del combo Pi + Coral, si se necesita más potencia por estación.

> **Sobre costos:** este README no publica precios. Los componentes son commodities cuyo precio varía por proveedor, tipo de cambio y disponibilidad, y cualquier cifra fijada aquí quedaría desactualizada. Cotiza los modelos de referencia con tu distribuidor local al momento de armar el kit.

### 📍 Estado actual del proyecto

**🚧 Fase 1 — Dataset y modelo propio (en curso)**

Con el pipeline de Fase 0 ya validado sobre Raspberry Pi + webcam, el foco actual es construir el dataset y el modelo propios (Steps 8-9 del build order):
- **Step 8 — Plan de dataset:** combinar datasets públicos de PPE (Roboflow Universe) para `no_glasses` / `glove_on_lathe`, y documentar la recolección propia para las clases específicas del proyecto (`hand_in_red_zone`, `chuck_key_visible`), que no existen en datasets públicos.
- **Step 9 — Entrenamiento inicial:** fine-tune de YOLOv8n en Google Colab sobre el dataset combinado, para reemplazar el modelo público genérico por uno propio.

**Lo que todavía no existe, dicho sin rodeos:** el modelo actual es público y genérico, no propio; no hay dataset etiquetado para las dos clases que ningún dataset público cubre; y no hay aún un despliegue medido en un taller real durante un periodo definido.

<details>
<summary><strong>✅ Fase 0 — Demo sin hardware (completada)</strong></summary>
<br>

**Hardware mínimo: ✅ confirmado.** Ya se cuenta con una Raspberry Pi + una webcam USB sencilla — el pipeline de Fase 0 (interfaces de cámara, motor de reglas, buffer circular + grabación de clips) está implementado y testeado, corriendo en modo demo sobre ese hardware, antes de invertir en el resto del kit (acelerador, cámara CSI, torre Andon).

</details>

El diseño completo — arquitectura, orden de build, y las decisiones técnicas — vive en:

- [`CLAUDE.md`](./CLAUDE.md) — guía de arquitectura y reglas del proyecto para desarrollo asistido por IA.
- [`docs/taller-seguro-vision-blueprint.md`](./docs/taller-seguro-vision-blueprint.md) — blueprint técnico completo (stack, modelo de datos, build order paso a paso).

### 🚀 Instalación

```bash
git clone https://github.com/diegomiranda06/taller-seguro-vision.git
cd taller-seguro-vision
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py --mode demo --zona_config config/torno_01.json
```

## Fuentes

Cada cifra de este README es rastreable a una fuente pública. Se indica el año al que corresponde el dato, porque varias son series que se actualizan.

1. **IMSS, _Memoria Estadística 2024_**, capítulo de Riesgos de Trabajo. Total de riesgos de trabajo en 2024: 610,751 — desglosados en 418,514 accidentes en jornada (859 defunciones), 175,357 accidentes de trayecto y 16,880 enfermedades de trabajo. Población asegurada en el Seguro de Riesgos de Trabajo al cierre de 2024: 22,065,677 trabajadores. <https://www.imss.gob.mx/conoce-al-imss/memoria-estadistica-2024>

2. **_Revista Médica del Instituto Mexicano del Seguro Social_** — estudio de costos directos e indirectos por amputaciones de mano derivadas de accidentes de trabajo, cuyo ranking de causas se basa en la Memoria Estadística del IMSS. <https://revistamedica.imss.gob.mx/index.php/revista_medica/article/view/1928>

3. **"El subregistro potencial de accidentes de trabajo en el Instituto Mexicano del Seguro Social", _Salud Pública de México_.** Estudio transversal con información de las 27 delegaciones del IMSS. **Datos del periodo 1994-2004** — es un estudio histórico, no una medición reciente, y así debe citarse. <https://www.scielo.org.mx/scielo.php?script=sci_arttext&pid=S0036-36342004000300009>

4. **INEGI, Directorio Estadístico Nacional de Unidades Económicas (DENUE)**, corte de mayo de 2025. Subsector SCIAN 332, *Fabricación de productos metálicos*: 78,328 unidades económicas, de las cuales 74,197 tienen de 0 a 10 personas ocupadas. <https://www.economia.gob.mx/datamexico/es/profile/industry/fabricated-metal-product-manufacturing>

5. **Ley del Seguro Social, artículo 72**, y Acuerdo de la STPS que establece los requisitos para la acreditación del Sistema de Administración de Seguridad y Salud en el Trabajo, publicado en el DOF el 19 de marzo de 2002. La vía habitual de acreditación es el Programa de Autogestión en Seguridad y Salud en el Trabajo (PASST). <https://autogestionsst.stps.gob.mx/>

6. **NOM-004-STPS-1999**, *Sistemas de protección y dispositivos de seguridad en la maquinaria y equipo — Instalación*. Exige guardas físicas y dispositivos de bloqueo en partes móviles peligrosas.

7. **NOM-030-STPS-2009**, *Servicios preventivos de seguridad y salud en el trabajo — Funciones y actividades*. Aplica a todos los centros de trabajo del país y obliga a evaluar periódicamente las condiciones de trabajo.

> **Sobre un dato que no existe:** ni el IMSS ni la STPS publican estadísticas de accidentes desagregadas por tipo de máquina, así que **no hay una cifra oficial de "accidentes en torno" en México**. Esa laguna es parte de lo que este proyecto busca atacar: generar el dato que hoy nadie mide.

## Licencia

Apache 2.0 — ver [`LICENSE`](./LICENSE).
