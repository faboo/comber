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

def test_simple_address():
    state = mailbox('foo@bar.com')
    assert state.text == ''
    assert state.tree == ['foo', '@', 'bar', '.', 'com']

def test_ipaddress():
    state = addressliteral('[127.0.0.1]')

    state = mailbox('foo@[127.0.0.1]')
    assert state.text == ''
    assert state.tree == ['foo', '@', '[', '127', '.', '0', '.', '0', '.', '1', ']']
