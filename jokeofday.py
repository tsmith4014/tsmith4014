import requests
import base64
from github import Github
import os
import re

# Your GitHub Personal Access Token
my_secret_key = os.environ['MY_SECRET_KEY']

# Fetch a new joke from JokeAPI
response = requests.get("https://v2.jokeapi.dev/joke/Programming?format=json")
joke_data = response.json()
print(f"Debug: Received joke data: {joke_data}")  # Debug print

# Format the joke based on its type
if joke_data['type'] == 'single':
    joke = joke_data['joke']
else:
    joke = f"{joke_data['setup']} {joke_data['delivery']}"

print(f"Formatted joke: {joke}")  # Debug print

# Fetch the current README.md file from your GitHub repository
g = Github(my_secret_key)
repo = g.get_repo("tsmith4014/tsmith4014")
contents = repo.get_contents("README.md")
readme_data = base64.b64decode(contents.content).decode("utf-8")

# Use regex to find and replace the joke in the README.md file
pattern = r"(⚡ AI Joke of the Day: 🤖 ).*?( 🤖)"
replacement = f"⚡ AI Joke of the Day: 🤖 {joke} 🤖"
new_readme_data = re.sub(pattern, replacement, readme_data, flags=re.DOTALL)

# pattern = r"(⚡ AI Joke of the Day: 🤖 ).*( 🤖)"
# replacement = f"⚡ AI Joke of the Day: 🤖 {joke} 🤖"
# new_readme_data = re.sub(pattern, replacement, readme_data)

print(f"New README data: {new_readme_data}")  # Debug print

# Update the README.md file in your GitHub repository
update_response = repo.update_file(contents.path, "Updated Joke of the Day", new_readme_data, contents.sha)
print(f"Update response: {update_response}")  # Debug print


pattern = r"(⚡ AI Joke of the Day: 🤖 ).*?( 🤖)"
replacement = f"⚡ AI Joke of the Day: 🤖 {joke} 🤖"
new_readme_data = re.sub(pattern, replacement, readme_data, flags=re.DOTALL)



# import requests
# import base64
# from github import Github
# import os
# import re

# # Your GitHub Personal Access Token
# my_secret_key = os.environ['MY_SECRET_KEY']

# # Fetch a new joke from JokeAPI
# response = requests.get("https://v2.jokeapi.dev/joke/Programming?format=json")
# joke_data = response.json()

# # Format the joke based on its type
# if joke_data['type'] == 'single':
#     joke = joke_data['joke']
# else:
#     joke = f"{joke_data['setup']} {joke_data['delivery']}"

# # Fetch the current README.md file from your GitHub repository
# g = Github(my_secret_key)
# repo = g.get_repo("tsmith4014/tsmith4014")
# contents = repo.get_contents("README.md")
# readme_data = base64.b64decode(contents.content).decode("utf-8")

# # Use regex to find and replace the joke in the README.md file
# pattern = r"(⚡ AI Joke of the Day: 🤖 ).*( 🤖)"
# replacement = f"⚡ AI Joke of the Day: 🤖 {joke} 🤖"
# new_readme_data = re.sub(pattern, replacement, readme_data)

# # Update the README.md file in your GitHub repository
# repo.update_file(contents.path, "Updated Joke of the Day", new_readme_data, contents.sha)


# import requests
# import base64
# from github import Github
# import os

# my_secret_key = os.environ['MY_SECRET_KEY']

# # Fetch a new joke from JokeAPI
# response = requests.get("https://v2.jokeapi.dev/joke/Programming?format=json")
# joke_data = response.json()

# # Format the joke based on its type
# if joke_data['type'] == 'single':
#     joke = joke_data['joke']
# else:  # Assuming the only other type is 'twopart'
#     joke = f"{joke_data['setup']} {joke_data['delivery']}"

# print(f"Debug: Received joke data: {joke_data}")
# print(f"Formatted joke: {joke}")

# # Fetch the current README.md file from your GitHub repository
# g = Github(my_secret_key)
# repo = g.get_repo("tsmith4014/tsmith4014")
# contents = repo.get_contents("README.md")
# readme_data = base64.b64decode(contents.content).decode("utf-8")

# # Find and replace the joke in the README.md file
# readme_lines = readme_data.split('\n')
# for i, line in enumerate(readme_lines):
#     if "⚡ AI Joke of the Day: 🤖" in line:
#         start = line.find("🤖") + len("🤖")  # Find the first 🤖 and move past it
#         end = line.rfind("🤖")  # Find the last 🤖
#         if start != -1 and end != -1 and start != end:
#             new_line = line[:start] + " " + joke + " " + line[end:]
#             readme_lines[i] = new_line
#             break
# else:
#     print("Joke string not found in README.md. No update performed.")


# new_readme_data = '\n'.join(readme_lines)

# # Update the README.md file in your GitHub repository
# repo.update_file(contents.path, "Updated Joke of the Day", new_readme_data, contents.sha)
