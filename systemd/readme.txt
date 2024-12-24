To enable the ground station gateway to startup at boot execute the following commands:

sudo cp /home/pi/RTLANSRGround/systemd/RTLANSRGround.service /lib/systemd/system
sudo chmod 644 /lib/systemd/system/RTLANSRGround.service
sudo systemctl daemon-reload
sudo systemctl enable RTLANSRGround.service
sudo reboot


Notes:
sudo systemctl stop RTLANSRGround