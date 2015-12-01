#! /bin/sh

# ---------------------------------------------------------------------
# shell script pour la machine à remonter le temps pour les musés 
# cantonaux.
# WTFPL2.0
# ---------------------------------------------------------------------

# Le projet fonctionne sur sur Raspberry Pi, à partir de Raspbian 
# Jessie, et avec les librairies PiWall, soit pwlibs et pwomxplayer 
# pour les tiles, et av-libs pour le master.

# Ce script sert à faire un pseudo handshake "à la HTTP", puis à SSH 
# depuis le master vers les 3 tiles, et à lancer l'écoute de 
# pwomxplayer, puis à lancer le broadcast.

# ---------------------------------------------------------------------
# La licence est à la fin du script
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Plan :
# function video_loop
# function check_connectivity
# function testit
# partie fonctionnelle
# ---------------------------------------------------------------------

# c'est la boucle principale, celle qui fait tout marcher en boucle
video_loop () {
	movie = $1
	#while check_connectivity;
	#do
		avconv \
			-re \
			-i $movie \
			-vcodec copy \
			-f avi \
			-an udp://239.0.1.23:1234
	#done
}

# cette fonction vérifie entre chaque boucle que les ordis soient biens 
# connectés. C'est la solution simple pour arréter la boucle, 
# déconnecter un Pi.
check_connectivity () {
	# TODO: vraiment implémenter cette fonction
	return 0 
	# 0 is true in bash
}

find_movie() {
	return movie.avi
}

testit () {
	if check_connectivity
	then
		echo 'yes'
	else
		echo 'non'
	fi
}

testit
video_loop find_movie

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