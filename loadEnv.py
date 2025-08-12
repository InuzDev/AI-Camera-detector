# loadEnv.py
"""
Este script convierte un archivo .env en un archivo env.py compatible con MicroPython/ESP32.
Permite cargar variables de entorno (como credenciales WiFi) en el entorno del microcontrolador.

Uso:
  1. Edite el archivo .env en el directorio raíz del proyecto.
  2. Ejecute este script: python loadEnv.py
  3. Se generará env.py con las variables necesarias para el firmware.
"""

from pathlib import Path

def load_dotenv(dotenv_path=".env"):
    """
    Carga variables de un archivo .env en un diccionario.
    Args:
        dotenv_path (str): Ruta al archivo .env
    Returns:
        dict: Variables de entorno clave-valor
    """
    env = {}
    with open(dotenv_path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
               key, val = line.strip().split("=", 1)
               env[key.strip()] = val.strip()
    return env

def generate_env_py(env_vars, out_path="env.py"):
    """
    Genera un archivo env.py a partir de un diccionario de variables.
    Args:
        env_vars (dict): Variables de entorno
        out_path (str): Ruta de salida para env.py
    """
    with open(out_path, "w") as f:
        for key, val in env_vars.items():
            f.write(f'{key} = "{val}"\n')

if __name__ == "__main__":
    env_vars = load_dotenv(".env")
    generate_env_py(env_vars)
    print("env.py generado")
