#!/usr/bin/env bash

cd /home/app || exit
# sudo python3 get-pip.py -i https://pypi.org/simple

sudo apt-get update
sudo apt-get install -y python3-pip
sudo apt-get install fonts-wqy-microhei
