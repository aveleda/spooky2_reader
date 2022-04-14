#!/bin/bash

echo -n "Installing... "
mkdir -p ~/.local/bin ~/.local/share/icons
cp -p spooky2_reader.py  ~/.local/bin
cp -p spooky2_reader.png ~/.local/share/icons
chmod 755 ~/.local/bin/spooky2_reader.py
USER=`whoami`
sed 's/USER/'"$USER"'/g' spooky2_reader.desktop.dist > ~/Desktop/spooky2_reader.desktop
sudo apt-get install python3-tk
echo "Done."
