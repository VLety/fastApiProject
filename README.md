# REST API server solution based on FastAPI framework
> Recommended for PoC or Prototype approach.

> [!NOTE]
> * Purpose: Intended for educational and promotional needs.
> * Audience: Python Junior+ and Middle level with linux DevOps skills.
> * Tech description: FastAPI & Swagger UI (with automatic interactive documentation), SQLite3 database, OAuth2 authorization with Password (and hashing), Bearer with JWT tokens together with Role-based access control (RBAC) permissions model.

> [!TIP]
> This solution is presented in the most easy-to-learn form without using Docker delivery technology or an additional full-fledged WSGI HTTP server such as Gunicorn or Redis to support caching. We will simply use the Uvicorn ASGI web server that is already built into FastAPI framework with NGINX as a proxy server. And this deployment option will be sufficient for PoC, Prototype, MVP or even production environment purposes. [Read more](https://fastapi.tiangolo.com/deployment/concepts/#deployments-concepts) about FastAPI recommended deployment.

> [!NOTE]
> What is the difference between [WSGI](https://wsgi.tutorial.codepoint.net/intro) and [ASGI](https://asgi.readthedocs.io/en/latest/) server interface specification? In simple words: WSGI is synchronous, handling one request at a time, and blocking execution until processing is complete. ASGI is asynchronous, handling multiple requests concurrently without blocking other requests.

> [!TIP]
> Using Nginx as a Proxy in front of your WSGI or ASGI server may not be necessary for PoC or Prototype approach, but is recommended for additional resilience and full-fledged production environment. Nginx can deal with serving your static media and buffering slow requests, leaving your application servers free from load as much as possible, add more security etc.

> [!IMPORTANT]
> However, for full use of the solution in a production environment, it is recommended to add Docker delivery technology, use PostgreSQL database instead of SQLite3 (AWS RDS will be good enough), optionally add Gunicorn WSGI server with automatic multiple worker process management in front of Uvicorn ASGI if it is really necessary according to the project requirements, but in most cases Uvicorn ASGI is our choice [read more](https://www.geeksforgeeks.org/fast-api-gunicorn-vs-uvicorn/).

## Project Tech stacks:
* Python 3.10+
* FastAPI as a base project framework [read more](https://fastapi.tiangolo.com)
* SQLAlchemy V2 as SQL toolkit and Object Relational Mapper [read more](https://www.sqlalchemy.org)
* Pydantic V2 as schemas builder [read more](https://docs.pydantic.dev/latest/#pydantic)
* Annotated(typing) for metadata management [read more](https://docs.python.org/3/library/typing.html#typing.Annotated)
* PyJWT for encode and decode JSON Web Tokens (JWT) [read more](https://pyjwt.readthedocs.io/en/stable/#welcome-to-pyjwt)
* Passlib[bcrypt] for password hashing [read more](https://passlib.readthedocs.io/en/stable/install.html#optional-libraries)
* Uvicorn as ASGI web server [read more](https://www.uvicorn.org/)
* NGINX as Reverse Proxy & TLS Termination service [read more](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
* Certbot as Let’s Encrypt certificates manager [read more](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
  
## Project specification and standards:
* OpenAPI Specification v3.1 [read more](https://spec.openapis.org/oas/latest.html)
* OAuth 2.0 authorization protocol [read more](https://oauth.net/2/)
* Role-Based Access Control (RBAC) permissions model [read more](https://auth0.com/docs/manage-users/access-control/rbac)
  
## Project features:
* Full-fledged RESTful API server
* JWT token authentication with expiration period and [optional authorization scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/#oauth2-scopes)
* Flexible project configuration via [config files](config/) 
* CRUD operations for 3 tables: Users and Employees with relational link to Tickets
* PATCH (partially update a resource request) for User's name & password changing
* RBAC permissions model for each API endpoint
  
## Setup and deploy project to the "clear" AWS Ubuntu EC2 Instance:
> [!NOTE]
> We will not consider the installation of EC2 instance in this article as this is a separate topic, assuming that the necessary knowledge already exists. For PoC or Prototype project deployments, the [AWS Free Tier](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all) will be sufficient [read more](https://aws.amazon.com/ec2/getting-started/).

> [!TIP]
> For the EC2 instance, it is recommended to choose the Ubuntu 24.04 LTS OS type as it comes with Python 3.12 pre-installed.

> To proceed further, log in to the Linux console...

#### Update system
```
sudo apt update && sudo apt upgrade -y
```
#### Install NGINX
```
sudo apt -y install nginx
```
#### Install CertBOT
```
sudo apt install snapd
sudo snap install --classic certbot
```
#### Install GIT
```
sudo apt -y install git
```
#### Install common Python Dependencies
```
sudo apt -y install build-essential libssl-dev libffi-dev python3-dev
sudo apt -y install python3-pip
sudo apt -y install python3-venv
```
#### Clone a project from a GitHub repository
```
git clone https://VLety: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@github.com/VLety/fastApiProject.git
```
#### Generate a random secret key that will be used to sign JWT tokens.
```
openssl rand -hex 32
```
#### Copy new SECRET_KEY to the project ./config/config.json file:
```
"auth": {
    "SECRET_KEY": "copy&paste new random secret key here",
```
> [!WARNING]
> Do not use the project default SECRET_KEY for production environments!

> [!CAUTION]
> SECRET_KEY is very important data from security point of view, and we must keep it safe.
#### Move to the project folder
```
cd fastApiProject
```

#### Create and activate lightweight Python “virtual environments” (VENV) [read more](https://docs.python.org/3/library/venv.html):
```
python3 -m venv venv
source venv/bin/activate
```

#### Install project dependencies (VENV must be in active mode):
```
pip3 install "fastapi[standard]"
pip3 install SQLAlchemy
pip3 install pyjwt
pip3 install "passlib[bcrypt]"
```

#### Run project for testing purpose (VENV must be in active mode)
```
uvicorn main:app --host 127.0.0.1 --port 8000
```
> [!TIP]
> We should see something like this:
> ![image](https://github.com/user-attachments/assets/c445a34e-60bd-475f-adc4-1fe13f930330)
> 

#### Run Certbot for NGINX
```
sudo certbot --nginx
```

#### Restart NGINX
```
sudo systemctl restart nginx
```
#### Setup Systemd to manage API server as service with following actions: start, restart, stop and status
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
