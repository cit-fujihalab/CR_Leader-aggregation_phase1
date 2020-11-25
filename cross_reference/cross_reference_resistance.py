import time
import socket, threading, json
import os
from time import sleep

# from p2p.owner_node_list import OwnerCoreNodeList


class CrossReferenceResistance:
#異常時にここに来る.
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

	#if self.Accept_list > 1: #current_accept_list
			#1以上なら確認する。

	def Failure_resistance_disconnection(self):#耐停止故障
        
		#受信できないドメインに再送（相手が悪い）

	#def Failure_resistance_disconnectionAtoB(self):#耐停止故障
		#自分が送信できない（自分が悪い?）