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
	crossref = CrossReferenceManager()
	signal.signal(signal.SIGINT, signal_handler)
	global my_p2p_server_inner
	my_p2p_server_inner = ServerCore(50077) # note
	my_p2p_server_inner.start(crm = crossref)
	my_p2p_server_inner.join_network() 

	global my_p2p_server_outer
	# my_p2p_server_outer = OwnerCore(50085, '10.84.247.68',50080) # Dtop
	# my_p2p_server_outer = OwnerCore(50050, '10.84.247.69',50080) # note
	# my_p2p_server_outer = OwnerCore(50050, '192.168.0.127',50080) # note Barcelona
	# my_p2p_server_outer = OwnerCore(50050, '10.84.240.73',50080)
	my_p2p_server_outer = OwnerCore(50050, '192.168.0.7',50080)
	my_p2p_server_outer.start(crm = crossref)
	my_p2p_server_outer.join_DMnetwork()



if __name__ == '__main__':
	main()
