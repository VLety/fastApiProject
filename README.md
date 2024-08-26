# PoC-Prototype API server solution based on FastAPI framework.
## Extended description: Applied solutions for API server based on: FastAPI with Swagger UI, SQLite DB and OAuth2 authorization with Password (and hashing), Bearer with JWT tokens together with Role-based access control (RBAC) permissions model.
#### Purpose: Intended for educational and promotional purposes
#### Audience: Junior-Middle level
## Project Tech stacks:
* FastAPI as a base framework https://fastapi.tiangolo.com/
* SQLAlchemy V2 https://www.sqlalchemy.org/
* Pydantic V2 https://docs.pydantic.dev/latest/#pydantic
* Annotated(typing) https://docs.python.org/3/library/typing.html#typing.Annotated
### FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints. [More details]([docs/CONTRIBUTING.md](https://fastapi.tiangolo.com))
## Project features:
### Blabla
## Project setup steps for a basic AWS Ubuntu 24.04 LTS server:

For analisys: https://dylancastillo.co/posts/fastapi-nginx-gunicorn.html#step-5-configure-nginx
https://docs.gunicorn.org/en/latest/deploy.html#systemd

### Update system
```
sudo apt update && sudo apt upgrade -y
```
### Install NGINX
```
sudo apt -y install nginx
```
### Install GIT
```
sudo apt install git
```
### Check Python version (3.12.3) and install Pip3 & Venv
```
python3 -V
sudo apt -y install build-essential libssl-dev libffi-dev python3-dev
sudo apt -y install python3-pip
sudo apt -y install python3-venv
```
### Clone project from GitHub repository
https://stackoverflow.com/questions/2505096/clone-a-private-repository-github
```
git clone https://VLety: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@github.com/VLety/fastApiProject.git
```
### Move to the project folder
```
cd fastApiProject
```
### Create a random secret key that will be used to sign the JWT tokens
```
openssl rand -hex 32
```
Copy new SECRET_KEY to the project config.json file:
```
"auth": {
    "SECRET_KEY": "copy&paste new random secret key here",
```
> [!WARNING]
> Do not use the default SECRET_KEY for production environments!

> [!CAUTION]
> SECRET_KEY is very important data from security point of view and we must keep it safe.

### Creating lightweight Python “virtual environments” - VENV:
https://docs.python.org/3/library/venv.html
```
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies for active VENV:
```
pip3 install "fastapi[standard]"
pip3 install SQLAlchemy
pip3 install pyjwt
pip3 install "passlib[bcrypt]"
pip3 install "fastapi[standard]"
```

### Start project for active VENV
```
uvicorn main:app --host 127.0.0.1 --port 8000
```

### Install CertBOT
```
sudo apt install snapd
sudo snap install --classic certbot
sudo certbot --nginx
```
### Restart NGINX
```
sudo systemctl restart nginx
```
### Setup Systemd
A tool that is starting to be common on linux systems is Systemd. It is a system services manager that allows for strict process management, resources and permissions control.
```
sudo nano /etc/systemd/system/fastApiProject.service
```
Type:
```
[Unit]
Description=Gunicorn instance to serve fastApiProject
After=network.target

[Service]
# the specific user that our service will run as
User=ubuntu
Group=ubuntu
# this user can be transiently created by systemd
# DynamicUser=true

# set project & venv PATH
WorkingDirectory=/home/ubuntu/fastApiProject
Environment="PATH=/home/ubuntu/fastApiProject/venv/bin"

# RUN instance
ExecStart=/home/ubuntu/fastApiProject/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000

# Support parameters
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

# if your app does not need administrative capabilities, let systemd know
ProtectSystem=strict

[Install]
WantedBy=multi-user.target
```
Save Ctrl + o and exit Ctrl + y
```
sudo systemctl daemon-reload
```
Set service to autoload when server starts
```
sudo systemctl enable fastApiProject.service
```
Start service
```
sudo systemctl start fastApiProject.service
```
Check service status
```
sudo systemctl status fastApiProject.service
```
![image](https://github.com/user-attachments/assets/5fa696b6-d8cc-4330-9de4-1d277f2b1e47)

## Useful commands:
### VENV
```
source venv/bin/activate
```
```
deactivate
```
### NGINX
```
sudo systemctl restart nginx
```
> [!NOTE]
> Useful information that users should know, even when skimming content.

> [!TIP]
> Helpful advice for doing things better or more easily.

> [!IMPORTANT]
> Key information users need to know to achieve their goal.

> [!WARNING]
> Urgent info that needs immediate user attention to avoid problems.

> [!CAUTION]
> Advises about risks or negative outcomes of certain actions.

https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
