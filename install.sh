#This is to install everything assuming you have the git repo.
#This *should* install to the git repo directory (this directory).
#Python packages etc. will be installed.
#Must run as root.

apt-get install libudev-dev
wget http://tjjr.fi/sw/python-uinput/releases/python-uinput-0.11.0.tar.gz
tar -xvf python-uinput-0.11.0.tar.gz
python3 python-uinput-0.11.0.tar.gz/setup.py build
python3 python-uinput-0.11.0.tar.gz/setup.py install
