# jukebox

Restore the functionality of a jukebox.

[Info](http://the.nerv.free.fr)


## The plan

### Stage 1

Hide a Raspberry Pi with WiFi dongle and external speakers
in the ample guts of the Jukebox.

Using a web interface you can select which song to play.

### Stage 2

Connect to the selection switches (via an arduino?) to allow songs
to be selected the old fashined way.

### Stage 3

Add and amplifier and reuse the original speakers.

## Installation

Stage 1 is based on a Raspberry Pi with a standard Raspian image.

### packages

You need the *sox* package with all the supported formats to
play the audio files:

    sudo apt-get install libsox-fmt-all sox

and a web-server:

    sudo apt-get install apache2

Yes, I know apache is overkill, but I'm familiar with it ...

Probaly git too (see below):

    sudo apt-get install git

### files

Clone this repo into ~/GIT/junkebox:

    mkdir ~/GIT
    cd ~/GIT
    git clone https://github.com/sprinkmeier/jukebox.git

Install the CGI script:

    cd ~/GIT/jukebox
    sudo cp --update --verbose ./jukebox.cgi /usr/lib/cgi-bin/

and override the 'welcome' page to redirect to it:

    sudo cp --update --verbose index.html /var/www/index.html

Someplace to store the audio files:

    sudo mkdir /var/jukebox/
    sudo chown www-data.www-data /var/jukebox/
    sudo ln --symbolic --force /var/jukebox/ /var/www/

The link allows you to download files.

### autostart

Edit the auto-start file:

    sudo vi rc.local

To include the following:

    screen -d -m su - pi -c '/home/pi/GIT/jukebox/jukebox.py'
