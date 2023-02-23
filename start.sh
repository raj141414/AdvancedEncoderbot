#!/bin/bash

###############------Aria2c_Setup------###############
wget -O ./bot_helper/aria2/dht.dat https://github.com/P3TERX/aria2.conf/raw/master/dht.dat
wget -O ./bot_helper/aria2/dht6.dat https://github.com/P3TERX/aria2.conf/raw/master/dht6.dat
TRACKER=$(curl -Ns https://raw.githubusercontent.com/XIU2/TrackersListCollection/master/all.txt -: https://ngosang.github.io/trackerslist/trackers_all_http.txt -: https://newtrackon.com/api/all -: https://raw.githubusercontent.com/DeSireFire/animeTrackerList/master/AT_all.txt -: https://torrends.to/torrent-tracker-list/?download=latest | awk '$1' | tr '\n' ',' | cat)
ran=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 12 | head -n 1)

###############------Starting_Bot------###############
gunicorn app:app --workers 1 --threads 1 --bind 0.0.0.0:5000 --timeout 86400 & python3 main.py