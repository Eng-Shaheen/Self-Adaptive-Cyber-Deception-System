#!/bin/bash

URL="http://127.0.0.1:5000/cowrie-log"

curl -s -X POST -H "Content-Type: application/json" \
-d '{"eventid":"auth.failed","src_ip":"10.0.2.20","message":"authentication failed","attempts":1}' $URL

sleep 1

curl -s -X POST -H "Content-Type: application/json" \
-d '{"eventid":"auth.failed","src_ip":"10.0.2.20","message":"authentication failed","attempts":2}' $URL

sleep 1

curl -s -X POST -H "Content-Type: application/json" \
-d '{"eventid":"auth.failed","src_ip":"10.0.2.20","message":"authentication failed","attempts":3}' $URL

sleep 1

curl -s -X POST -H "Content-Type: application/json" \
-d '{"eventid":"session.connect","src_ip":"10.0.2.15","username":"root","message":"login success"}' $URL
