# Firevolt AI Camera Detector (Detector de Incendios con Cámara AI)

## Descripción General del Proyecto

Firevolt es un sistema de cámara inteligente basado en IA, diseñado para detectar incendios y comunicar alertas a usuarios o robots (por ejemplo, un robot bombero). El proyecto está orientado al aprendizaje sobre sistemas de visión, detección con IA y robótica conectada en red. Es extensible y puede integrarse con hardware como microcontroladores ESP32S3.

---

## Características

- **Detección de Incendios con IA:** Utiliza una cámara y un modelo de IA para detectar fuego en tiempo real.
- **Comunicación en Red:** Envía alertas a usuarios u otros robots cuando se detecta fuego.
- **Configuración Flexible de Red:** Permite configurar WiFi mediante variables de entorno y archivos `.env`.
- **Código Modular en Python:** Fácil de extender e integrar.
- **Integración con Edge Impulse (Próximamente):** Se planea integrar modelos Edge Impulse para inferencia optimizada.
- **Soporte de Red Cerrada (Próximamente):** El ESP32S3 podrá crear su propia red WiFi para comunicación directa entre robots.

---

## Estructura del Proyecto

- **boot.py:** Inicializa la conexión WiFi al arrancar el dispositivo, gestiona reintentos y errores.
- **main.py:** Controla la cámara ESP32, inicia el servidor de streaming MJPEG y gestiona autenticación básica.
- **env.py:** Archivo generado automáticamente con las credenciales WiFi.
- **loadEnv.py:** Convierte un archivo `.env` en `env.py` para uso en MicroPython.
- **Server/**: Contiene el servidor de IA que recibe el stream de la cámara y realiza inferencia con YOLO.
- **Start_AI.py:** Recibe el stream MJPEG, ejecuta el modelo YOLO y muestra los resultados en tiempo real.

---

## Instalación y Configuración

### 1. Clonar el Repositorio

```sh
git clone <repo-url>
cd AI-Camera-detector
```

### 2. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente formato (sin comillas):

```env
WIFI_SSID=NombreDeTuWiFi
WIFI_PASS=ContraseñaDeTuWiFi
```

Ejecuta el script para generar `env.py`:

```sh
python loadEnv.py
```

### 3. Configuración del Entorno Python

Crea y activa un entorno virtual, luego instala dependencias:

```sh
python -m venv tf-env
source tf-env/bin/activate  # O usa el comando correspondiente a tu sistema
pip install -r requirements.txt
```

### 4. Firmware ESP32S3

- Flashea el ESP32S3 con el firmware adecuado.
- Sube los archivos `boot.py`, `main.py` y `env.py` al dispositivo.
- Configura el ESP32S3 en modo estación o punto de acceso según tu red.

### 5. Servidor de IA (Server/)

- Navega a la carpeta `Server/`.
- Instala dependencias necesarias (verifica `requirements.txt`).
- Edita la URL en `Start_AI.py` para que apunte a la IP de tu ESP32-CAM.
- Ejecuta el servidor:

```sh
python Start_AI.py
```

---

## Flujo de Comunicación

1. El ESP32-CAM se conecta a la red WiFi y comienza a transmitir video MJPEG.
2. El servidor de IA recibe el stream, ejecuta el modelo YOLO y detecta incendios.
3. Si se detecta fuego, se pueden enviar alertas a otros robots o usuarios.

---

## Solución de Problemas

- **WiFi:** Verifica que el SSID y la contraseña sean correctos en `.env` y que el ESP32 esté dentro del alcance de la red.
- **Streaming:** Asegúrate de que la IP y el puerto en `Start_AI.py` coincidan con los del ESP32-CAM.
- **Dependencias:** Instala todos los paquetes requeridos en el entorno virtual.
- **Firmware:** Si la cámara o la red no funcionan, reinicia el ESP32 o vuelve a flashear el firmware.

---

## Licencia

Este proyecto es para fines educativos. Consulta LICENSE para más detalles.
