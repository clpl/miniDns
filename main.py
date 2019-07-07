'''
main function of dns name server
including args parse and server boot
'''

import argparse
from nameServer import nameServer
import socketserver

print(nameServer)
# parse args
# return dict(args)
def getArg():
	parse = argparse.ArgumentParser()
	return ''


def main():
	args = getArg()
	HOST, PORT = "localhost", 53
	server = socketserver.ThreadingUDPServer((HOST, PORT), nameServer)
	server.serve_forever()




if __name__ == '__main__':
	main()
