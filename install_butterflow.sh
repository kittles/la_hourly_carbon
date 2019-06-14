#!/bin/bash
cd $HOME

# Install dependencies
sudo apt-get install \
git virtualenv python-dev \
ocl-icd-opencl-dev libopencv-dev \
python-opencv ffmpeg python-pip -y

git clone https://github.com/dthpham/butterflow.git

virtualenv -p /usr/bin/python2 butterflow

echo "/usr/lib/python2.7/dist-packages" > $HOME/butterflow/lib/python2.7/site-packages/butterflow.pth

deactivate

cd $HOME/butterflow
sudo python setup.py install

