import json

# Read Gmail data
with open("mock_data/gmail.json", "r") as f:
    gmail_data = json.load(f)

# Read Notion data
with open("mock_data/notion.json", "r") as f:
    notion_data = json.load(f)

# Read Jira data
with open("mock_data/jira.json", "r") as f:
    jira_data = json.load(f)

# Print them
print("📧 GMAIL:")
print(gmail_data)
print("\n📓 NOTION:")
print(notion_data)
print("\n🎫 JIRA:")
print(jira_data)