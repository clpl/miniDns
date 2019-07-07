import dns.resolver

domain = 'www.qq.com'
# 74.125.230.127 alt4.stun.l.google.com
my_resolver = dns.resolver.Resolver()
my_resolver.nameservers = ['127.0.0.1']

A= my_resolver.query(domain,'A')
print(A.response)
for i in A.response.answer:
	print(i)
	for j in i.items:
		if j.rdtype == 1:
			print (j.address)