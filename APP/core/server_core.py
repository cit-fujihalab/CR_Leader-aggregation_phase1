import time
import socket, threading, json
from settings import *
import pickle
import base64
import zipfile
import os
from settings import *
import logging
import sys
import numpy as np

from LDB import main_level

from signature.generate_sigunature import CheckDigitalSignature
from blockchain.blockchain_manager import BlockchainManager
from blockchain.block_builder import BlockBuilder
from transaction.transaction_pool import TransactionPool
from p2p.connection_manager import ConnectionManager
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
from p2p.message_manager import (
	MSG_NEW_TRANSACTION,
	MSG_NEW_BLOCK,
	MSG_REQUEST_FULL_CHAIN,
	RSP_FULL_CHAIN,
	MSG_ENHANCED,
	Sync_DB3
)

from p2p.connection_manager import LDB_P, PARAM_P, ZIP_P

STATE_INIT = 0
STATE_STANDBY = 1
STATE_CONNECTED_TO_NETWORK = 2
STATE_SHUTTING_DOWN = 3

# TransactionPoolの確認頻度
# 動作チェック用に数字小さくしてるけど、600(10分)くらいはあって良さそ
dirname = os.path.dirname(__file__).replace("core", "")

class ServerCore(object):

	def __init__(self, my_port = 50082, core_node_host=None, core_node_port=None, crm = None):
		self.server_state = STATE_INIT
		print('Initializing core server...')
		self.my_ip = self.__get_myip()
		print('Server IP address is set to ... ', self.my_ip)
		self.my_port = my_port
		self.cm = ConnectionManager(self.my_ip, self.my_port, self.__handle_message, self ) #, self.main_window.set_cnode_list, self.main_window.set_enode_list)
		self.mpmh = MyProtocolMessageHandler()
		self.core_node_host = core_node_host
		self.core_node_port = core_node_port
		self.bb = BlockBuilder()
		self.flag_stop_block_build = False
		self.is_bb_running = False
		my_genesis_block = self.bb.generate_genesis_block()
		self.bm = BlockchainManager(my_genesis_block.to_dict())
		self.prev_block_hash = self.bm.get_hash(my_genesis_block.to_dict())
		self.tp = TransactionPool()

		self.block_num = 0
		self.refblock_count = 0 #履歴交差回数を確認して 
		self.Phase2_list = []
		# self.Phase3_list = []
		self.filesave_flag = True

		if core_node_host and core_node_port:
			self.plz_share_db()
			# self.get_all_chains_for_resolve_conflict()
		# self.main_window.set_port(self.my_port)

		if Random_CHECK_INTERVAL_FLAG == True:
			print("Randomフラグ is True")
			self.bb_interval = np.random.choice(CHECK_INTERVAL_LIST)
			print("self.bb_interval is", self.bb_interval)

		else:
			print("Randomフラグ is Not True")
			self.bb_interval = CHECK_INTERVAL

	def start_block_building(self):
		self.bb_timer = threading.Timer(self.bb_interval, self.__generate_block_with_tp)
		self.bb_timer.start()

	def stop_block_building(self):
		print('Thread for __generate_block_with_tp is stopped now')
		self.bb_timer.cancel()

	def start(self, crm=None ):
		self.server_state = STATE_STANDBY
		self.cm.start()
		self.crm = crm
		self.start_block_building()

	def join_network(self):
		if self.core_node_host != None:
			self.server_state = STATE_CONNECTED_TO_NETWORK # 状態：親ノードへ接続中
			self.cm.join_network(self.core_node_host, self.core_node_port)
		else:
			print('This server is running as Genesis Core Node...')

	def shutdown(self):
		self.server_state = STATE_SHUTTING_DOWN # 状態：切断中
		print('Shutdown server...')
		self.cm.connection_close()
		self.stop_block_building()

	def get_my_current_state(self):
		return self.server_state
	
	def plz_share_db(self):
		print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
		print("■■■■■■■■■■■■■ plz_share_db ■■■■■■■■■■■■■■■■■■■■")
		print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
		new_message = self.cm.get_message_text(Sync_DB3)
		self.cm.send_msg((self.core_node_host, self.core_node_port), new_message)
		print("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")

	def get_all_chains_for_resolve_conflict(self):
		print('get_all_chains_for_resolve_conflict called')
		new_message = self.cm.get_message_text(MSG_REQUEST_FULL_CHAIN)
		self.cm.send_msg_to_all_peer(new_message)

	def break_time(self):
		for k in self.Phase2_list :
			with open( 'TIME/Phase2.txt' , mode ='a') as f:
				f.write(k)
		print("All in Phase2")

		# for j in self.Phase3_list :
		# 	with open( 'TIME/Phase3.txt' , mode ='a') as f:
		#		f.write(j)
		# print("All in Phase3")



	def __generate_block_with_tp(self):

		print('Thread for generate_block_with_tp started!')
		if self.flag_stop_block_build is not True:

			result_tp = self.tp.get_stored_transactions()
			cross_reference = self.crm.get_reference_pool()
			print("/////////////////////////////////////",cross_reference)
			logging.debug("Layer1側で取得したcroos_reference__" + str(cross_reference))
			print(("Layer1側で取得したcroos_reference__type" + str(type(cross_reference)))) ##str
			print(len(cross_reference))
			print("check_cross_reference pool")

			self.block_num += 1
			print(self.crm.check_ref_block_num())
			logging.debug("self.crm.check_ref_block_num()" + str (self.crm.check_ref_block_num()))

			if cross_reference:
				self.crm.ref_block_number(self.block_num)
				self.refblock_count += 1 #履歴交差回数の確認
				print("===== 履歴交差回数 =====", self.refblock_count)

			if result_tp == []:
				print('Transaction Pool is empty ...')
				#TODO:Create Empty Block
				new_block = self.bb.generate_new_block("", self.prev_block_hash, cross_reference, self.block_num)
				self.bm.set_new_block(new_block.to_dict())
				self.prev_block_hash = self.bm.get_hash(new_block.to_dict())
				message_new_block = self.cm.get_message_text(MSG_NEW_BLOCK, json.dumps(new_block.to_dict(), sort_keys=True, ensure_ascii=False))
				self.cm.send_msg_to_all_peer(message_new_block)
				index = len(result_tp)
				self.tp.clear_my_transactions(index)
				if cross_reference:
					print("履歴交差部に入っているから情報をクリアします.")
					logging.info("履歴交差部に入っているから情報をクリアします.")
					self.crm.clear_my_reference()
				tp2 = self.crm.time_stop_phase2()
				if tp2:
					print("Phase2_time:",tp2)
					time = str( "\n Turn" + str(self.crm.inc)  + " : Phase2: " + str(tp2) + " sec")
					print(time)
					self.Phase2_list.append(time)
					# with open( 'TIME/Pheae2.txt' , mode ='a') as f:
					# 	f.write(time)

			new_tp = self.bm.remove_useless_transaction(result_tp)
			self.tp.renew_my_transactions(new_tp)
			if len(new_tp) == 0:
				pass
			else:
				new_block = self.bb.generate_new_block(new_tp, self.prev_block_hash, cross_reference, self.block_num)
				self.bm.set_new_block(new_block.to_dict())
				self.prev_block_hash = self.bm.get_hash(new_block.to_dict())
				message_new_block = self.cm.get_message_text(MSG_NEW_BLOCK, json.dumps(new_block.to_dict(), sort_keys=True, ensure_ascii=False))
				self.cm.send_msg_to_all_peer(message_new_block)
				index = len(result_tp)
				self.tp.clear_my_transactions(index)
				if cross_reference:
					print("履歴交差部に入っているから情報をクリアします.")
					logging.debug("履歴交差部に入っているから情報をクリアします.")
					self.crm.clear_my_reference()
				tp2 = self.crm.time_stop_phase2()
				if tp2:
					print("Phase2_time:",tp2)
					time = str( "\n Turn" + str(self.crm.inc)  + " : Phase2: " + str(tp2) + " sec")
					print(time)
					self.Phase2_list.append(time)
					# with open( 'TIME/Pheae2.txt' , mode ='a') as f:
					# 	f.write(time)
					print("'Current Blockchain is ... ', self.bm.chain)"  + "省略中")
			print("'Current Blockchain is ... ', self.bm.chain) 省略中")
			self.Confirmed_block()
			#self.tp.create_transaction() #追加
			if self.crm.check_ref_block_num() == self.block_num:
				print("確定ブロック")
		print('Current prev_block_hash is ... ', self.prev_block_hash)
		print('Current prev_crossref_hash is ... ', self.crm.get_previous_cross_ref())
		self.flag_stop_block_build = False
		self.is_bb_running = False
		obj = self.bm.chain
		if self.filesave_flag == True:
			filename01 = "Current_Blockchain" + str(self.my_port) + ".json"
			self.save_json(filename01, obj)

		if self.refblock_count == REF_COUNT: ##規定回数を超えたら保存
			self.flag_stop_block_build = True #ブロック生成を停止
			print("ブロック生成を停止しました")
			if self.filesave_flag == True:
				if self.crm.phase1_list:
					filename02 = "Phase1_time" + str(self.my_port) + ".txt"
					print("ファイルかきこ")
					for i in self.crm.phase1_list:
						with open(filename02, mode='a') as f:
							f.write(str(i) + "\n")
					self.crm.phase1_list.clear()
					self.filesave_flag = False
			else :
				print("============= self.filesave_flag == False =============")

		else:
			x = REF_COUNT - self.refblock_count
			print(" =========== 規定履歴交差回数まで残り" + str(x) + "回 =========== ")
		self.bb_timer = threading.Timer(self.bb_interval, self.__generate_block_with_tp)
		self.bb_timer.start()

	def save_json(self, filename, obj):
		try:
			with open(filename, 'w', encoding = 'utf-8', newline = '\n') as fp:
				json.dump(obj, fp)
		
		except:
			logging.debug("ファイルを作成")
			with open(filename, 'w', encoding = 'utf-8', newline = '\n') as fp:
				json.dump(obj, fp)

	def Confirmed_block(self):#確定ブロックを更新
		print("Confirmed_block" + str(CONFIRMED_BLOCK) + "番目のブロック")
		print("確定ブロックの更新")
		chain_length = self.bm.get_my_chain_length()
		if CONFIRMED_BLOCK < chain_length:
			Block = self.bm.get_my_Confirmed_block()
			print("chain size is:", self.bm.get_my_chain_length())
			print("確定ブロック",Block)
			print("確定ブロックtype",type(Block))
			self.crm.renew_block_ref(Block)

		else:
			print("必要確定ブロック長さなし")
			pass

	def __handle_message(self, msg, is_core, peer=None):

		if peer != None:
			if msg[2] == MSG_REQUEST_FULL_CHAIN:
				print('Send our latest blockchain for reply to : ', peer)
				mychain = self.bm.get_my_blockchain()
				print(mychain)
				chain_data = pickle.dumps(mychain, 0).decode()
				new_message = self.cm.get_message_text(RSP_FULL_CHAIN, chain_data)
				self.cm.send_msg(peer,new_message)
		else:
			if msg[2] == MSG_NEW_TRANSACTION:
				#msg[4]の型を確認
				if isinstance(msg[4],dict):# dict
					print("for_client_msg[4]")
					# d = json.loads(msg[4]) # json.loads を使って dict に変換
					b = base64.b64decode(msg[4]['bin'].encode())	 # base64 を使ってバイナリから復元
					with open(dirname+"ZIP_busdata/accept_busdata/server_busdata.zip", "wb") as f:
						f.write(b)

					with zipfile.ZipFile(dirname+"ZIP_busdata/accept_busdata/server_busdata.zip") as zf:
						zf.extractall(dirname+"ZIP_busdata/accept_busdata")
					
					with open(dirname+"ZIP_busdata/accept_busdata/msg_pub.txt") as f:
						readdata = f.read().splitlines()
						print("read txt")
						new_transaction = json.loads(readdata[0])
				
				if isinstance(msg[4],str):# str
					print("for_server_msg[4]")
					print(type(msg[4]))
					new_transaction = json.loads(msg[4])
				
				else:
					print("object has no attribute")
					pass
				
				type(new_transaction)			

				current_transactions = self.tp.get_stored_transactions()
				if new_transaction in current_transactions:
					print("this is already pooled transaction:")
					return

				if not is_core:#from edge node
					ds = CheckDigitalSignature(new_transaction)
					CHECK_SIGNATURE = ds.get_flag()#ds.check_signature(new_transaction)
					if  CHECK_SIGNATURE == False:
						print('---------------------------------------')
						print ('DigitalSignature is False')
						print('---------------------------------------')
						return
					else:
						print('---------------------------------------')
						print ('DigitalSignature is True')
						print('---------------------------------------')

					self.tp.set_new_transaction(new_transaction)
					new_message = self.cm.get_message_text(MSG_NEW_TRANSACTION, json.dumps(new_transaction, sort_keys=True, ensure_ascii=False))
					self.cm.send_msg_to_all_peer(new_message)
				else:
					self.tp.set_new_transaction(new_transaction)

			elif msg[2] == MSG_NEW_BLOCK:

				if not is_core:
					print('block received from unknown')
					return

				# 新規ブロックを検証し、正当なものであればブロックチェーンに追加する
				new_block = json.loads(msg[4])
				print('new_block: ', new_block)
				if self.bm.is_valid_block(self.prev_block_hash, new_block):# is new block valid?
					# ブロック生成が行われていたら一旦停止してあげる（threadingなのでキレイに止まらない場合あり）
					if self.is_bb_running:
						self.flag_stop_block_build = True
					self.prev_block_hash = self.bm.get_hash(new_block)
					self.bm.set_new_block(new_block)
				else:
					#　ブロックとして不正ではないがVerifyにコケる場合は自分がorphanブロックを生成している
					#　可能性がある
					self.get_all_chains_for_resolve_conflict()

			elif msg[2] == RSP_FULL_CHAIN:

				if not is_core:
					print('blockchain received from unknown')
					return
				# ブロックチェーン送信要求に応じて返却されたブロックチェーンを検証し、有効なものか検証した上で
				# 自分の持つチェインと比較し優位な方を今後のブロックチェーンとして有効化する
				new_block_chain = pickle.loads(msg[4].encode('utf-8'))
				print(new_block_chain)
				result, pool_4_orphan_blocks = self.bm.resolve_conflicts(new_block_chain)
				print('blockchain received')
				if result is not None:
					self.prev_block_hash = result
					if len(pool_4_orphan_blocks) != 0:
						# orphanブロック群の中にあった未処理扱いになるTransactionをTransactionPoolに戻す
						new_transactions = self.bm.get_transactions_from_orphan_blocks(pool_4_orphan_blocks)
						for t in new_transactions:
							self.tp.set_new_transaction(t)
				else:
					print('Received blockchain is useless...')
				# self.main_window.set_chain(self.bm.chain)

			elif msg[2] == MSG_ENHANCED:
				# P2P Network を単なるトランスポートして使っているアプリケーションが独自拡張したメッセージはここで処理する。SimpleBitcoin としてはこの種別は使わない
				# self.mpmh.handle_message(msg[4])
				print("MSG_ENHANCED")

	def __get_myip(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		return s.getsockname()[0]
