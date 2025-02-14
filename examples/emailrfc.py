from comber import C, inf, rs

# An email address, as defined by RFC 5321, with minimal optimization

snum = rs('[0-9]{1,3}')
ipv4address = snum + (C+ '.' + snum)[3]
addressliteral = C+ '[' + ipv4address + ']'

subdomain = rs('[a-z0-9][-a-z0-9]*[a-z0-9]', True)
domain = subdomain + +(C('.') + subdomain)

atom = rs('[-a-z0-9!#$%&\'*+/=?^_`{|}~]+', True)
dotstring = atom + +(C('.') + atom)
qcontentsmtp = rs(r'([^\\"]|\\.)*')
quotedstring = C + '"' + +qcontentsmtp + '"'
localpart = dotstring | quotedstring

mailbox = localpart + '@' + (domain | addressliteral)

mailbox.whitespace = None

