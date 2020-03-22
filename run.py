import argparse
import postbot


parser = argparse.ArgumentParser()

parser.add_argument('-g', type=int, 
	help="Group number or id.")
parser.add_argument('-r', type=int,
	help="How many days to make posts.")
parser.add_argument('-d', type=int,
	help="From which day bot must start posting.")
parser.add_argument('-u', type=bool, default=False, 
	help="Update mediafiles.")
parser.add_argument('-m', type=int, default=0, #zero means this month
	help="Post for this month.")
parser.add_argument('-y', type=int, default=0, #zero means this year
	help="Post for this year.")

params = vars(parser.parse_args())

bot = postbot.PostBot(*list(params.values()))
bot.run()