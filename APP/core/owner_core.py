import time
import socket, threading, json
import copy
from time import sleep
import numpy as np
import hashlib
import logging
import datetime
from datetime import datetime, timedelta
import tkinter as tk
from settings import *

from signature.generate_sigunature import DigitalSignature
from signature.generate_sigunature import CheckDigitalSignature
from blockchain.blockchain_manager import BlockchainManager
from window.generate_window import MainWindow
from p2p.connection_manager_4owner import ConnectionManager4Owner
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
from p2p.owner_node_list import OwnerCoreNodeList
from p2p.message_manager import (
	MSG_REQUEST_CROSS_REFERENCE,
	MSG_ACCEPT_CROSS_REFFERENCE,
	LEADER_AGGREGATION_START_CROSS_REFFERENCE,
	MSG_CROSS_REFFERENCE_LEADER_AGGREGATION,
	REQUEST_POW,
	MSG_CROSS_REFFERENCE,
	START_CROSS_REFFERENCE,
	COMPLETE_CROSS_REFERENCE,
	RAFT_CANDIDATE_LEADER,
	U_RAFT_FOLLOWER,
	IM_RAFT_LEADER,
	RAFT_HEARTBEAT
)

from cross_reference.cross_reference_manager import CrossReferenceManager
# from cross_reference.cross_reference_resistance import CrossReferenceResistance

STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3
#FAILURE_POSSIBILITY = 0.00010000 # 故障確率
# TransactionPoolの確認頻度
# 動作チェック用に数字小さくしてるけど、600(10分)くらいはあって良さそう

