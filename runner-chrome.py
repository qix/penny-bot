import chrome_remote_shell, re, time

class runner:
	def __init__(self, port, site):
		self.shell=chrome_remote_shell.open(port=port)
		self.site = site
		tabs = self.shell.request('DevToolsService', command='list_tabs')['data']
		self.tabs = []
		for (id, addr) in tabs:
			if re.match('^http://(www\.)?'+site+'.*$', addr):
				self.tabs.append(id)

	def run(self, js):
		for tab in self.tabs:
			self.shell.request('V8Debugger', destination=tab, command='evaluate_javascript', data=js)
	def runonce(self, js):
		for tab in self.tabs:
			self.shell.request('V8Debugger', destination=tab, command='evaluate_javascript', data=js)
			break
	
	def refresh(self):
		self.run("window.location='http://www."+self.site+"/';");
		# Let it reload and kill off alerts
		time.sleep(0.5)
		self.run("window.alert = alert = function(){};");


if __name__ == "__main__":

	r = runner(9222, 'smokoo.co.za')
	r.refresh()
	r.run('alert("rawr");')
