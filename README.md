# Wafeform watcher UI suggestion
A suggestion for how to offer a user help in selecting which waveforms he wants to view. This is meant to demonstrate a UI, data access is not included here, demo data is loaded from files.

## Running locally
1) Git clone https://github.com/jmosbacher/waveform-watcher-ui.git
2) cd waveform-watcher-ui/waveforms
3) pip install -r requirements.txt
4) panel serve waveforms.py

## Deploy with docker machine
1) Git clone https://github.com/jmosbacher/waveform-watcher-ui.git
2) cd waveform-watcher-ui/
3) eval $(docker-machine env 'your-docker-machine-name') 
4) Create a network called web: `docker network create web`
5) export DOMAIN='your.domain.name'
6) docker-compose up