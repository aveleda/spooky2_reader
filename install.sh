#!/bin/bash

echo -n "Installing... "
mkdir -p ~/.local/bin ~/.local/share/icons
cp -p rep_spooky2.py  ~/.local/bin
cp -p rep_spooky2.png ~/.local/share/icons
chmod 755 ~/.local/bin/rep_spooky2.py
USER=`whoami`
sed 's/USER/'"$USER"'/g' report_spooky2.desktop.dist > ~/Desktop/report_spooky2.desktop
sudo apt-get install python3-tk
echo "Done."
