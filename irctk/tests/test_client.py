import unittest
from irctk.tests.mock_client import MockClient as Client
from irctk.nick import Nick


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = Client('kylef', 'kyle', 'Kyle Fuller')
        self.client.nick.nick = 'kylef'
        self.client.delegate = self

        self.private_messages = []

    # Delegate

    def irc_private_message(self, client, nick, message):
        self.private_messages.append((client, nick, message))

    # Tests

    def test_client_has_nickname(self):
        self.assertEqual(self.client.nickname, 'kylef')

    def test_client_has_ident(self):
        self.assertEqual(self.client.ident, 'kyle')

    def test_client_has_realname(self):
        self.assertEqual(self.client.realname, 'Kyle Fuller')

    # Registration

    def test_client_is_not_registered_by_default(self):
        self.assertFalse(self.client.is_registered)

    def test_client_is_registered_after_001(self):
        self.client.read_data(':irc.kylefuller.co.uk 001 kyle :Welcome')
        self.assertTrue(self.client.is_registered)

    # Ping

    def test_client_sends_pong_when_pinged(self):
        self.client.read_data('PING :hello')
        self.assertEqual(self.client.sent_lines, ['PONG hello'])

    # Handling

    def test_client_handles_5_parsing_support(self):
        self.client.read_data(':irc.kylefuller.co.uk 005 kyle :NICKLEN=5 CHANNELLEN=6')
        self.assertEqual(self.client.isupport.maximum_nick_length, 5)
        self.assertEqual(self.client.isupport.maximum_channel_length, 6)

    def test_client_handles_channel_new_mode(self):
        channel = self.client.add_channel('#test')
        self.client.read_data(':kyle!kyle@kyle MODE #test +tn')
        self.assertTrue(channel.modes['t'])
        self.assertTrue(channel.modes['n'])

    def test_client_handles_channel_remove_mode(self):
        channel = self.client.add_channel('#test')
        self.client.read_data(':kyle!kyle@kyle MODE #test +tn')
        self.client.read_data(':kyle!kyle@kyle MODE #test -tn')
        self.assertEqual(channel.modes, {})

    def test_client_handles_setting_channel_list_mode(self):
        channel = self.client.add_channel('#test')
        self.client.read_data(':kyle!kyle@kyle MODE #test +b cake')
        self.client.read_data(':kyle!kyle@kyle MODE #test +b snake')
        self.assertEqual(channel.modes['b'], ['cake', 'snake'])

    def test_client_handles_removing_channel_list_mode(self):
        channel = self.client.add_channel('#test')
        self.client.read_data(':kyle!kyle@kyle MODE #test +b cake')
        self.client.read_data(':kyle!kyle@kyle MODE #test +b snake')
        self.client.read_data(':kyle!kyle@kyle MODE #test -b cake')
        self.assertEqual(channel.modes['b'], ['snake'])

    def test_client_handles_removing_channel_list_mode(self):
        channel = self.client.add_channel('#test')
        self.client.read_data(':kyle!kyle@kyle MODE #test +l 5')
        self.client.read_data(':kyle!kyle@kyle MODE #test +l 6')
        self.assertEqual(channel.modes['l'], '6')

    # Delegate

    def test_client_forwards_private_messages_to_delegate(self):
        self.client.read_data(':bob!b@irc.kylefuller.co.uk PRIVMSG kylef :Hey')
        self.assertEqual(self.private_messages,
            [(self.client, Nick.parse(self.client, 'bob!b@irc.kylefuller.co.uk'), 'Hey')])

