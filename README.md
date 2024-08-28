# REST API server solution based on FastAPI framework with clean AWS EC2 Ubuntu server setup.
Recommended for PoC or Prototype approach.

> [!NOTE]
> * Purpose: Intended for educational and promotional needs.
> * Audience: Python Junior+ and Middle level with linux DevOps skills.
> * Tech description: FastAPI & Swagger UI (with automatic interactive documentation), SQLite3 database, OAuth2 authorization with Password (and hashing), Bearer with JWT tokens together with Role-based access control (RBAC) permissions model.

> [!TIP]
> This solution is presented in the most simple to learn form without using Docker technology or a full-fledged WSGI HTTP Server such as Gunicorn. We will simply use the Uvicorn ASGI web server that is already built into FastAPI framework and this is sufficient for PoC, Prototyping or even MVP purpose. [Read more](https://fastapi.tiangolo.com/deployment/concepts/#deployments-concepts) About FastAPI recommended deployment.

> [!NOTE]
> What is the difference between [WSGI](https://wsgi.tutorial.codepoint.net/intro) and [ASGI](https://asgi.readthedocs.io/en/latest/) server interface specification? In simple words: WSGI is synchronous, handling one request at a time, and blocking execution until processing is complete. ASGI is asynchronous, handling multiple requests concurrently without blocking other requests.

> [!TIP]
> Using Nginx as a TLS Termination Proxy in front of your WSGI or ASGI server may not be necessary for PoC or Prototype approach, but is recommended for additional resilience and full-fledged production environment. Nginx can deal with serving your static media and buffering slow requests, leaving your application servers free from load as much as possible, add more security etc.

> [!IMPORTANT]
> However, for full use of the solution in a production environment, it is recommended to add Docker delivery technology, Gunicorn WSGI HTTP Server with automatic multiple worker process management instead of Uvicorn and a PostgreSQL database (AWS RDS will be good enough).

## Project Tech stacks:
* Python 3.10+
* FastAPI as a base project framework [read more](https://fastapi.tiangolo.com)
* SQLAlchemy V2 SQL toolkit and Object Relational Mapper [read more](https://www.sqlalchemy.org)
* Pydantic V2 as schemas builder [read more](https://docs.pydantic.dev/latest/#pydantic)
* Annotated(typing) for metadata management [read more](https://docs.python.org/3/library/typing.html#typing.Annotated)
* PyJWT for encode and decode JSON Web Tokens (JWT) [read more](https://pyjwt.readthedocs.io/en/stable/#welcome-to-pyjwt)
* Passlib[bcrypt] is a password hashing library for Python [read more](https://passlib.readthedocs.io/en/stable/install.html#optional-libraries)
* Uvicorn is an ASGI web server implementation for Python [read more](https://www.uvicorn.org/)
* NGINX in Reverse Proxy mode [read more](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
## Project specification and standarts:
* OpenAPI Specification v3.1 [read more](https://spec.openapis.org/oas/latest.html)
* OAuth 2.0 authorization protocol [read more](https://oauth.net/2/)
* Role-Based Access Control (RBAC) permissions model [read more](https://auth0.com/docs/manage-users/access-control/rbac)
## Project features:
* RESTful API server with 
* JWT token authentication with expiration period and authorization scopes
* Flexible project configuration via config files
* CRUD operations for 3 tables: Users and Employees with relational link to Tickets
* PATCH (partially update a resource request) for User's name & password changing
* RBAC permissions model for each API endpoint
## Project setup steps for a clear AWS Ubuntu 24.04 LTS EC2 server:
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
sudo apt -y install git
```
### Check Python version (3.12.3) and install general dependencies, Pip3 and Venv
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

### Create and activate project VENV (lightweight Python “virtual environments”) [read more](https://docs.python.org/3/library/venv.html):
```
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies for a new active VENV:
```
pip3 install "fastapi[standard]"
pip3 install SQLAlchemy
pip3 install pyjwt
pip3 install "passlib[bcrypt]"
```
> [!TIP]
> We will not install a full-fledged Gunicorn WSGI HTTP server separately, since we already have a built-in Uvicorn ASGI web server in the FastAPI framework and this is sufficient for our needs.

### Run project in active VENV for testing purpose
```
uvicorn main:app --host 127.0.0.1 --port 8000
```
> [!TIP]
> We should see something like this:
> ![image](https://github.com/user-attachments/assets/c445a34e-60bd-475f-adc4-1fe13f930330)

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
### Setup Systemd to manage API server as service with following actions: start, restart, stop and status
> [!TIP]
> A tool that is starting to be common on linux systems is Systemd. It is a system services manager that allows for strict process management, resources and permissions control.
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
Save Ctrl + o and Exit Ctrl + y
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
> [!TIP]
> We should see something like this:
> ![image](https://github.com/user-attachments/assets/5fa696b6-d8cc-4330-9de4-1d277f2b1e47)

## Useful commands:
### VENV
Manually activate VENV
```
source venv/bin/activate
```
Manually deactivate (exit) VENV
```
deactivate
```
> [!IMPORTANT]
> must be in the project directory like: /home/ubuntu/fastApiProject

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
