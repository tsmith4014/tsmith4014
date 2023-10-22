import requests
import base64
from github import Github
import os
import random  # Import the random module

my_secret_key = os.environ['MY_SECRET_KEY']
print(f"Debug: MY_SECRET_KEY = {my_secret_key}")

def fetch_suggestion():
    response = requests.get("https://www.boredapi.com/api/activity")
    suggestion_data = response.json()

    activity = suggestion_data['activity']
    activity_type = suggestion_data['type']
    participants = suggestion_data['participants']
    price = suggestion_data['price']
    accessibility = suggestion_data['accessibility']

    suggestion_parts = []  # List to hold different parts of the suggestion

    # Randomly pick a phrase based on activity_type
    activity_type_phrases = {
        'education': ["🎓 Let's work on some brainpower", "📚 Time to hit the books", "🤓 Geek out"],
        'recreational': ["🏖️ Time to relax", "🎉 Let's have some fun", "🎮 Game on"],
        'social': ["👥 Be social", "🗨️ Let's mingle", "🤝 Time to network"],
        'charity': ["❤️ Make the world a better place", "🤲 Time to give back", "🌍 Be a hero"],
        'cooking': ["👨‍🍳 Masterchef time", "🍳 Let's cook up a storm", "🍲 Soup's on"],
        'music': ["🎵 Feel the rhythm", "🎶 Let's make some noise", "🎸 Rock on"]
    }

    if activity_type in activity_type_phrases:
        suggestion_parts.append(random.choice(activity_type_phrases[activity_type]))

    # Randomly pick a phrase based on participants
    if participants == 0:
        suggestion_parts.append("🚶‍♂️ Solo activity")
    elif participants == 1:
        suggestion_parts.append("👤 Grab a friend")
    elif participants == 2:
        suggestion_parts.append("👫 Grab a couple friends")
    else:
        suggestion_parts.append("👨‍👩‍👦‍👦 Gather the squad")

    # Randomly pick a phrase based on price
    if price == 0:
        suggestion_parts.append("💰 It's free!")
    elif 0 < price < 0.2:
        suggestion_parts.append("💵 Pocket change needed")
    elif 0.2 <= price < 0.5:
        suggestion_parts.append("💸 Break open your piggy bank")
    else:
        suggestion_parts.append("💳 Time to splurge!")

    # Randomly pick a phrase based on accessibility
    if accessibility <= 0.2:
        suggestion_parts.append("👌 Super easy to do")

    suggestion_parts.append(f"🎉 {activity}")

    suggestion = ' | '.join(suggestion_parts)
    print(suggestion)
    return suggestion

if __name__ == "__main__":
    suggestion = fetch_suggestion()

    g = Github(my_secret_key)
    repo = g.get_repo("tsmith4014/tsmith4014")
    contents = repo.get_contents("README.md")
    readme_data = base64.b64decode(contents.content).decode("utf-8")

    readme_lines = readme_data.split('\n')
    for i, line in enumerate(readme_lines):
        if "⚡ AI Suggestion of the Day: 🤖" in line:
            start = line.find("🤖") + len("🤖")
            end = line.rfind("🤖")
            if start != -1 and end != -1 and start != end:
                new_line = line[:start] + " " + suggestion + " " + line[end:]
                readme_lines[i] = new_line
                break
    else:
        print("Suggestion string not found in README.md. No update performed.")

    new_readme_data = '\n'.join(readme_lines)

    repo.update_file(contents.path, "Updated Suggestion of the Day", new_readme_data, contents.sha)



# import requests
# import base64
# from github import Github
# import os

# my_secret_key = os.environ['MY_SECRET_KEY']
# print(f"Debug: MY_SECRET_KEY = {my_secret_key}")

# def fetch_suggestion():
#     response = requests.get("https://www.boredapi.com/api/activity")
#     suggestion_data = response.json()

#     activity = suggestion_data['activity']
#     activity_type = suggestion_data['type']
#     participants = suggestion_data['participants']
#     price = suggestion_data['price']
#     accessibility = suggestion_data['accessibility']

#     suggestion_parts = []  # List to hold different parts of the suggestion

#     if activity_type == 'education':
#         suggestion_parts.append("🎓 Let's work on some brainpower")
#     if activity_type == 'recreational':
#         suggestion_parts.append("🏖️ Time to relax")
#     if activity_type == 'social':
#         suggestion_parts.append("👥 Be social")
#     if activity_type == 'charity':
#         suggestion_parts.append("❤️ Make the world a better place")
#     if activity_type == 'cooking':
#         suggestion_parts.append("👨‍🍳 Masterchef time")
#     if activity_type == 'music':
#         suggestion_parts.append("🎵 Feel the rhythm")

#     if participants > 1:
#         suggestion_parts.append("👫 Grab a friend")

#     if price >= 0.2:
#         suggestion_parts.append("💸 Break open your piggy bank")

#     if accessibility <= 0.2:
#         suggestion_parts.append("👌 Super easy to do")

#     suggestion_parts.append(f"🎉 {activity}")

#     suggestion = ' | '.join(suggestion_parts)
#     print(suggestion)
#     return suggestion

# if __name__ == "__main__":
#     suggestion = fetch_suggestion()

#     g = Github(my_secret_key)
#     repo = g.get_repo("tsmith4014/tsmith4014")
#     contents = repo.get_contents("README.md")
#     readme_data = base64.b64decode(contents.content).decode("utf-8")

#     readme_lines = readme_data.split('\n')
#     for i, line in enumerate(readme_lines):
#         if "⚡ AI Suggestion of the Day: 🤖" in line:
#             start = line.find("🤖") + len("🤖")
#             end = line.rfind("🤖")
#             if start != -1 and end != -1 and start != end:
#                 new_line = line[:start] + " " + suggestion + " " + line[end:]
#                 readme_lines[i] = new_line
#                 break
#     else:
#         print("Suggestion string not found in README.md. No update performed.")

#     new_readme_data = '\n'.join(readme_lines)

#     repo.update_file(contents.path, "Updated Suggestion of the Day", new_readme_data, contents.sha)