#!/bin/sh
ping -q -c 1 -W 1 8.8.8.8 > /dev/null; 
if [ $? -eq 1 ]; 
then exit; 
fi;
echo "    ATTENDERE PREGO......."
echo "  SpeedTest in corso      "
/usr/lib/enigma2/python/Plugins/Extensions/fReE_iPtV_pAnDa_SaT_tEaM/res/script/speedtest.py
exit 0