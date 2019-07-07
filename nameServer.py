import socketserver
import struct
import socket
import logging

logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)

log = logging.getLogger()

class nameServer(socketserver.BaseRequestHandler):
	url2ip = {}
	args = None
	remote_addr = '202.106.0.20'

	# handle socket
	def handle(self):
		# init url2ip table
		if self.url2ip == {}:
			self.load_file()
		data = self.request[0].strip()
		sock = self.request[1]
		log.debug('request from ' + str(self.client_address))
		parseResult = self.__parseData(data)
		header, query_list, query_info = parseResult['header'], parseResult['query_list'], parseResult['query_info']
		
		# for each query
		for item in query_list:
			name, q_type, q_class = item['url'], item['q_type'], item['q_class']
			log.info('query name:'+ str(name))

			# there name in url2ip 
			if name in self.url2ip.keys():
				ip = self.url2ip[name]
				log.debug('query result:'+ ip)

				if ip == '0.0.0.0':
					# ip error
					log.debug('ip = 0.0.0.0')
					res404 = self.__404data(header)
					sock.sendto(res404, self.client_address)			
				else:
					log.debug('return ip:'+ ip)
					res200 = self.__200Data(header, ip, query_info)
					sock.sendto(res200, self.client_address)
			else:
				# not found
				log.debug('request from remote:'+ name)
				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sock.sendto(data, (self.remote_addr, 53))
				udp_rece = sock.recvfrom(1024)
				self.__parseData(udp_rece[0])
				ip = self.url2ip[name]
				res200 = self.__200Data(header, ip, query_info)
				sock.sendto(res200, self.client_address)
				sock.close()


	# not found message, similar to HTTP 404 state code
	def __404data(self, header):
		answers = 0
		# AA:1 opcode:0000 AA:0 TC:0 RD:1 RA:1 zero:000 rcode: 0011
		flags = 0b1000000110000011
		res = struct.pack('>HHHHHH', header['id'], flags, header['quests'], answers, header['author'], header['addition'])
		return res

	# successful message, similar to HTTP 200 state code
	def __200Data(self, header, ip, query_info):
		
		answers = 1
		# AA:1 opcode:0000 AA:0 TC:0 RD:1 RA:1 zero:000 rcode: 0000
		flags = 0b1000000110000000
		res = struct.pack('>HHHHHH', header['id'], flags, header['quests'], answers, header['author'], header['addition'])
		
		# format: 11 offset
		_name = 0b1100000000001100
		_type, _classify, _ttl, _datalength = 1, 1, 500, 4
		res += query_info
		res += struct.pack('>HHHLH', _name, _type, _classify, _ttl, _datalength)
		s = ip.split('.')
		res += struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
		return res


	def __composeData(self, header, data):
		answers = 0
		# AA:1 opcode:0000 AA:0 TC:0 RD:1 RA:1 zero:000 rcode: 0011
		flags = 0b1000000110000011
		res = struct.pack('>HHHHHH', header['id'], flags, header['quests'], answers, header['author'], header['addition'])
		return res

	# unpack data to dict
	def __parseData(self, data):
		# parse header
		dns_tuple = struct.unpack('>HHHHHH', data[0:12])
		(_id, _flags, _problems, _answers, _author, _addition) = dns_tuple
		log.info('request id:' + str(_id))
		_header = dict(id=_id, flags=_flags, quests=_problems, answers=_answers, author=_author, addition=_addition)
		
		# some error sitution
		if _problems > 1:
			log.debug(str(_header))
			exit()

		# 12 is header length
		pos = 12
		query_list = []

		# parse problem
		for i in range(_problems):
			url, pos = self.__geturl(data, pos)
		
			log.debug('request domain:'+ url)
			q_type, q_class = struct.unpack('>HH', data[pos:pos + 4])
			pos += 4
			
			query_list.append(dict(url=url, q_type = q_type, q_class = q_class))
		query_info = data[12:pos]

		# parse RR and add it to url2ip
		for i in range(_answers):
			if data[pos] & 0b11000000 == 0b11000000:
				pos += 2
			else:
				_, pos = self.__geturl(data, pos)
			r_type, r_class, r_TTL, r_DataLength = struct.unpack('>HHLH', data[pos:pos + 10])
			pos += 10
			if r_type == 1:
				ip_list = struct.unpack('BBBB', data[pos: pos + r_DataLength])
				ip_list = list(map(str, ip_list))
				ip = '.'.join(ip_list)
				self.url2ip[url] = ip
				
			pos = pos + r_DataLength
			log.debug('receive RR: %d %d %d %d'%(r_type, r_class, r_TTL, r_DataLength))
			
		for i in range(_author):
			pass
		for i in range(_addition):
			pass

		return dict(query_list = query_list, header = _header, query_info = query_info)
	
	# read url from byte stream
	def __geturl(self, data, pos):
		url = ''
		# get url
		while True:
			
			if pos > len(data):
				exit()
			num = data[pos]
			
			if num == 0:
				pos += 1
				break
			url_str = data[pos + 1: pos + 1 + num]
			url_str = ''.join([chr(x) for x in url_str])
			url += '.' + url_str
			pos = pos + 1 + num
		return url.strip('.'), pos

	# init and read table from file
	def load_file(self, file_path = './dnsrelay.txt'):
		print(self.args)
		NOINFO = 5
		log.setLevel(NOINFO)

		if self.args.d == True:
			log.setLevel(logging.INFO)
		if self.args.dd == True:
			log.setLevel(logging.DEBUG)

		if self.args.addr:
			self.remote_addr = self.args.addr

		if self.args.filename:
			file_path = self.args.filename

		log.debug('load file')
		with open(file_path) as file:
			for line in file:
				if len(line.split()) == 0:
					break
				ip, name = line.strip().split()
				self.url2ip[name] = ip

