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

#---------------------------------------------------------------------
# dépendances sur le master
# - sshpass
# - avconv (av-libs)
# dépendances sur les tiles
# - pwlibs
# - pwomxplayer
#---------------------------------------------------------------------

# ---------------------------------------------------------------------
# # index :
# function video_loop
# function is_connected
# function testit
# function handshake
# function make_listening
# partie fonctionnelle
# ---------------------------------------------------------------------




tiles_ip=(192.168.1.76 192.168.1.77)
broadcast_ip='udp://239.0.1.23:1234'

# c'est la boucle principale, celle qui fait tout marcher en boucle
video_loop () {
	find_movie
	for ip in ${tiles_ip[@]}
	do 
		handshake $ip
		make_listening $ip
	done
	while is_connected;
	do
		avconv \
			-re \
			-i $movie \
			-vcodec copy \
			-f avi \
			-an $broadcast_ip 
	done
}

# cette fonction vérifie entre chaque boucle que les ordis soient biens 
# connectés. C'est aussi une solution simple pour arrêter la boucle, 
# déconnecter un Pi.
is_connected () {
	# TODO: vraiment implémenter cette fonction
	# handshake $tile_1['ip']
	# handshake $tile_2['ip']
	# handshake $tile_3['ip']
	
	for ip in ${tiles_ip[@]}
	do
		handshake $ip
	done
	# 0 is true in bash
}

# cette fonction recherche la vidéo la plus récente sur le disque dur 
# USB.
find_movie () {
	movie="/home/spoutnik16/borgia.avi"
}

# avec cette fonction on vérifie que le tile passé en variable est 
# connecté
handshake () {
	for i in {1..20}
	do
		if ping -c1 $1 &> /dev/null
		then
			return 0
		fi
		sleep 1
	done
}



make_listening() {
	sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no pi@$1 \
		pwomxplayer \
			--tile-code=21 \
			udp://239.0.1.23:1234?buffer_size=12000000B &


}

video_loop


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