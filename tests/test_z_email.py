from emailrfc import mailbox, addressliteral

def test_simple_address():
    state = mailbox('foo@bar.com')
    assert state.text == ''
    assert state.tree == ['foo', '@', 'bar', '.', 'com']

def test_ipaddress():
    state = addressliteral('[127.0.0.1]')

    state = mailbox('foo@[127.0.0.1]')
    assert state.text == ''
    assert state.tree == ['foo', '@', '[', '127', '.', '0', '.', '0', '.', '1', ']']
