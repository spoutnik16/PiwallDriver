#! /bin/bash
# coding: utf-8

# ---------------------------------------------------------------------
# script python pour la machine à remonter le temps pour les musés
# cantonaux.
# WTFPL2.0
# ---------------------------------------------------------------------

# le projet fonctionne sur sur Raspberry Pi, à partir de Raspbian
# Jessie pour le master, et Minibian Jessie pour les tiles, et avec les
# librairies PiWall, soit pwlibs et pwomxplayer pour les tiles, et
# av-libs pour le master.

# sur les tiles, on envoie le pwomxplayer en post-up dans /etc/networks
# /interfaces. Sur le master, le script boot.py est également envoyé en
# post-up.

# ce script sert à faire un pseudo handshake "à la HTTP", puis à SSH
# depuis le master vers les 3 tiles, et à lancer l'écoute de
# pwomxplayer, puis à lancer le broadcast.

# ---------------------------------------------------------------------
# licence à la fin du script
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# dépendances sur le master
# - sshpass
# - avconv (av-libs)
# - python-paramiko
# dépendances sur les tiles
# - pwlibs
# - pwomxplayer
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# index :
# class Piwall
# function __init__
# function __del__
# function loop_video
# function handshake
# function make_listening
# function restart_system
# function main
# partie fonctionnelle
# ---------------------------------------------------------------------
"""Module Machine à Remonter le Temps
Based on PWLibs and PWOMXPlayer"""

import os
from glob import glob
import multiprocessing
import time
import paramiko


__author__ = 'Jérôme Hugon'
__copyright__ = "WTFPL2.0"
__version__ = '1.0.1'
__email__ = 'jerome@theatreinterface.ch'


class Piwall:
    "Create a Piwall object, that deal with the whole process of"
    "initializing the tiles, the master, and a lot of thing"
    def __init__(self,
                 username='pi',
                 password='raspberry',
                 broadcast_ip='udp://239.0.1.23:1234',
                 movie=None,
                 tiles_ip=('192.168.0.1',
                           '192.168.0.2',
                           '192.168.0.3')):
        "Initialize. tiles_ip must be a list. Movie can be 'None',"
        "in which case the module will load the first video it sees"
        "on the usb key"
        self.username = username
        self.password = password
        self.tiles_ip = tiles_ip
        self.broadcast_ip = broadcast_ip
        self.movie = movie
        self.pause()

    def __del__(self):
        "close the pwomxplayer on the differents tiles, if possible"
        "DO NOT COUNT ON THAT. But it sometimes works"
        for ip in self.tiles_ip:
            self.kill_pwomxplayer(ip)
        pass
        print('le systeme est arreté')

    def kill_pwomxplayer(self, ip):
        client = paramiko.Transport((ip, 22))
        client.connect(username=self.username,
                       password=self.password)
        session = client.open_channel(kind='session')
        session.exec_command(
            "kill $(ps aux | grep pwomxp | awk'{print $2}')")
        print "tile %s stopped" % ip

    def pause(self):
        WAIT_TIME = 15
        for i in range(WAIT_TIME):
            s = WAIT_TIME - i
            print('waiting %(i)s' % {'i': s})
            time.sleep(1)

    def loop_video(self):
        "main loop. It handshake the tiles, set up and start "
        "pwomxplayer on the tiles, set up the audio on the master"
        "start the first non-syncronized broadcast, and then restart"
        "it, and is happy"
        # say hello to other pi until they are online
        for ip in self.tiles_ip:
            self.handshake(ip)
        self.pause()
        # open the pwomxplayer listening on all the tiles
        for ip in self.tiles_ip:
            self.make_listening(ip)
        print('handshake dones sleep 1')
        self.movie = self.movie or self.newest_movie()
        # run a first loop, during 25 sec, then kill it !
        self.run_first_loop()
        self.pause()
        print('playing')
        # do the real loop, that will last forever
        os.system('while true;'
                  ' do avconv -re -i %(movie)s -vcodec copy -f avi '
                  '%(broadcast_ip)s '
                  '; done' %
                  {'movie': self.movie,
                   'broadcast_ip': self.broadcast_ip})

    def _first_video_loop(self):
        "private method that run_first_video_loop passes to"
        "multiprocessing"
        os.system('avconv -re -i %(movie)s -vcodec copy -f avi '
                  '%(broadcast_ip)s' %
                  {'movie': self.movie,
                   'broadcast_ip': self.broadcast_ip})

    def run_first_loop(self):
        "This is a strange method. When started, PiWall often have sync"
        "issues. But if you restart it, it is allways solved."
        "This method start the wall, wait 2*WAIT_TIME, shut it down, "
        "and start it again"
        # we start the loop on background (multiprocess)
        p = multiprocessing.Process(target=self._first_video_loop)
        p.start()
        self.pause()
        self.pause()
        for i in range(1, 10):
            print(p.pid)
        # and then we kill it ! (twice cause it solves some bugs)
        p.terminate()
        p.terminate()
        # and we kill the subprocesses of the video
        pid1 = p.pid + 1
        pid2 = p.pid + 2
        os.system('sudo kill ' + pid1.__str__() + ' ' + pid2.__str__())

    def handshake(self, ip):
        "ping the ip until it respond"
        # we simply try 30 times in a row to ping the tile, return True
        # if it answers, wait two sec if it doesn't answer
        for i in range(1, 30):
            print('try handshake ' + ip)
            response = os.system('sudo ping -c1 -w1 %(ip)s '
                                 '>/dev/null 2>&1'
                                 % {'ip': ip})
            if response == 0:
                print('handshake done')
                return True
            time.sleep(2)
            print(ip + ' unreachable')
        return False

    def make_listening(self, ip):
        "set up (routing) the tile and start pwomxplayer"
        # we use paramiko to ssh into the tile, and tell it to listen
        client = paramiko.Transport((ip, 22))
        print('connected to ' + ip)
        client.connect(username=self.username, password=self.password)
        # the first part of the listening is to add the ip route to the
        # broadcast ip
        session = client.open_channel(kind='session')
        session.exec_command("pwomxplayer -A %(broadcast_ip)s"
                             "?buffer_size=120000B"
                             % {'broadcast_ip': self.broadcast_ip, })
        print('command launched')

    def newest_movie(self):
        "find a movie on the usb key, avi or mp4"
        return '/home/pi/Videos/movie.mp4'
        movie_list = [y
                      for x in os.walk('/media')
                      for y in glob(os.path.join(x[0], '*.mp4'))] \
            + [y
               for x in os.walk('/media/pi')
               for y in glob(os.path.join(x[0], '*.avi'))]
        return movie_list[0]

    def simple_loop(self):
        for ip in self.tiles_ip:
            self.makelistening(ip)
        os.system('avconv -re -i %(movie)s -vcodec copy -f avi '
                  '%(broadcast_ip)s' %
                  {'movie': self.movie,
                   'broadcast_ip': self.broadcast_ip})
        for ip in self.tiles_ip:
            self.kill_pwomxplayer(ip)
        return

    def run(self):
        self.run_first_loop()
        for ip in self.tiles_ip:
            self.kill_pwomxplayer(ip)
        while true:
            self.simple_loop



if __name__ == "__main__":
    Piwall().loop_video()


# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                                              Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
# DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE TERMS AND CONDITIONS FOR
# COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO
