import os
class sound:
	def play(self,filename, volume=10):
		pass # Sounds disabled
		#os.spawnv(os.P_NOWAIT,'/usr/bin/mplayer',('mplayer','-nolirc','-really-quiet','-af','volume='+str(volume)+'.1:0','sound/'+filename))

	def start(self): self.play('start.wav', 10)
	def bid(self): self.play('bid.wav', 20)
	def win(self): self.play('win.mp3', 3)
	def lose(self): self.play('lose.mp3', 3)
	def nobids(self): self.play('lose.mp3', 3)
	def over(self): self.play('lose.mp3', 3)
