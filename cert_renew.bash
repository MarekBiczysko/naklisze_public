#!/bin/bash

source /root/camera_shop/sklepenv/bin/activate
supervisorctl stop sklep
service nginx stop
certbot renew
service nginx start
supervisorctl start sklep