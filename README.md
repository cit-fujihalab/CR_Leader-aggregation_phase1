# 2022NS11
# Phase1計測を合意待ち時間含めた実験ノード


## 必要モジュールを以下に記載
（equirements.shを実行すると以下のコマンドが実行される）

equirements.txtに必要モジュールを記載
"""sh equirements.txt
$ apt install python3-pip

$ pip3 install numpy

$ pip3 install PyCryptodome

$ pip3 install websocket_server==0.4

↑バージョン指定しないと実行不可

$ pip3 websocket_client

$ pip3 install plyvel

$ apt-get -y install python3-tk


## 実行方法


実行するうえでIPアドレスとPORT番号の設定が必要である.
APP/settings.py内

IPアドレスの変更(1行目):HOST_IP_LAYER_0 = 'xx.xx.xxx.xx'

## 構築したいP2Pネットワークの規模に応じて起動ノード数を起動

"""sh
$ python3 owner_server0.py

$ python3 owner_server1.py

$ python3 owner_server2.py

$ python3 owner_server3.py

$ python3 owner_server4.py

            ・
            ・
            ・
            ・

$ python3 owner_serverXX.py <-(順番に起動することが望ましい)
"""