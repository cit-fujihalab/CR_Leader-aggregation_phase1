import time
import socket, threading, json
import copy
import pickle
import base64
import zipfile
import os
from time import sleep
import numpy as np
import hashlib
import logging
# from kivy.app import App
# from kivy.uix.label import Label

from signature.generate_sigunature import DigitalSignature
from signature.generate_sigunature import CheckDigitalSignature
from p2p.connection_manager_4owner import ConnectionManager4Owner
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
from p2p.owner_node_list import OwnerCoreNodeList
from p2p.message_manager import (
	MSG_NEW_TRANSACTION,
	MSG_NEW_BLOCK,
	MSG_REQUEST_FULL_CHAIN,
	RSP_FULL_CHAIN,
	MSG_ENHANCED,
	MSG_REQUEST_CROSS_REFERENCE,
	MSG_ACCEPT_CROSS_REFFERENCE,
	MSG_CROSS_REFFERENCE,
	START_CROSS_REFFERENCE,
	COMPLETE_CROSS_REFERENCE

)
from cross_reference.cross_reference_manager import CrossReferenceManager
# from cross_reference.cross_reference_resistance import CrossReferenceResistance

STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3

# TransactionPoolの確認頻度
# 動作チェック用に数字小さくしてるけど、600(10分)くらいはあって良さそ

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

		self.AC = 0
		self.Accept_list = None #Accept Count
		self.Ccount = 0 
		self.Send_list = None
		self.REcount = 0
		self.RE_Send_list = None
		self.check_count = None
		# self.previous_cross_sig = []
		# self.inc = 0
		self.Phase1_list = []
		# self.Phase3_list = []
		self.overtime_c = 0
		self.overtime_flag = False

	def start(self, crm = None):
		self.server_state = STATE_STANDBY
		self.cm.start()
		self.crm = crm

	def join_DMnetwork(self):
		if self.owner_node_host != None:
			self.server_state = STATE_CONNECTED_TO_NETWORK # 状態：親ノードへ接続中
			self.cm.join_DMnetwork(self.owner_node_host, self.owner_node_port)
		else:
			print('This server is running as Genesis Core Node...')

	def shutdown(self):
		self.server_state = STATE_SHUTTING_DOWN # 状態：切断中
		print('Shutdown server...')
		self.cm.connection_close()

	def get_my_current_state(self):
		return self.server_state

	def request_cross_reference(self):
		#time計測なし self.crm.time_start_phase1()#time計測なし
		print('thread-started')
		print(" ============= Phase1 start =============")
		self.crm.inc += 1
		print("start_request_cross_reference")
		#耐故障猶予時間開始
		new_message = self.cm.get_message_text(MSG_REQUEST_CROSS_REFERENCE)
		self.cm.send_msg_to_all_owner_peer(new_message)

	def start_cross_reference(self):
		print("start_request_crose_reference")
		block_hash = str(np.random.randint(10000000, 100000000))
		block_msg = {}
		block_msg["block"] = block_hash
		new_message = self.cm.get_message_text(MSG_CROSS_REFFERENCE, json.dumps(block_msg, sort_keys = True ,ensure_ascii = False))
		print("new_message",new_message)
		block_in = self._get_hash_sha256(block_hash)
		self.crm.add_cross_reference(block_in)
		print("============= start_request_crose_reference =============")
		self.cm.send_msg_to_all_owner_peer(new_message)

	def current_crossref(self, msg):
		cross_re = json.loads(msg)
		cross_ref = cross_re["block"]
		block_in = self._get_hash_sha256(cross_ref) # hash_syori 
		self.crm.add_cross_reference(block_in)

	def cross_sig(self, cre):
		cross_sig = self.gs.add_public_key(cre)
		return cross_sig

	def _get_hash_sha256(self, message):
		return hashlib.sha256(message.encode()).hexdigest()

	def complete_cross_block(self, msg):
		print("complete_cross_block()")
		#time計測なし if self.overtime_flag:
		#	overtime = str( str(self.overtime_c ) + "turn" + str(self.overtime_t) + "sec \n" + str(msg) + "\n")
		#	with open( 'TIME/overtime.txt' , mode ='a') as f:
		#		f.write(overtime)
		#		self.overtime_flag = False
		new_message = self.cm.get_message_text(COMPLETE_CROSS_REFERENCE, msg)
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
		self.crm.clear_cross_reference()
		print( "refresh crossre ference pool")
		self.AC = 0 # Reset
		self.Ccount = 0
		self.REcount = 0
		# self.crm.flag = False
		print("ok----Full-Reset")

	"""
	def break_time(self):
		for i in self.Phase1_list :
			with open( 'TIME/Phase1.txt' , mode ='a') as f:
				f.write(i)
		print("All in Phase1")
		
		for j in self.Phase3_list :
			with open( 'TIME/Phase3.txt' , mode ='a') as f:
				f.write(j)
		print("All in Phase3")
		
	"""
	#if self.Accept_list > 1: #current_accept_list
			#1以上なら確認する。

	#def Failure_resistance_disconnection(self):#耐停止故障
		#受信できないドメインに再送（相手が悪い）

	#def Failure_resistance_disconnectionAtoB(self):#耐停止故障
		#自分が送信できない（自分が悪い?）
	
	def start_ref_building(self):
		self.ref = threading.Timer(20, self.check_resisrtance)
		self.ref.start()

	def check_resistance(self):
		if self.check_count == 1:#1回目に呼ばれたら
			if len(self.Accept_list) == 1:
				pass
			else:
				print("どこか故障した？")
				print(self.Accept_list)
				
		if self.check_count == 2:
			if len(self.Send_list) == 1:
				print("not Failureok!")
				pass
			else:
				print("どこか故障した？")


	def __handle_message(self, msg, is_owner, peer=None):

		if msg[2] == MSG_REQUEST_CROSS_REFERENCE:
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("故障しました。sleep10000")
			print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")	
			sleep(10000)

			#Failure_resistance_time = #耐故障猶予時間
			print("MSG_REQUEST_CROSS_REFERENCE:")
			#履歴交差了解MSG リクエストok
			new_message = self.cm.get_message_text(MSG_ACCEPT_CROSS_REFFERENCE)
			self.cm.send_msg(peer,new_message, delay = False) #True) #delay消してる。

		elif msg[2] == MSG_ACCEPT_CROSS_REFFERENCE: # ACCEPTを受け取ったら
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
				print("ok-----------------------------CROSS_REFERENCE")
				print("SEND_START")
				new_message = self.cm.get_message_text(START_CROSS_REFFERENCE)
				self.cm.send_msg_to_all_owner_peer(new_message)
				# 履歴交差開始
				print("accept next履歴交差開始")
				self.start_cross_reference()

		elif msg[2] == START_CROSS_REFFERENCE:
			print("START_CROSS_REFFERENCE")
			print("履歴交差開始")
			self.start_cross_reference()

		elif msg[2] == MSG_CROSS_REFFERENCE:
			#iDの照合
			print("MSG_CROSS_REFFERENCE")
			# cross_reference部のへの追加
			print("マイニング Phase1-1")

			if self.Ccount == 0:
				self.Ccount = 1
				self.Send_list = copy.deepcopy(self.cm.owner_node_set.get_list())
				
				if peer in self.Send_list:
					self.Send_list.remove(peer)
					self.current_crossref(msg[4])
				else:
					pass
			elif self.Ccount >= 1:
				if peer in self.Send_list:
					self.Send_list.remove(peer)
					self.current_crossref(msg[4])
				else:
					pass
			else:
				pass

			if len(self.Send_list) == 1:

				# blockの中身が確定
				print("CROSS_REFERENCE_ACCEPT_ALL_NODE　全ノード受信完了")
				#time計測なし tp1 = self.crm.time_stop_phase1()
				#time計測なし print(" ============= Phase1 end ============= time_is:",tp1)
				#time計測なし if tp1 :
				#time計測なし	time = str( "\n Turn" + str(self.crm.inc)  + " : Phase1: " + str(tp1) + " sec")
				#time計測なし	print(time)
				#time計測なし	self.Phase1_list.append(time)

				#time計測なし	if tp1 > 10:
				#time計測なし		self.overtime_c = +1
				#time計測なし		self.overtime_t = tp1
				#time計測なし		self.overtime_flag = True

				print(" ============= (マイニング) Phase2 start =============")
				#time計測なし self.crm.time_start_phase2() # phase2-1 start

				msg = self.crm.hysteresis_sig()
				self.crm.set_new_cross_reference(msg)

				#time計測なし self.crm.time_start_phase3() # phase3 start
				print(" ============= Phase3 start ============= ")

				# phase3 start
				sleep(30)
				self.complete_cross_block(msg)


		elif msg[2] == COMPLETE_CROSS_REFERENCE:
			print(" ==== OK ==== COMPLETE_CROSS_REFERENCE ==== ")
			print("self.cross_reference", self.crm.reference)
			# Re-Set
			print("cross_reference_ALL RESET")
			# できた
			# self.previous_cross_sig #前sigの更新　
			if self.REcount == 0:
				# self.crm.time_start() # phase3 start
				# print(" ============= Phase3 start ============= ")
				self.REcount = 1
				self.RE_Send_list = copy.deepcopy(self.cm.owner_node_set.get_list())

			elif self.REcount >= 1:
				if peer in self.RE_Send_list:
					self.RE_Send_list.remove(peer)
					if len(self.RE_Send_list) == 1:
						self.cross_reference_reset()
						print( "refresh crossre ference pool")

	def __get_myip(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		return s.getsockname()[0]
