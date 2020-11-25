import time
import socket, threading, json
import copy
import pickle
import base64
import zipfile
import os
from time import sleep
import random
import hashlib

from signature.generate_sigunature import DigitalSignature
from signature.generate_sigunature import CheckDigitalSignature
from p2p.connection_manager_4owner import ConnectionManager4Owner
from p2p.my_protocol_message_handler import MyProtocolMessageHandler
# from p2p.owner_node_list import OwnerCoreNodeList



class CrossReferenceManager:

	def __init__(self):
		self.gs = DigitalSignature()
		self.cross_reference = []
		self.previous_cross_sig = []
		self.reference = []
		self.lock = threading.Lock()
		self.timer1 = 0
		self.flag1 = False
		self.timer2 = 0
		self.flag2 = False
		self.timer3 = 0
		self.flag3 = False
		self.cross_reference_flag = False
		self.inc = 0
		self.ref_block_num = 999


	def set_new_cross_reference(self, cross):
		with self.lock:
			self.reference.append(cross)
			print("======= set_new_cross_ref =======")

	def clear_my_reference(self, index):
		with self.lock:
			new_reference = self.reference
			del new_reference[0:index]
			print('reference is now refreshed ... ', new_reference)
			self.reference = new_reference
		
	def add_cross_reference(self, cross): #reference部形成リスト
		self.cross_reference.append(cross)

	def clear_cross_reference(self):
		self.cross_reference.clear()
		print(" ======== reference部形成リストclear ======== ",self.cross_reference)
	
	def get_reference_pool(self):
		if len(self.reference) == 1:
			return self.reference[0]
		else:
			print("Currently, it seems cross pool is empty...")
			return []
		
	def hysteresis_sig(self):
		Current_C = self.cross_reference
		print(Current_C)
		Current_C.append(self.get_previous_cross_ref())
		print(Current_C)
		msg = json.dumps(Current_C)
		msg_pub = self.gs.add_public_key(msg)
		self.store_previous_cross_ref(msg_pub)
		return msg_pub

	def store_previous_cross_ref(self, msg_sig):
		
		self.previous_cross_sig.clear()
		
		print("クリア後", len(self.previous_cross_sig))

		msg_hash = self._get_hash_sha256(msg_sig)
		print("store_previous_crossref_hash")
		d = {
			'previous_crossref_hash' : msg_hash
		}
		self.previous_cross_sig.append(d)
		# r = self.previous_cross_sig[0] # .get('previous_crossref_hash')
		print("======= renew prev_crossref_hash  ... ======= ",self.previous_cross_sig)

		if len(self.previous_cross_sig) == 1:
			print("store_previous_cross_ref　＝　正常")
		
		elif len(self.previous_cross_sig) > 1 :
			print("~~~~~~~~~~~~異常~~~~~~~~~~~~~~")

		else :
			print("~~~~~~特大異常~~~~~~~")
			pass


	def _get_hash_sha256(self, message):
		return hashlib.sha256(message.encode()).hexdigest()

	def get_previous_cross_ref(self):
		print("get_previous_cross_sig")
		if len(self.previous_cross_sig) == 1:
			msg_sig = self.previous_cross_sig[0]
			return msg_sig
		else:
			print("Currently, it seems previous_cross_sig is empty or ERR...")
			d = {
				'previous_crossref_hash' : {}
			}
			return d

	def time_start_phase1(self):
		self.flag1 = True
		self.timer1 =  time.perf_counter()
	
	def time_stop_phase1(self):
		if self.flag1:
			t = time.perf_counter()- self.timer1
			self.flag1 = False
			return t
		else:
			return None

	def time_start_phase2(self):
		self.flag2 = True
		self.timer2 =  time.perf_counter()
	
	def time_stop_phase2(self):
		if self.flag2:
			t = time.perf_counter()- self.timer2
			self.flag2 = False
			return t
		else:
			return None


	def ref_block_number(self,num):
		self.ref_block_num = num + 2
		print("##########################",self.ref_block_num)

	def check_ref_block_num(self):
		return self.ref_block_num

	def block_cheek(self):
		self.cross_reference_flag = False
