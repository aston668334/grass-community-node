# Grass-community-node

## Description
Automated mining for Grass.

## Theory
Using web socks to mimic communication between Grass extension ans Grass server.

## Usage
### first usage 
```
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install -r requirements.txt
cp ./.env_template ./.env
```

### For .env

for GRASS_USERID
in logined grass web console run
```
localStorage.getItem('userId');
```
### gerneral usage 

```
source ./.venv/bin/activate
python3 ./grass_community_no_proxy.py
```
 
# Proxy
This project support proxy.
If you want to use proxy for change your IP, add proxy in proxy-list.txt

# Docker
[dockerhub link](https://hub.docker.com/r/astonlee6403/grass-community-node)




# Referrals
if it help you. Please use my Referrals code.
https://app.getgrass.io/register/?referralCode=hQ0bvpT7r02R51x
