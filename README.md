# REST API server solution based on FastAPI framework with RBAC model
> Recommended for PoC and Prototype approach or as a base template<br />
> The delivery result of this project can be seen here https://fastapiproject.key-info.com.ua/api/v1/docs

> [!Note]
> * Purpose: Intended for educational and promotional needs.
> * Audience: Python Junior+/Middle level with linux DevOps skills.

> [!TIP]
> This solution is presented in the most easy-to-learn form without using Docker delivery technology or an additional full-fledged WSGI HTTP server such as Gunicorn. We will simply use the Uvicorn ASGI web server that is already built into FastAPI framework with NGINX as a proxy server. And this deployment option will be sufficient for PoC, Prototype, or even MVP-production purposes.<br />
> [Read more](https://fastapi.tiangolo.com/deployment/concepts/#deployments-concepts) about FastAPI recommended deployment.

> [!IMPORTANT]
> However, to fully utilize the solution in a production environment, it is recommended to add Docker delivery technology, use PostgreSQL database instead of SQLite3 (AWS RDS will be enough), optionally add Redis for caching support and Gunicorn WSGI server with automatic management of multiple worker processes in front of Uvicorn ASGI server, if it is really necessary according to the project requirements.

## Project IDEA
> [!Note]
> ### User story
> Need to create a Prototype/MVP backend solution for implementing a simple Ticket system.<br />
> * Participants: **User** of the outsourcing support department, **Employee** and **Ticket** on the basis of which the employees are supported. The creation and processing of the **Ticket** is the responsibility of the support department.
> * Security: Access to the system based on user's roles. It is also necessary to have separate explicit user attributes to control enabling/disabling access to the system and allowing/denying logins (separate from the user's roles).
> ### Technical requirements
> * REST API server with Swagger UI.
> * OAuth2 authorization protocol with Role-based access control (RBAC) model.
> * Ability for easily integration with others backend solutions and frontend UI/UX part.

