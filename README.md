# miniDns

An DNS name server toy, homework of computer network course in bupt.

# Feature

Read * dnsrelay.txt * as a mapping table (host2ip). When receiving a DNS A problem, there are three cases:

The host is not in the mapping table, the problem is resent to the remote name server to get the ip(RR from remote name server), and then it is responded to the client.

Host is in the map table, but ip is "0.0.0.0", respond with no answer.

Host in the map table, respond with ip.

# Using

```shell
python main.py [-d|-dd] --addr [dns-server-ipaddr] --filename [filename]
```

*-d* or *-dd* to set logging level, note that they are exclusive.

*dns-server-ipaddr* is the ip of the remote name server.

*filename* is dnsrelay.txt.
