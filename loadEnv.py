from pathlib import Path

def load_dotenv(dotenv_path=".env"):
    env = {}
    with open(dotenv_path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
               key, val = line.strip().split("=", 1)
               env[key.strip()] = val.strip()
    return env

def generate_env_py(env_vars, out_path="env.py"):
    with open(out_path, "w") as f:
        for key, val in env_vars.items():
            f.write(f'{key} = "{val}"\n')

if __name__ == "__main__":
    env_vars = load_dotenv(".env")
    generate_env_py(env_vars)
    print("env.py genreated")