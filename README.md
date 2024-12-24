# RTLANSRGround
Arizona Near Space Research RS41 Camera Ground Station


*******  Windows ********

Install python3 if not already installed

https://www.python.org/downloads/


pip install bitstring

pip install python3-scipy

pip install libscrc

pip install websocket

pip install websocket-client



********  Linux ********

sudo pip install pyrtlsdr

sudo apt-get install build-essential cmake git

sudo apt-get install libusb-dev libusb-1.0-0-dev

git clone https://github.com/librtlsdr/librtlsdr.git

cd librtlsdr

mkdir build && cd build

cmake ../ -DINSTALL_UDEV_RULES=ON

make

sudo make install

sudo ldconfig

sudo pip install libscrc

sudo pip install bitstring

sudo apt install python3-scipy

sudo pip install websocket-client

sudo pip install reedsolo



sudo nano /etc/modprobe.d/blacklist-rtl8xxxu.conf

blacklist dvb_usb_rtl28xxu

