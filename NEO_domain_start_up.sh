#!/bin/bash

echo "リーダーを起動します。"
gnome-terminal -- bash -c "python3 APP/owner_server0.py; bash"
echo "リーダー以外に何ノード立てますか"
echo "16進数で入力してください。(入力待ち・・・）"
read -p "input? 1-A > " str	#標準入力（キーボード）から1行受け取って変数strにセット
echo " == 入力受付完了 == 適切な起動間隔待ち"
echo "$str"
case "$str" in			#変数strの内容で分岐
  [1])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    ;;

  [2])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    ;;

  [3])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server3.py; bash"
    ;;

  [4])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server3.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server4.py; bash"
    ;;

  [5])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server3.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server4.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server5.py; bash"
    ;;

  [6])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server3.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server4.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server5.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server6.py; bash"
    ;;

  [7])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server3.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server4.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server5.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server6.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server7.py; bash"
    ;;

  [8])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server3.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server4.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server5.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server6.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server7.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server8.py; bash"
    ;;

  [9])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server3.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server4.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server5.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server6.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server7.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server8.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server9.py; bash"
    ;;

  [A])
    sleep 10
    gnome-terminal -- bash -c "python3 APP/owner_server1.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server2.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server3.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server4.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server5.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server6.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server7.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server8.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server9.py; bash"
    sleep 15
    gnome-terminal -- bash -c "python3 APP/owner_server10.py; bash"
    ;;

  *)
    echo "undefined(plz input number)";;
esac

