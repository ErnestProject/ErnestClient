# brew cask install xquartz
# OR
# wget https://dl.bintray.com/xquartz/downloads/XQuartz-2.7.11.dmg
# sudo hdiutil attach XQuartz-2.7.11.dmg
# sudo installer -package /Volumes/XQuartz-2.7.11/XQuartz.pkg -target /
# sudo hdiutil detach /Volumes/XQuartz-2.7.11
# Uninstall command line (to check if installed) : sudo rm -rf /opt/X11* /Library/Launch*/org.macosforge.xquartz.* /Applications/Utilities/XQuartz.app /etc/*paths.d/*XQuartz




# brew install homebrew/x11/freerdp
# To check if installed : brew ls --versions freerdp

# reboot

# xfreerdp -u USERNAME -p PASSWORD INSTANCE_IP