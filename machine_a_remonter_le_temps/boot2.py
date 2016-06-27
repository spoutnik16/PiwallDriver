"""
Script that allow to autorun a piwall on 3 tiles.
Dependances : apt-get install python-paramiko
WTFPL2.0
"""
import paramiko
from multiprocessing import Process
import os

username = 'pi'
password = 'raspberry'
broadcast_ip = 'udp://239.0.1.23:1234'
broadcast_args = 'buffer_size=1200000B'
movie = '/home/pi/Videos/movie.mp4'
tiles_ip = ('192.168.0.1',
    '192.168.0.2',
    '192.168.0.3')

class Piwall:
    "Create a Piwall object, that deal with the whole process of"
    "initializing the tiles, the master, and a lot of thing"
    def __init__(self, username, password, broadcast_ip, 
                broadcast_args, movie, tiles_ip):
        "Initialize. tiles_ip must be a list."
        self.username = username
        self.password = password
        self.tiles_ip = tiles_ip
        self.broadcast_ip = broadcast_ip
        self.broadcast_args = broadcast_args
        self.movie = movie
    def start_pwo(self, ip):
        "simply start pwomxplayer on one tile"
        self.ssh('pwomxplayer -A --aidx=1 --adev=local  %s?%s'
            % (self.broadcast_ip, self.broadcast_args), ip)
    def stop_pwo(self, ip):
        "stop pwomxplayer on one tile"
        self.ssh("kill $(ps aux | grep pwomxp | awk '{print $2}')", ip)
    def ssh(self, command, ip):
        "ssh into *ip* and send *command*"
        print('connecting on %s' % ip)
        client=paramiko.Transport((ip, 22))
        client.connect(username=self.username, password=self.password)
        session = client.open_channel(kind='session')
        session.exec_command(command)
        print('finished on %s' % ip)
        session.close()
        client.close()
        print('finished on %s, command %s' % (ip, command))
    def run_on_all(self, function):
        "run command on all the tiles"
        list_process = []
        for ip in self.tiles_ip:
            proc = Process(target=function, args=(ip,))
            proc.start()
            list_process += [proc]
        for proc in list_process:
            proc.join()
        print('%s all finished' % function)
    def run(self):
        "start pwo, run the video, and close pwo"
        self.run_on_all(self.start_pwo)
        os.system('avconv -re -i %s -vcodec copy -acodec copy -f avi %s'
            % (self.movie, self.broadcast_ip))
        self.run_on_all(self.stop_pwo)
        print('done')
    def loop(self):
        "loop run until never"
        while True:
            self.run()

if __name__ == "__main__":
    Piwall(username=username, password=password, broadcast_ip=broadcast_ip,
        broadcast_args=broadcast_args, movie=movie, tiles_ip=tiles_ip).loop()

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
