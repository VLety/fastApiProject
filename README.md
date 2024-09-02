# REST API server solution based on FastAPI framework
> Recommended for PoC or Prototype approach

> [!IMPORTANT]
> * Purpose: Intended for educational and promotional needs.
> * Audience: Python Junior+ or Middle level with linux DevOps skills.
> * Tech features: FastAPI RESTful server with Swagger UI, SQLite3 database, OAuth2 authorization with Bearer JWT token combined with a Role-based access control (RBAC) permissions for every endpoint.

> [!Note]
> This solution is presented in the most easy-to-learn form without using Docker delivery technology or an additional full-fledged WSGI HTTP server such as Gunicorn. We will simply use the Uvicorn ASGI web server that is already built into FastAPI framework with NGINX as a proxy server. And this deployment option will be sufficient for PoC, Prototype, MVP or even production environment purposes. [Read more](https://fastapi.tiangolo.com/deployment/concepts/#deployments-concepts) about FastAPI recommended deployment.

> [!Note]
> What is the difference between [WSGI](https://wsgi.tutorial.codepoint.net/intro) and [ASGI](https://asgi.readthedocs.io/en/latest/) server interface specification? In simple words: WSGI is synchronous, handling one request at a time, and blocking execution until processing is complete. ASGI is asynchronous, handling multiple requests concurrently without blocking other requests.

> [!TIP]
> Using Nginx as a Proxy in front of your WSGI or ASGI server may not be necessary for PoC or Prototype approach, but is recommended for additional resilience and full-fledged production environment. Nginx can deal with serving your static media and buffering slow requests, leaving your application servers free from load as much as possible, add more security etc.

> [!CAUTION]
> However, to fully utilize the solution in a production environment, it is recommended to add Docker delivery technology, use PostgreSQL database instead of SQLite3 (AWS RDS will be enough), optionally add Redis for caching support and Gunicorn WSGI server with automatic management of multiple worker processes in front of Uvicorn ASGI server, if it is really necessary according to the project requirements.

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
* Certbot as Let’s Encrypt SSL certificate manager [read more](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
  
## Project specification and standards:
* OpenAPI Specification v3.1 [read more](https://spec.openapis.org/oas/latest.html)
* OAuth 2.0 authorization protocol [read more](https://oauth.net/2/)
* Role-Based Access Control (RBAC) permissions model [read more](https://auth0.com/docs/manage-users/access-control/rbac)
  
## Project features:
* Full-fledged RESTful API server with Swagger UI
* JWT token authentication with expiration period and [optional authorization scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/#oauth2-scopes)
* Flexible project customization and tuning using configuration files
* CRUD operations on 3 objects: User, Employee and Ticket which is relational to Employee
* PATCH operations on User object for name & password changing
* RBAC permissions model for each API endpoint

> [!IMPORTANT]
> In our project setup and installation we will use the name "fastApiProject" everywhere and my domain name is fastapiproject.key-info.com.ua, which is done for clarity. But for your needs you should of course use your own names and your own domain.

## Setup and deploy project to the "clear" AWS Ubuntu EC2 Instance:
> [!NOTE]
> We will not consider the installation of EC2 instance via AWS console in this article as this is a separate topic, assuming that the necessary knowledge already exists. For PoC or Prototype project deployments, the [AWS Free Tier](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all) will be sufficient [read more](https://aws.amazon.com/ec2/getting-started/).

> [!TIP]
> For the EC2 instance, it is recommended to choose the Ubuntu 24.04 LTS OS type as it comes with Python 3.12 pre-installed bur you can try other linux OS.

> To proceed further, log in to the Linux console...

#### Update system
```
sudo apt update && sudo apt upgrade -y
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

### Initial project configuration

#### Clone a project from a GitHub repository
```
git clone https://VLety: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@github.com/VLety/fastApiProject.git
```
Let's go to our project catalog
```
cd /home/ubuntu/fastApiProject/
```
#### Create lightweight Python “virtual environments” (VENV) [read more](https://docs.python.org/3/library/venv.html):
```
python3 -m venv venv
```
#### Activate VENV
```
source venv/bin/activate
```
#### Install project dependencies:
VENV must be in Active mode
```
pip3 install "fastapi[standard]"
pip3 install SQLAlchemy
pip3 install pyjwt
pip3 install "passlib[bcrypt]"
```
#### Deactivate VENV
```
deactivate
```

#### Setup configuration files
> [!CAUTION]
> Never add configuration files to the repository! This is due to potential security issues and problems with updates delivery.

> [!IMPORTANT]
> There are many approaches to avoid config problem - we will use the initial creation of configuration files from the project templates.

Copy all 4 config template files from ./setup/config to the base project's ./config folder and rename them by removing the "template" extension.
```
cp -f /home/ubuntu/fastApiProject/setup/config/*.template /home/ubuntu/fastApiProject/config/
cd /home/ubuntu/fastApiProject/config/
mv -f config.json.template config.json
mv -f permissions.json.template permissions.json
mv -f schemas.json.template schemas.json
mv -f log.ini.template log.ini
```
> [!NOTE]
> As a result, we should have such a list of files:
> ![image](https://github.com/user-attachments/assets/1881eaa7-63d2-47f5-9cdc-7d33991099a5)

#### Generate a new SECRET_KEY that will be used to encrypt/decrypt JWT tokens
```
openssl rand -hex 32
```
#### Copy new SECRET_KEY to the project /config/config.json file
```
"auth": {
    "SECRET_KEY": "paste new secret key here",
```
> [!WARNING]
> Do not use the project default SECRET_KEY for production environment!

> [!TIP]
> Optionally via initial setup you can change necessary project settings for:
> * config.json: The file is intended to store the main project configuration settings.
> * schemas.json: The file is used to configure Pydantic JSON schemas validation.
> * permissions.json: The file is used to configure RBAC permissions for API endpoints.

#### Setup password for default users
We have 3 default users: admin, manager and employee. So please open the ./setup/setup.json file, change the passwords for all 3 users and save the file with the new passwords.
```
sudo nano /home/ubuntu/fastApiProject/setup/setup.json
```
> [!NOTE]
> ![image](https://github.com/user-attachments/assets/c5cc0078-0d87-4271-8b0d-98ea54ad538a)
> Save Ctrl+o, Exit Ctrl+x

> [!TIP]
> Project password requirements: Minimum password length is 8 characters. Maximum password length is 16 characters. At least one uppercase and one lowercase letter, one number and one special character.

#### Update new passwords in database
Activate project's VENV
```
cd /home/ubuntu/fastApiProject/
source venv/bin/activate
```
Run password update
```
python /home/ubuntu/fastApiProject/setup/change_users_password.py
```
> [!NOTE]
> We should see something like this:
> ![image](https://github.com/user-attachments/assets/8c26f82b-b08d-4592-b174-15aa91649055)

#### Run project for testing purpose
> VENV must be in Active mode
```
uvicorn main:app --host 127.0.0.1 --port 8000
```
> [!NOTE]
> We should see something like this:
> ![image](https://github.com/user-attachments/assets/c445a34e-60bd-475f-adc4-1fe13f930330)

> [!TIP]
> **Initial project configuration is complete successfully!**

#### Add Systemd service
> [!TIP]
> A tool that is starting to be common on linux systems is Systemd. It is a system services manager that allows for strict process management, resources and permissions control.
> The Linux/Unix socket approach is used to create a communication endpoint and return a file descriptor referencing that endpoint.
> We will use the Systemd service to manage the state of our API server: starting, restarting, stopping and see current status.
> Logging --> https://www.uvicorn.org/settings/#logging

> [Read more](https://www.uvicorn.org/settings/#settings) about Uvicorn RUN instance settings

Create a Systemd service file
```
sudo nano /etc/systemd/system/fastApiProject.service
```
Type:
```
[Unit]
Description=Uvicorn instance to serve fastApiProject
After=network.target

[Service]
# The specific user that our service will run as
# Need R/W/X access to the project folder
User=ubuntu
Group=ubuntu

# Set project & venv PATH
WorkingDirectory=/home/ubuntu/fastApiProject
Environment="PATH=/home/ubuntu/fastApiProject/venv/bin"

# RUN instance
ExecStart=/home/ubuntu/fastApiProject/venv/bin/uvicorn main:app --workers 3 --log-config /home/ubuntu/fastApiProject/config/log.ini --forwarded-allow-ips='*' --uds /tmp/fastApiProject.sock

# Support parameters
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5

# Socket .sock file access type (requires false for NGINX access)
PrivateTmp=false

# This user can be transiently created by systemd
# DynamicUser=true

# If your app does not need administrative capabilities, let systemd know
# ProtectSystem=strict

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

### NGINX setup
```
sudo apt update && sudo apt upgrade -y
sudo apt -y install nginx
```

#### Add the public IP address of EC2 instance to your domain's DNS A record.
> My variant:
> ![image](https://github.com/user-attachments/assets/cd75e648-5fb3-494d-92af-11871afb4807)

### Create NGINX configuration
> [!NOTE]
> FastAPI latency is lower when interacting with NGINX via a socket than when interacting via a port, but both solutions work. We will go the way of interacting with NGINX via a socket.

#### Delete default NGINX configuration file symlink
```
sudo rm /etc/nginx/sites-enabled/default
```

#### Create new NGINX configuration file
sudo nano /etc/nginx/sites-available/fastApiProject
```
server {
    listen 80;
    
    # Project server URL
    server_name	fastApiProject.key-info.com.ua;

    location / {

		# Unix Socket mode
		proxy_pass http://fastApiProject;
		proxy_redirect off;
		proxy_buffering off;
		proxy_ignore_client_abort on;

		# NGINX timeout should be about 5 seconds longer than the same Uvicorn setting
		proxy_connect_timeout 65s;
		proxy_read_timeout 65s;
		proxy_send_timeout 65s;
		
		# Proxy header section
		proxy_set_header Host $http_host;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection $connection_upgrade;
		proxy_set_header X-Real-IP $remote_addr;
		
		# NGINX to pass through the 'server' header of upstream server (Uvicorn)
		proxy_pass_header Server;
		
		# Sets the HTTP protocol version for proxying. By default, version 1.0 is used.
		# Version 1.1 is recommended for use with keepalive connections and NTLM authentication. 
		proxy_http_version 1.1;
	}

	# Path for project static files
	location /static {
		root /home/ubuntu/fastApiProject/static;
        }

    # Optional project settings which you need to select at your own discretion
    server_tokens off;
    client_max_body_size 8M;
    keepalive_requests 5000;  
    keepalive_timeout 120;
    set_real_ip_from 10.0.0.0/8;
    set_real_ip_from 172.16.0.0/12;
    set_real_ip_from 192.168.0.0/16;
    real_ip_header X-Forwarded-For;
    real_ip_recursive on;

    gzip on; # gzip settings
    gzip_proxied any;
    gzip_disable "msie6";
    gzip_comp_level 6;
    gzip_min_length 200; # check your average response size and configure accordingly
}

map $http_upgrade $connection_upgrade {
	default upgrade;
    '' close;
}

# Uvicorn service file descriptor referencing
upstream fastApiProject{
    server unix:/tmp/fastApiProject.sock;
}
```
Save Ctrl+o, Exit Ctrl+x

#### Copy NGINX configuration file as symlink to the site-enabled folder
```
sudo ln -sf /etc/nginx/sites-available/fastApiProject /etc/nginx/sites-enabled/fastApiProject
```
#### Restart NGINX
```
sudo systemctl restart nginx.service
```
#### Check NGINX status
```
sudo systemctl status nginx.service
```
> [!NOTE]
> We should see something like this:
> ![image](https://github.com/user-attachments/assets/222a6303-86b4-408e-9fe2-4e80e76110d0)

#### Check the project's HTTP URL
> My variant: http://fastapiproject.key-info.com.ua/api/v1/docs
> ![image](https://github.com/user-attachments/assets/e6e4c0d6-8737-4b12-9fce-f4ea4c44db0b)

> [!TIP]
> **NGINX setup is complete successfully!**

#### CertBOT setup
```
sudo apt update && sudo apt upgrade -y
sudo apt install snapd
sudo snap install --classic certbot
```
#### Run Certbot to create project's SSL certificate
> In our project, the role of the TLS terminator will be performed by the NGINX server
```
sudo certbot --nginx
```
> [!NOTE]
> We should see something like this (also enter your email address for important Certbot messages):
> ![image](https://github.com/user-attachments/assets/62acf224-5c52-49ae-b70d-2d4ab0ced739)

> If we now look at the NGINX configuration file, we will see the changes thanks to which we got the HTTPS connection.
> ![image](https://github.com/user-attachments/assets/a2c65902-73f4-4977-bd10-bf0f78ea85c7)

#### Restart NGINX
> Restart NGINX for HTTPS changes update
```
sudo systemctl restart nginx
```
#### Check the project's HTTPS URL
> My variant: https://fastapiproject.key-info.com.ua/api/v1/docs

> [!TIP]
> **Project setup and deployment completed successfully!**

> [!NOTE]
> **Useful commands:**
> * Activate VENV
> ```
> cd /home/ubuntu/fastApiProject/
> source venv/bin/activate
> ```
> * Run project in port mode
>  ```
>  
>  ```
> * Deactivate VENV (exit)
> ```
> deactivate
> ```

### NGINX
```
sudo systemctl restart nginx
```
