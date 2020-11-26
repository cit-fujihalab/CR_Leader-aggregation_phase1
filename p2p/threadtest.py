import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')


def worker1(d, lock):
    logging.debug('start')
    # ②ロック実行
    lock.acquire()
    i = d['x']
    time.sleep(5)
    d['x'] = i + 1
    logging.debug(d)
    # ③アンロック
    lock.release()
    logging.debug('end')


def worker2(d, lock):
    logging.debug('start')
    # ②ロック実行(worker1の実行が完了するまで、処理を待つ)
    lock.acquire()
    i = d['x']
    d['x'] = i + 1
    logging.debug(d)
    # ③アンロック
    lock.release()
    logging.debug('end')

if __name__ == '__main__':
    d = {'x': 0}
    # ①ロックを作成
    lock = threading.Lock()
    t1 = threading.Thread(target=worker1, args=(d, lock))
    t2 = threading.Thread(target=worker2, args=(d, lock))
    t1.start()
    t2.start()