class OwnerCore(object):

	def __init__(self, my_port = 50082, owner_node_host=None, owner_node_port=None  ):
		self.server_state = STATE_INIT
		print('Initializing owner server...')
		self.my_ip = self.__get_myip()
		print('Server IP address is set to ... ', self.my_ip)
		self.my_port = my_port
		self.cm = ConnectionManager4Owner(self.my_ip, self.my_port, self.__handle_message, self )
		self.mpmh = MyProtocolMessageHandler()
		self.owner_node_host = owner_node_host
		self.owner_node_port = owner_node_port
		self.gs = DigitalSignature()
		self.ww = MainWindow(self.my_port)
		self.bmc = BlockchainManager()
		self.create_log()
		self.tkinter_state = tkinter_state #tkinter
		self.Raft_initial()
		self.CR_initial()
		self.Experiment_initial()
		logging.debug('debugメッセージ : END __init__')

	def CR_initial(self): #履歴交差関係の初期化
		self.CR_Last_stamp = time.time()
		self.AC = 0
		self.Accept_list = [] #Accept Count
		self.Ccount = 0 
		self.Send_list = []
		self.REcount = 0
		self.RE_Send_list = []
		self.check_count = None
		self.previous_cross_sig = []
		self.CR_INTERVAL = CR_INTERVAL #履歴交差インターバル
		self.CR_state = CR_STATE
		logging.debug('debugメッセージ : END CR_initial')

	def Raft_initial(self):#Raft関係の初期化
		self.Raft_Voting = 0
		self.Voting_Result = []
		self.Candidate = False #あとで確認機能を作る必要がある.
		self.Raft_timer = 0
		# self.Raft_MAX = RAFT_MAX		
		self.CR_count = 0
		self.Raft_Leader_state = None
		self.Raft_Voting_state = False
		self.Leader_C = 0
		self.Lastping_leader = 0 #UNIX時間でタイムスタンプ管理
		self.Last_Heartbeat_time()
		logging.debug('debugメッセージ : END Raft_initial')

	def Experiment_initial(self):#実験関係の初期化
		self.Phase1_list = []
		self.Phase3_list = []
		self.overtime_c = 0
		self.overtime_flag = False
		logging.debug('debugメッセージ : END CR_Experiment_initial')

	def start(self, crm = None):
		self.server_state = STATE_STANDBY
		self.cm.start()
		logging.debug('debugメッセージ : 原始ノードはjoin_DMnetworkは起動しない.')
		self.crm = crm
		self.Raft_Leader_state = True#if
		self.Raft_Leader_loop()

	def window(self):
		if tkinter_state == True:
			print("debugメッセージ : Tkinterを起動します。")
			logging.debug('debugメッセージ : Tkinter')
			self.ww.generate_genesis_window()

		else:
			logging.debug('debugメッセージ : Tkinterオフ')
			pass

	def create_log(self):
		try:
			file_name = "logging/raft_status" + str(self.my_port) + ".log"
			formatter = '%(asctime)s: %(message)s'
			# logging.basicConfig(format=formatter, filename= file_name, level = logging.DEBUG)
			logging.basicConfig(format=formatter, filename= file_name, level = logging.INFO)
			
		except:
			file_name = "APP/logging/raft_status" + str(self.my_port) + ".log"
			formatter = '%(asctime)s: %(message)s'
			# logging.basicConfig(format=formatter, filename= file_name, level = logging.DEBUG)
			logging.basicConfig(format=formatter, filename= file_name, level = logging.INFO)



	def join_DMnetwork(self):
		logging.info('debugメッセージ : join_DMnetwork')
		if self.owner_node_host != None:
			logging.info('debugメッセージ : join_DMnetwork')
		
			self.server_state = STATE_CONNECTED_TO_NETWORK # 状態：親ノードへ接続中
			self.cm.join_DMnetwork(self.owner_node_host, self.owner_node_port)
			#Raftのリーダー状態の更新
			self.Raft_Leader_state = False
			logging.debug('Raft_Leader_state:' + str(self.Raft_Leader_state))
			self.Raft_Follower_loop()

		else:
			print('This server is running as Genesis Owner Node...')
			logging.info('debugメッセージ : leaderがいませんでした。')
			#Raftのリーダー状態の更新
			self.Raft_Leader_state = True
			self.Raft_Leader_loop()

	def Last_Heartbeat_time(self):
		print("Last_Heartbeat_time")
		self.Last_Heartbeat = time.time()
		print("Last_Heartbeat is ",self.Last_Heartbeat)
		print(datetime.fromtimestamp(self.Last_Heartbeat))

	def Time_judge_is_Follower(self): #切り替わりのタイミング
		print("リーダーの生存を検証")
		self.Follower_time = time.time() #datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
		# 現在時刻の確認.
		print("現在時刻の確認")
		logging.info('debugメッセージ : 現在の時刻の確認')
		if  self.Follower_time < self.Last_Heartbeat + ALLOWABLE_TIME:
			print("Renew_Last_Heartbeat", float(self.Last_Heartbeat + ALLOWABLE_TIME ))
			print("Last_Heartbeat",self.Last_Heartbeat)
			print("NEXTCHECK_Heartbeatの方が先の時間")
			print("リーダーのハートビート有効期間")
			print("Followerとして居続ける")
			print("self.Raft_Voting_state", self.Raft_Voting_state)
			logging.info('debugメッセージ : Followerとして居続ける')
			self.Raft_Follower_side = threading.Timer(LEADER_CHECK_INTERVAL, self.Time_judge_is_Follower)
			self.Raft_Follower_side.start()

		else:
			print("Renew_Last_Heartbeat", float(self.Last_Heartbeat + ALLOWABLE_TIME))
			print("Last_Heartbeat", self.Last_Heartbeat)
			print("Follower_time is ", self.Follower_time)
			print("Last_Heartbeatの方が先の時間")
			print("リーダーのハートビート有効期限切れ")
			print("Candidateする")
			logging.info('リーダーのハートビート有効期限切れ')
			logging.info('debugメッセージ : Candidate')
			print("self.Raft_Voting_state", self.Raft_Voting_state)
			self.Raft_Candidate_Leader()

	def shutdown(self):
		self.server_state = STATE_SHUTTING_DOWN # 状態：切断中
		print('Shutdown server...')
		self.cm.connection_close()

	def Raft_Follower_loop(self): # FOLLOWER側の確認LOOP
		logging.info('debugメッセージ : Follower_loop')
		print("000000000000000000000000Follower_loop000000000000000000000000")
		self.Time_judge_is_Follower()
		
	def Raft_Leader_loop(self): # リーダー側の更新LOOP
		CR_stamp = time.time()
		logging.info('1111111111111111111111111Leader_loop1111111111111111111111111')
		print("1111111111111111111111111Leader_loop1111111111111111111111111")
		if self.ww.Break_state == True:
			logging.debug('Tkinterから故障命令')
			self.Leader_broken()

		else:
			self.Leader_loop = threading.Timer(LEADER_UPDATE_INTERVAL, self.Raft_timer_for_Leader)#ここのインターバルはランダムにする必要あり(初期200)
			self.Leader_loop.start()

		logging.debug("故障なし")
		logging.debug("CR_check_stamp" + str(CR_stamp))
		logging.debug("self.CR_Last_stamp" + str(self.CR_Last_stamp))

		if CR_INTERVAL < CR_stamp - self.CR_Last_stamp :
			logging.info("CR_loop発火")
			self.CR_loop()

		else :
			logging.info("最後の履歴交差から" + str(CR_INTERVAL) + "経過していない")

	def Leader_broken(self):
		logging.debug('故障させます。sleep(10000000)' + str(self.my_port))
		print("故障しました。")
		while True:
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("故障しています。")
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			sleep(5)
			if self.ww.Break_state == False:
				logging.debug("フォロワーとして復帰")
				print("フォロワーとして復帰")
				self.Raft_Leader_state = False
				self.Raft_Follower_loop()

	def Raft_reset(self):#投票が行われた際の
		logging.debug('Raftのリセット')
		self.Voting_Result = [] #投票のリセット
		self.Raft_Voting = 0 #立候補の数のリセット
		self.Candidate = False
		self.Raft_Voting_state = False
		# self.Raft_timer = 0
		self.Leader_C = 0
		logging.debug('Raftの投票関連をリセット。')

	def Send_heartbeat(self):
		logging.info("Send_heartbeat")
		if self.Raft_Leader_state == True: #port番号と照合
			self.Lastping_leader = time.time()

		else :
			logging.debug('自分はリーダーではない‥')

	def Raft_timer_for_Leader(self): #スレッドタイマーで回す
		RenewLastping_Leader = time.time()
		if self.Raft_Leader_state == True:
			if RenewLastping_Leader - self.Lastping_leader > 5:
				new_message = self.cm.get_message_text(RAFT_HEARTBEAT)
				self.cm.send_msg_to_all_owner_peer(new_message) #全体に送信
				logging.info("リーダー権の継続"+str(self.my_ip) + "," + str(self.my_port))
				print("リーダー権の継続")			
				self.Raft_Leader_loop()

			else:
				print("直近に5秒以内にping送っている")
				logging.info('直近に5秒以内にping送っている')
				self.Raft_Leader_loop()

		else :
			print("Leader権がなくなっています。もしくは投票モード")
			logging.debug('Leader権がなくなっています。もしくは投票モード。')

	def Raft_Candidate_Leader(self):
		logging.debug('リーダーに立候補する' + str(self.my_ip) + "," + str(self.my_port))
		print("リーダーに立候補する")
		#投票FLAGがTrueなら
		if self.Raft_Voting_state == True:
			print("投票モードに移行しているので立候補をしない")
			self.Candidate = False
			logging('投票モードに移行しているので立候補をしませんでした。')
			print("Followerに戻る")
			self.Raft_Follower_loop()

		else:
			self.Raft_Voting_state = True
			print("投票モードに移行します。")
			new_message = self.cm.get_message_text(RAFT_CANDIDATE_LEADER)
			self.cm.send_msg_to_all_owner_peer(new_message) #全体に送信
			logging.debug('RAFT_CANDIDATE_LEADERを送信しました。')
			#time outを決める。

	def CR_loop(self):#自分がリーダーか確認して
		logging.info('CR_loop開始')
		n = self.crm.ref_block_number
		logging.info("1つ前の履歴交差ブロックnum : " + str(n))
		if self.CR_state == True:
			if self.cm.adding_timer + NEW_CONNECTION < time.time():
				self.CR_Last_stamp = time.time()
				if len(self.cm.owner_node_set.get_list()) > MINIMUM_DOMAIN:
					self.CR_count += 1
					self.request_cross_reference()#ここのインターバルはランダムにする必要あり
					logging.debug('履歴交差開始' + str(self.CR_count))
					logging.debug("履歴交差タイムスタンプの更新A")

				else:
					logging.debug('履歴交差に必要なドメイン数を確保まで履歴交差はできません.\n ドメイン数: ' + str(len(self.cm.owner_node_set.get_list())))
					logging.debug("履歴交差タイムスタンプの更新B")
					
			else:
				logging.debug("新しいコネクションが" + str(NEW_CONNECTION) + "秒以内にあり") 
				print("")
		#履歴交差を開始する。
		else:
			print("理由があって履歴交差を行わない。")
			logging('理由があって履歴交差を行わない。')
			# self.CR_loop#ここのインターバルはランダムにする必要あり

