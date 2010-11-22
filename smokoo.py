import os,re,time,select,fcntl,datetime,random,sys,cgi,BaseHTTPServer,random
from subprocess import PIPE,Popen

class smokoo:
	def __init__(self,interface='eth0'):
		# Start monitoring
		self.ng = os.popen('sudo ngrep -d '+interface) #+' port 80')
		self.lastBid = {}

		fd = self.ng.fileno()
		fl = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

	def read(self):
		if select.select([self.ng], [], [], 0) == ([self.ng], [], []):
			r = self.ng.read()
			r = r.replace("\n", '').replace("\t", '').replace(' ','')
			return r
		else: return None

	def latest(self):
		r = self.read()
		if r is None: return {}

		try:
			results = {}
			for groups in re.findall('\\^!%[0-9]*\\|([0-9.]+)\\|', r):
				(left,) = groups
				results[item] = float(left)
			return results
		except:
			return {}
