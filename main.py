'''
main function of dns name server
including args parse and server boot
'''

import argparse
from nameServer import nameServer
import socketserver



def getArg():
	parser = argparse.ArgumentParser()

	exclusive_group = parser.add_mutually_exclusive_group()
	exclusive_group.add_argument("-d", action="store_true", help="Level-1 Debuging")
	exclusive_group.add_argument("-dd", action="store_true", help="Level-2 Debuging")

	parser.add_argument("--addr", help="DNS server IP address", type=str)
	parser.add_argument("--filename", help="\"dnsrelay.txt\"", type=str)
	return parser.parse_args()


def main():
	args = getArg()
	print(args)
	nameServer.args = args
	HOST, PORT = "localhost", 53
	server = socketserver.ThreadingUDPServer((HOST, PORT), nameServer)
	server.serve_forever()




if __name__ == '__main__':
	main()
