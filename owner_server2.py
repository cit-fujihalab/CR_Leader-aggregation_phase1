import signal
from time import sleep

from core.owner_core import OwnerCore
from core.server_core import ServerCore
from cross_reference.cross_reference_manager import CrossReferenceManager
my_p2p_server_outer = None
my_p2p_server_inner = None

def signal_handler(signal, frame):
	shutdown_server()

def shutdown_server():
	global my_p2p_server_outer
	my_p2p_server_outer.shutdown()
	global my_p2p_server_inner
	my_p2p_server_inner.shutdown()

def main():
	count = 0
	crossref = CrossReferenceManager()
	signal.signal(signal.SIGINT, signal_handler)
	global my_p2p_server_inner
	my_p2p_server_inner = ServerCore(50087) # note
	my_p2p_server_inner.start(crm = crossref)
	my_p2p_server_inner.join_network() 

	global my_p2p_server_outer
	# my_p2p_server_outer = OwnerCore(50085, '10.84.247.68',50080) # Dtop
	# my_p2p_server_outer = OwnerCore(50090, '10.84.247.69',50080) # note
	# my_p2p_server_outer = OwnerCore(50090, '192.168.0.142',50080) # note
	my_p2p_server_outer = OwnerCore(50070, '10.84.242.68',50080) # Dtop
	# my_p2p_server_outer = OwnerCore(50085, '10.84.247.102',50080)
	# my_p2p_server_outer = OwnerCore(50070, '192.168.0.127',50080) # Tokyo
	# my_p2p_server_outer = OwnerCore(50085, '10.84.247.102',50080)
	# my_p2p_server_outer = OwnerCore(50070, '10.84.240.73',50080)
	# my_p2p_server_outer = OwnerCore(50070, '192.168.0.7',50080)
	my_p2p_server_outer.start(crm = crossref)
	my_p2p_server_outer.join_DMnetwork()

	print("60sec後にCross_reference開始(whileloop)")
	sleep(60)
	
	while True:
		print(count) 
		if 1000 <= count:
			print("sleep(300)") 
			sleep(300)
			print('!!BREAK!!')
			my_p2p_server_outer.break_time()
			my_p2p_server_inner.break_time()
			sleep(300)
			shutdown_server()
			break
		my_p2p_server_outer.request_cross_reference() #クロスリファレンス開始
		count += 1
		print("=== 履歴交差回数 === :",count)
		print("sleep(300)") 
		sleep(300)
	

if __name__ == '__main__':
	main()
