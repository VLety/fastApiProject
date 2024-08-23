# Project installation steps for "clear" AWS Ubuntu 24.04 LTS server:
sudo apt update
sudo apt -y upgrade
sudo apt -y git

#### Install Python 3.12.3, PIP3 & VENV
python3 -V
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
sudo apt -y install python3-pip
sudo apt -y install python3-venv

#### NGINX
sudo apt -y install nginx

#### Clone project from GitHub repository
git clone https://VLety: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@github.com/VLety/fastApiProject.git

#### Creating lightweight Python “virtual environments” - VENV:
## https://docs.python.org/3/library/venv.html
cd fastApiProject
python3 -m venv venv
source venv/bin/activate

#### Add dependencies for active VENV:
pip3 install "fastapi[standard]"
pip3 install SQLAlchemy
pip3 install pyjwt
pip3 install "passlib[bcrypt]"
pip3 install "fastapi[standard]"

#### Start project inside VENV
uvicorn main:app --host 127.0.0.1 --port 8000

#### CertBOT
sudo apt install snapd
sudo snap install --classic certbot
sudo certbot --nginx
sudo systemctl restart nginx

#### Useful commands:
## VENV
  source venv/bin/activate
  deactivate
## NGINX
  sudo systemctl restart nginx


