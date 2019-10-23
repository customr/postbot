import argparse
import core as pb


parser = argparse.ArgumentParser()

parser.add_argument('-g', type=int, 
	help="Group number or id.")
parser.add_argument('-r', type=int, default=0,
	help="How many days to make posts.")
parser.add_argument('-d', type=int, default=0, 
	help="From which day bot must start posting.")
parser.add_argument('-u', type=bool, default=False, 
	help="Update mediafiles.")

params = vars(parser.parse_args())

client = pb.Client(params['g'], params['u'])
bot = pb.Post(client, params['r'], params['d'])

bot.run()