
#!/bin/bash

find APP/logging/ -maxdepth 1 -type f -name "*.log" -delete
echo 'APP/LOG/内の.logファイルの全削除を実行'
find -maxdepth 1 -type f -name "*.json" -delete
echo '.json(BC)ファイルの全削除を実行'
find -maxdepth 1 -type f -name "*.txt" -delete
echo '.txt(Phase1_time)ファイルの全削除を実行'
