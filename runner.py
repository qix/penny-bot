import subprocess, re, time

class runner:
	def __init__(self, port, site):
		self.shell = subprocess.Popen(('nc', 'localhost', '4242'), stdin=subprocess.PIPE, stdout=file('repl-out.txt','w'))
		self.site = site

	def run(self, js):
		self.runonce(js)

	def runonce(self, js):
		self.shell.stdin.write(js+"\n")

	def refresh(self):
		self.run("window.location='http://www."+self.site+"/';");


if __name__ == "__main__":
	r = runner(9222, 'smokoo.co.za')
	r.run('alert("rawr");')
