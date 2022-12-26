HOST_IP_LAYER_0 = '10.0.2.15' # '??.??.???.??'

DIF = 1 # difficulty 難易度(suffix = '0' * difficulty)
REF_COUNT = 10 # 履歴交差規定回数
LEADER_UPDATE_INTERVAL = 45 # ハートビートを送る間隔 [sec]
LEADER_CHECK_INTERVAL =  60 # リーダーが故障不在か確認するループのインターバル [sec]
FAILURE = False
CR_INTERVAL = 30 # 履歴交差間隔
ALLOWABLE_TIME = 200 # HEART_BEATの検証許容時間[min]
tkinter_state = False # tkinterを起動するかどうか.
CR_STATE = True # 履歴交差を行うか.
LEADER_AGGREGATION = True # リーダーが集約するか。

MINIMUM_DOMAIN = 3 # 履歴交差を開始させる最低ドメイン数
NEW_CONNECTION = 120 # [sec] 新しい接続があった場合はNEW_CONNECTION
CONFIRMED_BLOCK = 3 # 確定ブロック 履歴交差で共有するブロック
REF_RECHECK = 1 # [sec] 履歴交差部未完時の再チェック待ち時間
MINING_BLOCK_CHECK = 5 # [sec] 履歴交差ブロックマイニングの再チェック待ち時間

HOST_PORT_LAYER_0_origin = 50050 # 0番目のオリジンノードのポート番号(Layer-0)
HOST_PORT_LAYER_1_origin = HOST_PORT_LAYER_0_origin + 1 # 0番目のオリジンノードのポート番号(Layer-1)

#Layer-1
CHECK_INTERVAL = 5 # [min]ブロック生成間隔　# TransactionPoolの確認頻度
Random_CHECK_INTERVAL_FLAG = False # ブロック不生成間隔
CHECK_INTERVAL_LIST = [1 ,15 ,30]
TRANSACTION = 'AD9B477B42B22CDF18B1335603D07378ACE83561D8398FBFC8DE94196C65D806'
#APP/transaction/transaction_pool.pyのcreate_transactionでtransactionを生成中

#他ドメインとIPアドレスとPORT番号設定値はsettings_connection.pyに記載
