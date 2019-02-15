# Trouve ton train

L'application TrouveTonTrain consiste à proposer des horaires de train entre deux destinations, 
avec une estimation du prix associé, 
et de permettre à l'utilisateur de stocker les horaires qui l'intéressent dans le cloud. 
Cette application se voulant internationale, 
elle permet à l'utilisateur d'indiquer la devise dans laquelle l'estimation du prix est donnée.

## Installation

Installation de python 3

    sudo apt install virtualenv
    sudo apt install python3-pip
   
Création de l'environnement virtuel

    virtualenv -p python3 venv
    . venv/bin/activate
    pip install -r requirements.txt

## Démarrer

Pour Linux

    export FLASK_APP=application.py
    flask run

Pour Windows

    set FLASK_APP=application.py
    flask run
    
## Maitre a jours les stations SNCF

Lancer le script

    python sncf_api.py

Le fichier json générer sera `french_stations.json`

## Changer le token SNCF

Vous pouvez changer le token de L'api SNCF dans le fichier `sncf_api.py` constante `TOKEN`

## Git API REST information sur la ville

https://github.com/keyofdeath/info-sur-ville.git
