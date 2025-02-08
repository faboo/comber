from comber import C, inf, rs

# An email address, as defined by RFC 5321, with minimal optimization

snum = rs('[0-9](1,4)')
ipv4address = snum + (C('.') + snum)[3]
addressliteral = C+ '[' + ipv4address + ']'

letdig = rs('[a-z0-9]', True)
ldhstr = rs('[-a-z0-9]*', True) + letdig
subdomain = letdig + ~ldhstr
domain = subdomain + (C('.') + subdomain)[0, inf]


atom = rs('[-a-z0-9!#$%&\'*+/=?^_`{|}~]', True)
dotstring = atom + (C('.') + atom)[0, inf]
qtextsmtp = None
qcontentsmtp = qtextsmtp #| quotedpairsmtp
#quotedstring = C + '"' + qcontentsmtp[0, inf] + '"'
localpart = dotstring #| quotedstring

mailbox = localpart + '@' + (domain | addressliteral)

mailbox.whitespace = None
