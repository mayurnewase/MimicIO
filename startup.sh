#!/bin/bash

sudo apt-get update
sudo apt-get upgrade

sudo apt install awscli --assume-yes
sudo snap install docker

export AWS_ACCESS_KEY_ID=SOMTHING
export AWS_SECRET_ACCESS_KEY=SOMTHING
export AWS_DEFAULT_REGION=ap-south-1

die() { status=$1; shift; echo "FATAL: $*"; exit $status; }
EC2_INSTANCE_ID="`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id || die \"wget instance-id has failed: $?\"`"

aws ec2 associate-address --instance-id $EC2_INSTANCE_ID --public-ip 13.234.165.198

sudo docker pull mayurnewase/mimicio-first:latest
sudo docker run -p 443:5000 -d mayurnewase/mimicio-first:latest