# Project installation steps for "clear" Ubuntu 24.04 LTS server:
sudo apt update
sudo apt -y upgrade

#### Python 3.12.3
python3 -V
sudo apt -y install python3-pip
sudo apt -y install python3-venv

#### Install additional Phyton3 libraries (if not exists)
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

#### Clone project from GitHub repository
git clone https://VLety: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@github.com/VLety/fastApiProject.git
cd fastApiProject


#### Start project
python3 main.py

#### create file /config/environment.json
{
  "current_environment": "prod",
  "prod": "PRODUCTION environment",
  "dev": "DEVELOPMENT environment"
}

#### Create directory /logs/

#### Install unbuffer to put log stream in log file with ni delay
sudo apt-get install expect

#### Useful commands:
./git_update.sh
./start_tippie_monitoring.sh
tail -f ./logs/monitoring-2022_06_14.txt
nano ./config/prod/config.json

crontab -e
To run a cron job every 5 minutes, add the following line in your crontab file:
#### PRODUCTION server
*/5  * * * * /home/ubuntu/tippie_monitoring/start_tippie_monitoring.sh

