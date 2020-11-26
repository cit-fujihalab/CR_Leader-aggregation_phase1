import signal

from core.owner_core import OwnerCore
from core.server_core import ServerCore
from cross_reference.cross_reference_manager import CrossReferenceManager

my_p2p_server_outer = None
my_p2p_server_inner = None

def signal_handler(signal, frame):
	shutdown_server()

def shutdown_server():
	global my_p2p_server_inner
	global my_p2p_server_outer
	my_p2p_server_inner.shutdown()
	my_p2p_server_outer.shutdown()

def main():
	crossref = CrossReferenceManager()
	signal.signal(signal.SIGINT, signal_handler)
	# global my_p2p_server_inner
	global my_p2p_server_outer
	# 始原のCoreノードとして起動する
	my_p2p_server_inner = ServerCore(50075)
	my_p2p_server_inner.start(crm = crossref)
	my_p2p_server_outer = OwnerCore(50080)
	my_p2p_server_outer.start(crm = crossref)


if __name__ == '__main__':
	main()
