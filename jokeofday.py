import requests
import base64
from github import Github
import os

my_secret_key = os.environ['MY_SECRET_KEY']

# Fetch a new joke from JokeAPI
response = requests.get("https://v2.jokeapi.dev/joke/Programming?format=json")
joke_data = response.json()
joke = joke_data['setup'] + " " + joke_data['delivery']

# Fetch the current README.md file from your GitHub repository
g = Github(my_secret_key)
repo = g.get_repo("tsmith4014/tsmith4014")
contents = repo.get_contents("README.md")
readme_data = base64.b64decode(contents.content).decode("utf-8")

# Replace the joke in the README.md file
new_readme_data = readme_data.replace("⚡ AI Joke of the Day: 🤖 YOUR_OLD_JOKE", f"⚡ AI Joke of the Day: 🤖 {joke}")

# Update the README.md file in your GitHub repository
repo.update_file(contents.path, "Updated Joke of the Day", new_readme_data, contents.sha)
