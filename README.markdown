Penny auction bot
=================

Prelude
-------

This is a rather unorganised dump of the scripts I gathered together while writing a bot for a local penny auction site (www.smokoo.co.za). I honestly hate the idea of penny auctions but since I figured I could beat them decided to give it a shot. At the time there was nothing against any kind of bot in their T&C, so got to writing one.

After a fair amount of practice (and money) I started to win items using the bot. I ran the bot on a server for a while (much reduced ping time) which must have set off a whole bunch of alarms at their place - which then challenged me legally. Their claims and attitude towards the whole thing was shit, but as I was too busy to fight it legally and with the advice of a lawyer accepted a 90% discount (10% handling fee - eh?)

The most upsetting bit about the whole deal is I can calculate just how much money I earned them personally (well over $10k), as well as the fact that they didn't refund the other bidders in the auctions that suddenly became 'void'.

Strategy
--------

The strategy that finally worked well is quite simple. The advantage of a bot is in bidding at the last second or *sniping*. You can quite easily determine the auction would have ended if you had not bid. After a couple of snipes in quick succession you are quite likely one of the last two.

At this stage it is important to bid *earlier*. There are quite often a number of people waiting to snipe that bid after the time limit has exceeded. When this happens, even though my bot prevented the auction from ending, they land up with the timer counting down (and then I need to bid to prevent them from winning.) For this reason the bot has a percentage chance it will try 'kill', by bidding with 4-5s remaining, and hoping all the snipers miss.

Usage
-----

This isn't designed for script-kiddies or anything of the like. The source code is presented, you'll need to figure out the main parts as well as code a custom module for the auction site you use it on.

That said:
* 'ngrep' is used for tracking bids and current price
* The current runner uses moz-repl (firefox plugin) running on port 4242. A runner for chrome using 'chrome remote shell' is also included.

The actual bot has a shorthand syntax for bidding on auctions
python bot.py *auction-id* [,*auction-id* ...] [m*mode*] [f*initial-bid*] [-*friendly-username*] [=*max-bids*]
