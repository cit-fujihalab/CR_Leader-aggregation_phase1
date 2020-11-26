from distutils.version import StrictVersion
import json

PROTOCOL_NAME = 'simple_bitcoin_protocol'
MY_VERSION = '0.1.0'

MSG_ADD_AS_OWNER = 1000
MSG_REMOVE_AS_OWNER = 1001
MSG_OWNER_LIST = 1002
MSG_REQUEST_OWNER_LIST = 1003
MSG_ADD_AS_CORE = 0
MSG_REMOVE_AS_CORE = 1
MSG_CORE_LIST = 2
MSG_REQUEST_CORE_LIST = 3
MSG_PING = 4
MSG_ADD_AS_EDGE = 5
MSG_REMOVE_EDGE = 6
MSG_NEW_TRANSACTION = 7
MSG_NEW_BLOCK = 8
MSG_REQUEST_FULL_CHAIN = 9
RSP_FULL_CHAIN = 10
MSG_ENHANCED = 11

Sync_DB = 101
Sync_DB2 = 102
Sync_DB3 = 103
Sync_DB4 = 104
Sync_DB5 = 105
Sync_DB6 = 106
Sync_DB7 = 107

MSG_REQUEST_CROSS_REFERENCE = 1012
MSG_ACCEPT_CROSS_REFFERENCE = 1013
MSG_CROSS_REFFERENCE = 1014
START_CROSS_REFFERENCE = 1015
COMPLETE_CROSS_REFERENCE = 1016

ERR_PROTOCOL_UNMATCH = 0
ERR_VERSION_UNMATCH = 1
OK_WITH_PAYLOAD = 2
OK_WITHOUT_PAYLOAD = 3


class MessageManager:

    def __init__(self):
        print('Initializing MessageManager...')

    def build(self, msg_type, my_port=50082, payload=None):
        """
        プロトコルメッセージの組み立て

        params:
            msg_type : 規定のメッセージ種別
            my_port : メッセージ送信者が受信用に待機させているServerSocketが使うポート番号
            payload : メッセージに組み込みたいデータがある場合に指定する

        return:
            message : JSON形式に変換されたプロトコルメッセージ
        """

        message = {
          'protocol': PROTOCOL_NAME,
          'version': MY_VERSION,
          'msg_type': msg_type,
          'my_port': my_port
        }

        if payload is not None:
            message['payload'] = payload

        return json.dumps(message, sort_keys=True, ensure_ascii=False)

    def parse(self, msg):
        """
        プロトコルメッセージをパースして返却する

        params
            msg : JSON形式のプロトコルメッセージデータ
        return :

          結果（OK or NG）とパース結果の種別（ペイロードあり/なし）と送信元ポート番号およびペーロードのデータ
        """
        msg = json.loads(msg)
        msg_ver = StrictVersion(msg['version'])

        cmd = msg.get('msg_type')
        my_port = msg.get('my_port')
        payload = msg.get('payload')

        if msg['protocol'] != PROTOCOL_NAME:
            return ('error', ERR_PROTOCOL_UNMATCH, None, None, None)
        elif msg_ver > StrictVersion(MY_VERSION):
            return ('error', ERR_VERSION_UNMATCH, None, None, None)
        elif cmd in (MSG_CORE_LIST, MSG_OWNER_LIST, MSG_CROSS_REFFERENCE, COMPLETE_CROSS_REFERENCE, MSG_NEW_TRANSACTION, MSG_NEW_BLOCK, RSP_FULL_CHAIN, MSG_ENHANCED):
            result_type = OK_WITH_PAYLOAD
            return ('ok', result_type, cmd, my_port, payload)
        else:
            result_type = OK_WITHOUT_PAYLOAD
            return ('ok', result_type, cmd, my_port, None)
