#! /bin/bash

# ---------------------------------------------------------------------
# shell script pour la machine à remonter le temps pour les musés
# cantonaux.
# WTFPL2.0
# ---------------------------------------------------------------------

# le projet fonctionne sur sur Raspberry Pi, à partir de Raspbian
# Jessie, et avec les librairies PiWall, soit pwlibs et pwomxplayer
# pour les tiles, et av-libs pour le master.

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
# dépendances sur les tiles
# - pwlibs
# - pwomxplayer
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# index :
# function video_loop
# function is_connected
# function testit
# function handshake
# function make_listening
# function restart_system
# function main
# partie fonctionnelle
# ---------------------------------------------------------------------

# TODO: créer une classe, pour que quand elle est détruite ça ferme ce
# putain de listen

import os
import time
import paramiko


class Piwall:

    def __init__(self,
                 username='pi',
                 password='raspberry',
                 broadcast_ip='udp://239.0.1.23:1234',
                 movie=None,
                 tiles_ip=('192.168.1.77',)):
        self.username = username
        self.password = password
        self.tiles_ip = tiles_ip
        self.broadcast_ip = broadcast_ip
        self.movie = Movie(movie)

    def __del__(self):
        # close the pwomxplayer on the differents tiles, if possible
        for host in self.tiles_ip:
            try:
                client = Paramiko.Transport((host, 22))
                client.connect(username=self.username, password=self.password)
                session = client.open_channel(kind='session')
                session.exec_command(
                    "kill $(ps aux | grep pwomxp | awk'{print $2}')")
            except:
                pass
        pass
        print('le systeme est arreté')

    def video_loop(self):
        for ip in self.tiles_ip:
            self.handshake(ip)
            self.make_listening(ip)
        time.sleep(5)
        os.system('while true; do avconv -re -i %(movie)s -vcodec copy -f avi -an %(broadcast_ip)s; done' %
                  {'movie': self.movie, 'broadcast_ip': self.broadcast_ip})

    def handshake(self, ip):
        for i in range(1, 20):
            response = os.system("ping -c1 -w1 %(ip)s >/dev/null 2>&1"
                                 % {'ip': ip})
            if response == 0:
                return True
            time.sleep(1)
            print(ip + ' unreachable')
        return False

    def make_listening(self, ip):
        client = paramiko.Transport((ip, 22))
        client.connect(username=self.username, password=self.password)
        session = client.open_channel(kind='session')
        session.exec_command('pwomxplayer --tile-code=21 ' +
                             self.broadcast_ip + '?buffer_size=1200000B')


class Tile:

    def init(self,
             username='pi',
             password='raspberry',
             tile_ip='192.168.1.77'):
        self.username = username
        self.password = password
        self.tile_ip = tile_ip


class Movie:

    def __init__(self, movie=None):
        if movie:
            self.movie = movie
        else:
            movie = "/home/spoutnik16/borgia.avi"

    def __str__(self):
        return movie.__str__()


if __name__ == "__main__":
    Piwall().video_loop()


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
