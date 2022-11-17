#! /bin/bash
#update and upgrade the system ...
echo "update and upgrade the system..."
sudo apt-get update

sudo apt-get upgrade


echo "install pip ..."
#sudo apt install pip -y
conda install pip

#Installing the necessary packages 

echo "Installing the necessary packages...."

pip install -r requirements.txt

echo "Installation finished...."