#-----------------------------------------------------------------------------------------------------------------------------------------
	def request_cross_reference(self):
		print("履歴交差開始stateを確認")
		#time計測なし self.crm.time_start_phase1()#time計測なし
		self.crm.time_start_phase1()
		self.check_count = 11
		print(" ============= Phase1 start =============")
		self.crm.inc += 1
		print("start_request_cross_reference")
		#耐故障猶予時間開始
		self.Send_heartbeat()
		if LEADER_AGGREGATION == True:
			self.cross_reference_reset()
		new_message = self.cm.get_message_text(MSG_REQUEST_CROSS_REFERENCE)
		self.cm.send_msg_to_all_owner_peer(new_message)

	def start_cross_reference(self):
		print("start_request_crose_reference")
		block_l = json.dumps(self.crm.block_ref())
		block_msg = self._get_hash_sha256(block_l)
		self.crm.add_cross_reference(block_msg)
		self.crm.myblock_in = True
		new_message = self.cm.get_message_text(MSG_CROSS_REFFERENCE, json.dumps(block_msg, sort_keys = True ,ensure_ascii = False))
		# print("new_message",new_message)
		print("============= start_request_crose_reference =============")
		logging.info("============= start_request_crose_reference =============")
		self.Send_heartbeat()
		self.cm.send_msg_to_all_owner_peer(new_message)

	def current_crossref(self, msg):
		#logging.debug("cross_re" + str(type(cross_re)) + str(cross_re))
		self.crm.add_cross_reference(msg)

	def cross_sig(self, cre):
		cross_sig = self.gs.add_public_key(cre)
		return cross_sig

	def _get_hash_sha256(self, message):
		return hashlib.sha256(message.encode()).hexdigest()

	def complete_cross_block(self, msg):
		logging.info("complete_cross_block()")
		#time計測なし if self.overtime_flag:
		#	overtime = str( str(self.overtime_c ) + "turn" + str(self.overtime_t) + "sec \n" + str(msg) + "\n")
		#	with open( 'TIME/overtime.txt' , mode ='a') as f:
		#		f.write(overtime)
		#		self.overtime_flag = False
		if LEADER_AGGREGATION == True:
			new_message = self.cm.get_message_text(COMPLETE_CROSS_REFERENCE, msg)
			self.Send_heartbeat()
			self.cm.send_msg_to_all_owner_peer(new_message)
			
		else:
			self.cross_reference_reset()
			new_message = self.cm.get_message_text(COMPLETE_CROSS_REFERENCE, msg)
			self.Send_heartbeat()
			self.cm.send_msg_to_all_owner_peer(new_message)
		
	def cross_reference_reset(self):
		# tp3 = self.crm.time_stop()
		# self.inc += 1
		"""
		print("======= end Phase3 ======= : ",tp3 )
		if tp3 :
			time = str( "\n Turn " + str(self.crm.inc)  + " : Phase3: " + str(tp3) + " sec")
			self.Phase3_list.append(time)
		"""
		# Re-Set
		print("cross_reference_ALL RESET")
		print("refresh crossre ference pool")
		self.crm.clear_cross_reference()
		print( "refresh crossre ference pool")
		logging.debug("clear後のself.crm.cross_reference is" + str(self.crm.cross_reference))
		self.AC = 0 # Reset
		self.Ccount = 0
		self.REcount = 0
		# self.crm.flag = False
		self.crm.myblock_in = False
		logging.info("cross_reference_reset is ok----Full-Reset")
		print("ok----Full-Reset")


	def myblock_in_check(self):#リーダー集約の時には通らない。
		logging.debug("myblock_in_check")
		if self.crm.myblock_in == True: #自分のブロックを入れてるか確認
			msg = self.crm.hysteresis_sig()
			self.crm.set_new_cross_reference(msg)
			print(" ============= (マイニング) Phase2 start =============")
			logging.debug("myblock_in_check-完了")
			if LEADER_AGGREGATION == True:
				logging.debug("リーダー集約モード\n集約した内容を全体に送信")
				self.cross_reference_reset()
				new_message = self.cm.get_message_text(REQUEST_POW, msg) # マイニングの依頼
				self.Send_heartbeat()
				self.cm.send_msg_to_all_owner_peer(new_message)
				
			else:
				complete = threading.Timer(30, self.complete_cross_block(msg)) # 条件分岐で
				complete.start()
				return 0

		else:
			recheck = threading.Timer(REF_RECHECK, self.myblock_in_check)
			recheck.start()	
			logging.debug("myblock_in_check-再チェック開始")
			return 1

	def __handle_message(self, msg, is_owner, peer=None):
		if self.ww.Break_state == True:
			logging.debug("ーー故障中ーーハンドルメッセージに応答しない")
			pass

		elif msg[2] == MSG_REQUEST_CROSS_REFERENCE:
			self.crm.time_start_phase1()
			self.cross_reference_reset()
			# Re-Set
			print("cross_reference_ALL RESET")
			print("refresh crossre ference pool")
			logging.debug('MSG_REQUEST_CROSS_REFERENCE:')
			print("MSG_REQUEST_CROSS_REFERENCE:")
			#履歴交差了解MSG リクエストok
			new_message = self.cm.get_message_text(MSG_ACCEPT_CROSS_REFFERENCE)
			self.cm.send_msg(peer, new_message, delay = False) #True) #delay消してる。

		elif msg[2] == MSG_ACCEPT_CROSS_REFFERENCE: # ACCEPTを受け取ったら
			logging.debug('MSG_ACCEPT_CROSS_REFFERENCE')
			#Failure_resistance_time = #耐故障猶予時間
			print("MSG_ACCEPT_CROSS_REFFERENCE")
			print("self.o_list.get_list = ", self.cm.owner_node_set.get_list())

			if self.AC == 0:
				self.AC = 1
				self.Accept_list = copy.deepcopy(self.cm.owner_node_set.get_list())
				if peer in self.Accept_list:
					self.Accept_list.remove(peer)
			elif self.AC >= 1:
				if peer in self.Accept_list:
					self.Accept_list.remove(peer)
			else:
				pass

			# 履歴交差部
			if len(self.Accept_list) == 1: #Accept Count
				print("ok----------------------------ACCEPT_CROSS_REFERENCE")
				print("SEND_START")
				self.check_count = 22

				if LEADER_AGGREGATION == True:
					logging.debug("リーダーが集約するモード")
					
					block_l = json.dumps(self.crm.block_ref())
					block_msg_M = self._get_hash_sha256(block_l)
					c = self.gs.compute_digital_signature(block_msg_M)
					logging.debug('self.gs.get_private_key' + str(c))
					logging.debug('block_msg' + str(block_l))
					msg_d = {
						c + "__PORT(" + str(self.my_port) + ")":block_msg_M + "__(Block_Hash)"
					}
					logging.debug("署名文:block_hash" + str(msg_d))
					self.current_crossref(msg_d)
					
					logging.debug("self.crm.cross_reference is :" + str(self.crm.cross_reference))
					
					new_message = self.cm.get_message_text(LEADER_AGGREGATION_START_CROSS_REFFERENCE)
					self.cm.send_msg_to_all_owner_peer(new_message)
					self.Send_heartbeat()
					
				else:
					new_message = self.cm.get_message_text(START_CROSS_REFFERENCE)
					self.cm.send_msg_to_all_owner_peer(new_message)
					self.Send_heartbeat()
					# 履歴交差開始
					print("accept next履歴交差開始")
					self.start_cross_reference()

		elif msg[2] == START_CROSS_REFFERENCE: #リーダー集約時は通らない。
			logging.info(START_CROSS_REFFERENCE)
			print("START_CROSS_REFFERENCE")
			print("履歴交差開始")
			if LEADER_AGGREGATION == False:
				self.start_cross_reference()

			else:
				logging.debug("リーダーが集約するモード")

		elif msg[2] == MSG_CROSS_REFFERENCE_LEADER_AGGREGATION: #追加0222
			logging.info('MSG_CROSS_REFFERENCE_LEADER_AGGREGATION @' + str(peer))
			# cross_reference部のへの追加

			msg_loads = json.loads(msg[4])

			print("受信HASH:" ,msg_loads)	

			if self.Ccount == 0:
				self.Ccount = 1
				self.Send_list = copy.deepcopy(self.cm.owner_node_set.get_list())
				logging.debug("sendlist is" + str(self.Send_list))
				
				if peer in self.Send_list:
					self.Send_list.remove(peer)
					self.current_crossref(msg_loads)
					logging.critical("A-1")
				else:
					logging.critical("A-2")
					pass
			elif self.Ccount >= 1:
				if peer in self.Send_list:
					self.Send_list.remove(peer)
					self.current_crossref(msg_loads)
					logging.critical("B-1")
				else:
					logging.critical("B-2")
					pass
			else:
				logging.critical("C")
				pass

			if len(self.Send_list) == 1:
				logging.debug("他ドメインからのCROSS_REFERENCE_ACCEPT_ALL_NODE 全ノード受信完了")
				# マイニング依頼
				## リーダーの格納
				msg = self.crm.hysteresis_sig()
				logging.debug("msg is :" + str(type(msg)))
				self.crm.set_new_cross_reference(msg) #ここ1
				print("self.reference", self.crm.reference)
				print("============== type ==============" + str(type(self.crm.reference)))
				logging.debug("self.reference" + str(self.crm.reference))
				logging.debug("======= type =======" + str(type(self.crm.reference)))
				#logging.debug("self.reference" + str(P))
				block_msg_C = self.crm.get_reference_pool() #ここ1 str
				print("block_msg_C", block_msg_C)
				print("block_msg_C", type(block_msg_C))
				logging.debug("block_msg_C" + str(block_msg_C))
				logging.debug("======= type =======" + str(type(block_msg_C)))
				new_message = self.cm.get_message_text(REQUEST_POW, json.dumps(block_msg_C, sort_keys = True ,ensure_ascii = False))
				logging.info("REQUEST_POWを全ドメインに送信")
				self.cm.send_msg_to_all_owner_peer(new_message)
				print("============= self.crm.time_stop_phase1() =============")
				phase1_time = self.crm.time_stop_phase1()
				self.crm.phase1_list.append(phase1_time)
				print("self.crm.Phase1_list", self.crm.phase1_list)
				print(" ============= (マイニング) Phase2 start =============")
				# Leader  Layer1側で取得したcroos_reference__type<class 'str'>
				# Follower Layer1側で取得したcroos_reference__type<class 'list'>

				# complete = threading.Timer(30, self.complete_cross_block(msg)) # 条件分岐で
				# complete.start()
				
		elif msg[2] == REQUEST_POW:
			print("REQUEST_POW")
			logging.debug("REQUEST_POW == msg[4] ==" + str(type(msg[4])))
			msg_loads = json.loads(msg[4])
			# self.current_crossref(msg_loads)
			logging.info("リーダーからのマイニング依頼を受信 --- REQUEST_POW")
			# print("msg_loads is :", type(msg_loads))
			logging.debug("msg_loads is " + str( msg_loads))
			logging.debug("msg_loads is type is" + str(type(msg_loads)))
			logging.info("マイニングプールへ保管")
			self.crm.cross_reference = eval(msg_loads)
			msg = self.crm.hysteresis_sig()
			logging.debug("=================== msg is =================== 1 : " + str(msg))			
			self.crm.set_new_cross_reference(msg)
			# print("msg is : " + str(type(msg)))
			phase1_time = self.crm.time_stop_phase1()
			self.crm.phase1_list.append(phase1_time)
			print("phase1 time is :", phase1_time)
			logging.debug("=================== msg is =================== 1: " + str(type(msg)))
			print(" ============= (マイニング) Phase2 start ============= ")
			logging.info(" ============= (マイニング) Phase2 start ============= ")

			# complete = threading.Timer(30, self.complete_cross_block(msg)) # 条件分岐で
			# complete.start()
			
		elif msg[2] == LEADER_AGGREGATION_START_CROSS_REFFERENCE: #追加0222 リーダーが集約した内容を受信
			logging.debug('LEADER_AGGREGATION_START_CROSS_REFFERENCE @' + str(peer)) # @LEADER
			# リーダーからの受信してフォロワーが返信
			# 履歴交差部の返信
			#MSG_CROSS_REFFERENCE_LEADER_AGGREGATION
			print("start_リーダ集約_crose_reference")
			block_l = json.dumps(self.crm.block_ref())
			block_msg = self._get_hash_sha256(block_l)
			# self.crm.add_cross_reference(block_msg)いらない
			self.crm.myblock_in = True
			c = self.gs.compute_digital_signature(block_msg)
			logging.debug('block_msg' + str(block_l))
			msg_d = {
				c + "__PORT(" + str(self.my_port) + ")":block_msg + "__(Block_Hash)"
			}
			logging.debug("秘密鍵:block_hash" + str(msg_d))
			new_message = self.cm.get_message_text(MSG_CROSS_REFFERENCE_LEADER_AGGREGATION, json.dumps(msg_d, sort_keys = True ,ensure_ascii = False))
			print("============= start_cross_reference__Leader_aggregation =============")
			logging.info("============= start_cross_reference__Leader_aggregation =============")
			self.cm.send_msg(peer ,new_message, delay = False) # リーダーに返信
			logging.info("MSG_CROSS_REFFERENCE_LEADER_AGGREGATIONをリーダーに返信")
			self.Send_heartbeat

		elif msg[2] == MSG_CROSS_REFFERENCE: #リーダー集約時にはここを通らないはず
			logging.debug('リーダー集約時にはここを通らないはず' + str(peer))
			logging.debug('MSG_CROSS_REFFERENCE @' + str(peer))
			#iDの照合m
			print("received : MSG_CROSS_REFFERENCE")
			# cross_reference部のへの追加
			print("マイニング Phase1-1")
			msg_loads = json.loads(msg[4])

			print("自身HASH:" ,msg_loads)	

			if self.Ccount == 0:
				self.Ccount = 1
				self.Send_list = copy.deepcopy(self.cm.owner_node_set.get_list())
				logging.debug("sendlist is" + str(self.Send_list))
				
				if peer in self.Send_list:
					self.Send_list.remove(peer)
					self.current_crossref(msg_loads)
					logging.critical("A-1")
				else:
					logging.critical("A-2")
					pass
			elif self.Ccount >= 1:
				if peer in self.Send_list:
					self.Send_list.remove(peer)
					self.current_crossref(msg_loads)
					logging.critical("B-1")
				else:
					logging.critical("B-2")
					pass
			else:
				logging.critical("C")
				pass

			if len(self.Send_list) == 1:
				logging.debug("他ドメインからのCROSS_REFERENCE_ACCEPT_ALL_NODE 全ノード受信完了")
				check = self.myblock_in_check() #追加
				logging.debug("block-check-while前" + str(check))
				if check == 0:
					logging.debug("block-check完了" + str(check))
				
				else:
					logging.debug("block-check再チェック待ち" + str(check))

		elif msg[2] == COMPLETE_CROSS_REFERENCE:
			print(" ==== OK ==== COMPLETE_CROSS_REFERENCE ==== ")
			logging.debug(" ==== OK ==== COMPLETE_CROSS_REFERENCE ==== ")

