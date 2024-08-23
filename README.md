## Project setup steps for a basic AWS Ubuntu 24.04 LTS server:

For analisys: https://dylancastillo.co/posts/fastapi-nginx-gunicorn.html#step-5-configure-nginx

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
