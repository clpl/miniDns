import socketserver
import struct
import socket

class nameServer(socketserver.BaseRequestHandler):
	url2ip = {}
	id2id = {}
	def handle(self):
		if self.url2ip == {}:
			self.load_file()
		data = self.request[0].strip()
		sock = self.request[1]
		print(self.client_address)
		parseResult = self.__parseData(data)
		header, query_list = parseResult['header'], parseResult['query_list']
		print(query_list)
		for item in query_list:
			name, q_type, q_class = item['url'], item['q_type'], item['q_class']
			print('query name:', name)
			if name in self.url2ip.keys():
				ip = self.url2ip[name]
				print('query result:', ip)
				if ip == '0.0.0.0':
					res404 = self.__404data(header)
					sock.sendto(res404, self.client_address)
					print('ip = 0.0.0.0')
				else:
					print('return answers', ip)
					res200 = self.__200Data(header, ip)
					sock.sendto(res200, self.client_address)
			else:
				ip = self.requestRemote()
				print('requestRemote:', name)
				sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				sock.sendto(data, ('202.106.0.20', 53))
				udp_rece = sock.recvfrom(1024)
				print(udp_rece)
				self.__parseData(udp_rece[0])
				

		# socket = self.request[1]
		# print("wrote:",self.client_address[0])
		# print (data)
		# sock.sendto(self.request[0].strip(), self.client_address)
		# self.request[0].strip()
		#socket.sendto(data.upper(), self.client_address)

	def __404data(self, header):
		answers = 0
		# AA:1 opcode:0000 AA:0 TC:0 RD:1 RA:1 zero:000 rcode: 0011
		flags = 0b1000000110000011
		res = struct.pack('>HHHHHH', header['id'], flags, header['quests'], answers, header['author'], header['addition'])
		return res

	def __200Data(self, header, ip):
		print('hp:', header, ip)
		answers = 1
		# AA:1 opcode:0000 AA:0 TC:0 RD:1 RA:1 zero:000 rcode: 0000
		flags = 0b1000000110000000
		res = struct.pack('>HHHHHH', header['id'], flags, header['quests'], answers, header['author'], header['addition'])
		#res = struct.pack('>HHHHHH', header['id'], flags, 0, answers, header['author'], header['addition'])
		
		# 11 offset
		_name = 0b1100000000001100
		_type = 1
		_classify = 1
		_ttl = 5000
		_datalength = 4
		res += self.qu
		res += struct.pack('>HHHLH', _name, _type, _classify, _ttl, _datalength)
		s = ip.split('.')
		res += struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
		return res

	def requestRemote(self):
		pass


	def __composeData(self, header, data):
		answers = 0
		# AA:1 opcode:0000 AA:0 TC:0 RD:1 RA:1 zero:000 rcode: 0011
		flags = 0b1000000110000011
		res = struct.pack('>HHHHHH', header['id'], flags, header['quests'], answers, header['author'], header['addition'])
		return res
	# unpack data to dict
	def __parseData(self, data):
		dns_tuple = struct.unpack('>HHHHHH', data[0:12])
		(_id, _flags, _quests, _answers, _author, _addition) = dns_tuple
		_header = dict(id=_id, flags=_flags, quests=_quests, answers=_answers, author=_author, addition=_addition)
		print(_header)
		pos = 12
		query_list = []
		for i in range(_quests):
			url = ''
			# get url
			while True:
				num = data[pos]
				print(num)
				if num == 0:
					self.qu = data[12:]
					pos += 1
					break
				url_str = data[pos + 1: pos + 1 + num]
				url_str = ''.join([chr(x) for x in url_str])
				url += '.' + url_str
				pos = pos + 1 + num
			url = self.__geturl(data, pos)
			q_type, q_class = struct.unpack('>HH', data[pos:pos + 4])
			pos += 4
			
			query_list.append(dict(url=url, q_type = q_type, q_class = q_class))
		for i in range(_answers):
			print('pos:',pos)
			print('now',bin(data[pos]))
			if data[pos] & 0b11000000 == 0b11000000:
				print('tiao')
				pos += 2
			r_type, r_class, r_TTL, r_DataLength = struct.unpack('>HHLH', data[pos:pos + 10])
			if r_type == 1:
				pass
				
			else:
				pos = pos + 10 + r_DataLength
			

			print('reserive:', r_type, r_class, r_TTL, r_DataLength)

			
		for i in range(_author):
			pass
		for i in range(_addition):
			pass

		return dict(query_list = query_list, header = _header)
	
	def __geturl(self, data, pos):
		url = ''
		# get url
		while True:
			num = data[pos]
			print(num)
			if num == 0:
				self.qu = data[12:]
				pos += 1
				break
			url_str = data[pos + 1: pos + 1 + num]
			url_str = ''.join([chr(x) for x in url_str])
			url += '.' + url_str
			pos = pos + 1 + num
		return url.strip('.')
		#return dict(header=_header, queryInfo=DNSQueryDestructor(data[12:]))

	def load_file(self, file_path = './dnsrelay.txt'):
		
		with open(file_path) as file:
			for line in file:
				if len(line.split()) == 0:
					break
				ip, name = line.strip().split()
				self.url2ip[name] = ip

	# def listen(self, data):
	# 	(ip, das) = self.__parseData(data)

	# 	if ip == '0.0.0.0':
	# 		pass
	# 		#self.send()
	# 	#else if Form[ip] != None:
	# 	#	pass
	# 		#self.send(Form[ip])
	# 	else:
	# 		pass
	# 		domain = self.__getFromRemote()
	# 		#send()

	

