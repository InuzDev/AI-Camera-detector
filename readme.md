# AI Camera to detect fire - Firevolt project

> Due the my pc being low-end I couldn't complete the AI training correctly.
> NOTE: Activate the virtual environment before installing packages or running scripts.

## Environment variables preparation template

```env
WIFI_SSID <This is your WiFi ID/Name>
WIFI_PASS <This is your WiFi Connection password>
```

## What is this about?

This project made to learn how cameras works and how AI is made. to try and learn, I decided to try and code a camera that detects fires and send a signal to the user or to another robot.

If the other robot is configured to turn off the fire (Like a firefighter robot), then the camera send a signal to the robot to share the location of the fired. The other robot should have a integrated camera too.

## Preparation of the `boot.py` file

In this file, you can see there a line of code where you required to put your network connection. For that, we opted to use .env files to not share the information between git commits. (which I sadly did with the initialization of this repository)

To properly add your network information and avoid sharing it between commits, use the `loadEnv.py` file.

### Steps to create the .env file

First, we create a .env file (Which is ignore by .gitignore), in that file we put

```env
WIFI_SSID=<Network Name>
WIFI_PASS=<Network Password>
```

Now, after introducing the information. We now just run the loadEnv.py with `py loadEnv.py` in the command line.
> If `py loadEnd.py` doesn't work. Try `python loadEnv.py`.

## Activating the Python Virtual Environment

This guide shows how to activate the Python virtual environment `tf-env/` on different operating systems and shells.

---

### the virtual environment and install the packages

```shell
python -m venv tf-env
pip install -r requirements.txt
```

## Windows

### CMD (Command Prompt)

```cmd
tf-env\Scripts\activate.bat
```

### Powershell

```shell
.\tf-env\Scripts\Activate.ps1
```

> If you get issues running this command, run this command once -> `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Git Bash or WSL

```bash
source tf-env/Scripts/Activate
```

### Linux / MacOS

```bash
source tf-env/bin/activate
```

To deactivate the virtual environment just run `deactivate`
