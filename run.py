import argparse
import postbot


parser = argparse.ArgumentParser()

parser.add_argument('-g', type=int, 
	help="Group number or id.")
parser.add_argument('-r', type=int, default=0,
	help="How many days to make posts.")
parser.add_argument('-d', type=int, default=0, 
	help="From which day bot must start posting.")
parser.add_argument('-u', type=bool, default=False, 
	help="Update mediafiles.")
parser.add_argument('--up', type=str, default='', 
	help="Posting while didn't met photo id.")
parser.add_argument('--ua', type=str, default='', 
	help="Posting while didn't met audio id.")
parser.add_argument('-m', type=int, default=0, 
	help="This month + this value.")

params = vars(parser.parse_args())

bot = postbot.PostBot(*list(params.values()))
bot.run()