#------------------------------ Raft --------------------------------------------------
		elif msg[2] == RAFT_CANDIDATE_LEADER: #相手から立候補からありました.
			self.Last_Heartbeat_time() #事実上の暫定のリーダーからのものを更新するべきか。
			print("msg[2] == Raft_My_Leader")
			logging.debug(str(peer) + "からRAFT_CANDIDATE_LEAADERを受信しました。投票モードに移行しました。")
			print("私がリーダーに立候補しました。for ",peer)

			if self.Raft_Voting == 0:
				self.Raft_Voting_state = True
				print("立候補を認めます. ＝ 承認")
				self.Raft_Voting = +1 #立候補を認知
				new_message = self.cm.get_message_text(U_RAFT_FOLLOWER)
				self.cm.send_msg(peer,new_message, delay = False)
			
			else:
				print("立候補を認めません. ＝ 否認")
				logging.debug("立候補を認めません. ＝ 否認 今の所否認することはない。")
				#否認なら何も送らない.
				#リセットしないと

		elif msg[2] == U_RAFT_FOLLOWER: #相手からの立候補の承認がありました.
			print("あなたがリーダーになったことを認めますよ")
			#過半数を超えるとリーダーになれる.
			print("投票結果を集計中")
			self.Voting_Result.append(peer) #投票結果
			B = len(self.Voting_Result)
			A = copy.deepcopy(self.cm.owner_node_set.get_list())
			if len(A)/2 <= B: # 各ドメインの中心コアノードの過半数
				self.Raft_Leader_state = True
				print("過半数を獲得しリーダーとして承認されました")
				logging.debug("過半数を獲得しリーダーとして承認されました。")
	
				new_message = self.cm.get_message_text(IM_RAFT_LEADER) 
				#Follower_listを添付して全体に検証してもらった方がいいかもほうがいいかも
				self.cm.send_msg_to_all_owner_peer(new_message) #承認されたことを全体に送信

				self.Raft_reset_timer = threading.Timer(60, self.Raft_reset)#投票内容をReset
				self.Raft_reset_timer.start()
				self.Raft_Leader_loop()

			else:
				print("未だ過半数の承認を得られていません.")
				logging.debug("未だ過半数として承認されていません.")

		elif msg[2] == IM_RAFT_LEADER: #リーダの決定通知
			self.Last_Heartbeat_time() #最終ハートビートの更新
			#私がリーダで確定しました.
			self.Raft_Leader_state = False
			print("Re new leader is", peer)
			self.Raft_Leader = peer

			print("投票モードの終了")
			logging.debug("IM_RAFT_LEADE投票モードの終了 :Raft_Voting_state is)" + str(self.Raft_Voting_state))

			self.Raft_Leader_state = False
			self.Raft_reset()

			logging.debug("IM_RAFT_LEADER Leader_stateの更新" + str(self.Raft_Leader_state) + "時間を上限値に戻す" + str(self.Raft_timer))
			self.Raft_Follower_loop()
			
		elif msg[2] == RAFT_HEARTBEAT: #リーダの継続申請
			logging.debug('RAFT_HEARTBEATの受け取った')
			print("RAFT_HEARTBEATの受け取った")
			#ハートビート履歴の更新
			self.Last_Heartbeat_time() #最終ハートビートの更新
			#self.Raft_timer_decrement_Follower(msg[4])

	"""	
	def _get_double_sha256_r1(self,message):
		return hashlib.sha256(hashlib.sha256(message).digest()).digest()

    def get_hash_r1(self,block):
		""#
        正当性確認に使うためブロックのハッシュ値を取る
            param
                block: Block
        ""#
        print('BlockchainManager: get_hash was called!')
        block_string = json.dumps(block, ensure_ascii=False, sort_keys=True)
        # print("BlockchainManager: block_string", block_string)
        return binascii.hexlify(self._get_double_sha256((block_string).encode('utf-8'))).decode('ascii')
	"""

	def __get_myip(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		return s.getsockname()[0]

