import json
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config

bot = Bot(
	token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
		parse_mode=ParseMode.MARKDOWN_V2, 
		link_preview_is_disabled=True
	)
)

def io_json(variable:str, mode:str="r", data:dict|None=None) -> dict | None:

	"""
	variable: name of variable,

	mode: "r" - read, "w" - write

	data: data to be writed
	"""

	if mode == "w":

		with open(file=f"data/{variable}.json", mode=mode) as outfile:

			json.dump(data, outfile)
			return True

	elif mode == "r":

		with open(file=f"data/{variable}.json", mode=mode) as outfile:

			try:
				data = json.load(outfile)

			except json.decoder.JSONDecodeError:
				print("json file is empty")

		if data != None and data != {}:

			try:
				data_w_corr_data_type = {int(key):int(val) for key, val in data.items() if val != None}
			
			except: 
				data_w_corr_data_type = {int(key):val for key, val in data.items() if val != None}
			
			finally:
				return data_w_corr_data_type
		else:
			return {}

	else:
		raise Exception("unsupported mode type")