## Project Tech stack
* Python 3.10+
* FastAPI as a base project framework [read more](https://fastapi.tiangolo.com)
* SQLAlchemy V2 as SQL toolkit and Object Relational Mapper [read more](https://www.sqlalchemy.org)
* Pydantic V2 as schemas builder [read more](https://docs.pydantic.dev/latest/#pydantic)
* Annotated(typing) for metadata management [read more](https://docs.python.org/3/library/typing.html#typing.Annotated)
* PyJWT for encode and decode JSON Web Tokens (JWT) [read more](https://pyjwt.readthedocs.io/en/stable/#welcome-to-pyjwt)
* Passlib[Argon2] for password hashing [read more](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.argon2.html#passlib-hash-argon2-argon2)
* Uvicorn as ASGI web server [read more](https://www.uvicorn.org/)
* NGINX as Reverse Proxy & TLS Termination service [read more](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
* Certbot as Let’s Encrypt SSL certificate manager [read more](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)

> [!Note]
> What is the difference between [WSGI](https://wsgi.tutorial.codepoint.net/intro) and [ASGI](https://asgi.readthedocs.io/en/latest/) server interface specification? In simple words: WSGI is synchronous, handling one request at a time, and blocking execution until processing is complete. ASGI is asynchronous, handling multiple requests concurrently without blocking other requests. We know that FastApi is an asynchronous framework, so Uvicorn ASGI web server is an obvious choice.

> [!Note]
> Using Nginx as a Proxy in front of your WSGI or ASGI server may not be necessary for PoC or Prototype approach, but is recommended for additional resilience and full-fledged production environment. Nginx can deal with serving your static media and buffering slow requests, leaving your application servers free from load as much as possible, add more security etc.

> [!Note]
> For password hashing we will not apply the commonly used [bcrypt] algorithm, will use the Argon2 for the following reasons:
> * Crypt Function has been deprecated since Python version 3.11 and will be removed in version 3.13 [read more](https://peps.python.org/pep-0594/#crypt)
> * Argon2 is a modern Password Hashing Algorithm and is intended to replace pbkdf2_sha256, bcrypt, and scrypt [read more](https://guptadeepak.com/comparative-analysis-of-password-hashing-algorithms-argon2-bcrypt-scrypt-and-pbkdf2/)
  
## Project specification and standards
* OpenAPI Specification v3.1 [read more](https://spec.openapis.org/oas/latest.html)
* OAuth 2.0 authorization protocol [read more](https://oauth.net/2/)
* Role-Based Access Control (RBAC) permissions model [read more](https://auth0.com/docs/manage-users/access-control/rbac)
  
## Project Tech features
* Full-fledged RESTful API server with Swagger UI
* OAuth 2.0 authorization protocol
* JWT token authentication with expiration period and [optional authorization scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/#oauth2-scopes)
* Flexible project customization and tuning using configuration files
* CRUD operations for 3 objects: User, Employee and Ticket
* PATCH operations on User object (name or password changing etc)
* User RBAC permissions model for each API endpoint with additional security attributes: Disabled and LoginDenied

> [!TIP]
> ## Learn more about the project security model
> > The role-based access control (RBAC) model is used to grant permissions to any API endpoint, except for the Authentication section, where we have:
> * Login (get a valid token) based on username and password **/api/v1/token**
> * Get information about me (based on a valid user token) **/api/v1/me**
> * Get my current status (based on a valid user token) **/api/v1/status**<br />
> ### RBAC roles:
> * admin - can do CRUD (PATCH) requests with **User**, **Employee** and **Ticket** (top level of security).
> * manager - can do CRUD requests with **Employee** and **Ticket**, also read **User** and UPDATE: Contacts, Disabled and LoginDenied attribute. Can't change User role(s).
> * support - can do CRUD requests with **Ticket**, also read **Employee**.
> * all roles can use Authentication section and change your own password.
> ### Additional security attributes
> * Disabled users with valid token cannot access any endpoints regardless of their role(s), except for the Authentication section - but can Login (get valid token).<br />
> * LoginDenied users cannot Login (cannot get valid token).<br />
> * Default token expiration period equal "ACCESS_TOKEN_EXPIRE_MINUTES": 60 (we can changer this setting in ./config/config.json file).

## Setup and deploy project to the "clear" AWS EC2 Ubuntu instance
> [!TIP]
> For the EC2 instance, it is recommended to choose the Ubuntu 24.04 LTS OS type as it comes with Python 3.12 pre-installed but you can try other linux OS.
> We will not consider the installation of EC2 instance via AWS console in this article as this is a separate topic, assuming that the necessary knowledge already exists. For PoC or Prototype project deployments, the [AWS Free Tier](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all) will be sufficient [read more](https://aws.amazon.com/ec2/getting-started/).

> [!IMPORTANT]
> In our project setup we will use everywhere the name "fastApiProject", linux user "ubuntu" and url "fastapiproject.key-info.com.ua", what is done for simplicity. But for your needs you can/can/must use your own name/user/url.

> To proceed further, log in to the EC2 instance linux server console...

### Install base software
Update system
```
sudo apt update && sudo apt upgrade -y
```
Install GIT
```
sudo apt -y install git
```
Install common Python Dependencies
```
sudo apt -y install build-essential libssl-dev libffi-dev python3-dev
sudo apt -y install python3-pip
sudo apt -y install python3-venv
```

### Setup project configuration

Clone a project from a GitHub repository
```
git clone https://VLety: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@github.com/VLety/fastApiProject.git
```
Let's go to our project catalog
```
cd /home/ubuntu/fastApiProject/
```
Create lightweight Python “virtual environments” (VENV) [read more](https://docs.python.org/3/library/venv.html):
```
python3 -m venv venv
```
Activate VENV
```
source venv/bin/activate
```
#### Install Python dependencies
> VENV must be in Active mode
```
pip3 install "fastapi[standard]"
pip3 install SQLAlchemy
pip3 install pyjwt
pip3 install "passlib[argon2]"
pip3 install pytest
pip3 install pytest-assert-utils
```
Deactivate VENV
```
deactivate
```

#### Setup configuration files
> [!CAUTION]
> Never ever add configuration files to the repository! This is due to potential security issues and problems with updates delivery.

> [!IMPORTANT]
> There are many approaches to avoid "config problem" - we will use the initial creation of configuration files from the project config templates.

Copy all 5 config template files from ./setup/config to the base project's ./config folder and rename them by removing the "template" extension.
```
cp -f /home/ubuntu/fastApiProject/setup/config/*.template /home/ubuntu/fastApiProject/config/
cd /home/ubuntu/fastApiProject/config/
mv -f config.json.template config.json
mv -f permissions.json.template permissions.json
mv -f schemas.json.template schemas.json
mv -f test_main.json.template test_main.json
mv -f log.ini.template log.ini
```

> As a result, we should get the following list of files:<br />
> ![image](https://github.com/user-attachments/assets/97e8b3ab-13c4-4842-bae9-4cf0dbf792c1)<br /><br />

Generate a new SECRET_KEY that will be used to encrypt/decrypt JWT tokens
```
openssl rand -hex 32
```

Copy new SECRET_KEY to the project /config/config.json file
```
nano /home/ubuntu/fastApiProject/config/config.json
```
Change SECRET_KEY value
```
"auth": {
    "SECRET_KEY": "paste new secret key here",
```
> Save: Ctrl+o, Exit: Ctrl+x

> [!WARNING]
> Do not use the project default SECRET_KEY for production environment!

> [!TIP]
> If you wish, you can change the necessary project parameters using the initial setup, please going through:
> * config.json: The file is intended to store the main project configuration settings.
> * schemas.json: The file is used to configure Pydantic schemas validation.
> * permissions.json: The file is used to configure RBAC permissions for API endpoints.
> * test_main.json: The file is intended to store the main project test settings.
> * log.ini: The file is used to configure server logging.

Change password for default users<br />
> Initially we have 3 default users: admin, manager and support. So please open the ./setup/setup.json file, change the passwords for all 3 users and save the file with the new passwords.
```
nano /home/ubuntu/fastApiProject/setup/setup.json
```
> Example:<br />
> ![image](https://github.com/user-attachments/assets/b01f9934-44bf-4bdc-97ac-e5a8935c5fca)<br />
> Save: Ctrl+o, Exit: Ctrl+x

> [!TIP]
> Default password requirements (can be changed in the schemas.json file): minimum password length is 8 characters - maximum password length is 16 characters. At least one uppercase and one lowercase letter, one number and one special character.

Update new passwords in database<br />
> Activate project's VENV
```
cd /home/ubuntu/fastApiProject/
source venv/bin/activate
```
Run password update
```
python /home/ubuntu/fastApiProject/setup/change_users_password.py
```
> We should see something like this:
> ![image](https://github.com/user-attachments/assets/8c26f82b-b08d-4592-b174-15aa91649055)

#### Run project TEST to check if everthing setup properly
Set relevant admin user name & password in the ./config/test_main.json file<br />
```
nano /home/ubuntu/fastApiProject/config/test_main.json
```
> Save: Ctrl+o, Exit: Ctrl+x<br />

Run test in compact output<br />
> VENV must be in Active mode
```
python -m pytest /home/ubuntu/fastApiProject/test_main.py
```

Run test in verbose output [optional]<br />
```
python -m pytest -rP /home/ubuntu/fastApiProject/test_main.py
```

Also we can run API server in a port mode [optional]
> VENV must be in Active mode
```
uvicorn main:app --host 127.0.0.1 --port 8000
```
> We should see something like this:<br />
> ![image](https://github.com/user-attachments/assets/c445a34e-60bd-475f-adc4-1fe13f930330)

> [!TIP]
> #### Setup project configuration completed successfully!

### Add Systemd service
> [!NOTE]
> A tool that is starting to be common on linux systems is Systemd. It is a system services manager that allows for strict process management, resources and permissions control.
> The Linux/Unix socket approach is used to create a communication endpoint and return a file descriptor referencing that endpoint.
> We will use the Systemd service to manage the state of our API server: starting, restarting, stopping and check current status.
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

# Socket .sock file access type (access from NGINX side requires false)
PrivateTmp=false

# This user can be transiently created by systemd
# DynamicUser=true

# If your app does not need administrative capabilities, let systemd know
# ProtectSystem=strict

[Install]
WantedBy=multi-user.target
```
> Save: Ctrl+o and Exit: Ctrl+y<br />

Cause Systemd to reload units update from disk
```
sudo systemctl daemon-reload
```

Set service to autoload when server starts
```
sudo systemctl enable fastApiProject.service
```

Start project service
```
sudo systemctl start fastApiProject.service
```

Check project service status
```
sudo systemctl status fastApiProject.service
```

> We should see something like this:<br />
> ![image](https://github.com/user-attachments/assets/6e71d759-2f0e-4925-8fd3-e07189f8e3e7)

> [!TIP]
> **Systemd service added successfully!**

### NGINX setup
> [!NOTE]
> FastAPI latency is lower when communicating with NGINX via a socket than when communicating via a port, but both solutions will work. We will go the way of NGINX communicating with Uvicorn via a socket connection.<br />

Add the public IP address of EC2 instance to your domain's DNS A record.
> My variant:
> ![image](https://github.com/user-attachments/assets/cd75e648-5fb3-494d-92af-11871afb4807)

Install NGINX
```
sudo apt update && sudo apt upgrade -y
sudo apt -y install nginx
```

Delete default NGINX configuration file symlink
```
sudo rm /etc/nginx/sites-enabled/default
```

Create new NGINX configuration file
```
sudo nano /etc/nginx/sites-available/fastApiProject
```

Type:
> [!IMPORTANT]
> Don't forget to specify your domain url for the **server_name fastApiProject.key-info.com.ua;** configuration string
```
server {
    listen 80;
    
    # Project server URL
    server_name fastApiProject.key-info.com.ua;

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
> Save: Ctrl+o, Exit: Ctrl+x

Copy NGINX configuration file as symlink to the site-enabled folder
```
sudo ln -sf /etc/nginx/sites-available/fastApiProject /etc/nginx/sites-enabled/fastApiProject
```

Restart NGINX
```
sudo systemctl restart nginx.service
```

Check NGINX status
```
sudo systemctl status nginx.service
```
> We should see something like this:
> ![image](https://github.com/user-attachments/assets/222a6303-86b4-408e-9fe2-4e80e76110d0)

Check the project's HTTP URL
> My variant: http://fastapiproject.key-info.com.ua/api/v1/docs
> ![image](https://github.com/user-attachments/assets/5cc4b4d1-a30c-4a47-aebe-d557991937a5)

> [!TIP]
> **NGINX setup completed successfully!**

### Certbot setup
Install Certbot
```
sudo apt update && sudo apt upgrade -y
sudo apt install snapd
sudo snap install --classic certbot
```

Run Certbot to create project's SSL certificate
> In our project, the role of the TLS terminator will be performed by the NGINX server.
```
sudo certbot --nginx
```
> We should see something like this (also enter your email address for important Certbot messages):<br />
> ![image](https://github.com/user-attachments/assets/62acf224-5c52-49ae-b70d-2d4ab0ced739)<br />
> If we now look at the NGINX configuration file, we will see the changes thanks to which we got the HTTPS connection.<br />
> ![image](https://github.com/user-attachments/assets/a2c65902-73f4-4977-bd10-bf0f78ea85c7)<br />
> The Certbot packages on your system come with a cron job that will renew your certificates automatically before they expire (certificate are valid for 90 days). You will not need to run Certbot again, unless you change your configuration. You can test automatic renewal for your certificates by running this command:
> ```
> sudo certbot renew --dry-run
> ```

Restart NGINX for HTTPS changes update
```
sudo systemctl restart nginx
```
> Check the project's HTTPS URL<br />
> My variant: https://fastapiproject.key-info.com.ua/api/v1/docs

> [!TIP]
> ### Project setup and deployment completed successfully!

## Useful commands
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
