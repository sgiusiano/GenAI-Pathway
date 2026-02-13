import os
from dotenv import find_dotenv, load_dotenv

# find .env automagically by walking up directories until it's found, then
# load up the .env entries as environment variables
load_dotenv(find_dotenv())

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY", "")
