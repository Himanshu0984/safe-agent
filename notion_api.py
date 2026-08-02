import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))


def search_notion_pages():
    """Fetch all pages the integration has access to."""
    results = notion.search(filter={"property": "object", "value": "page"})
    pages = []
    for page in results.get("results", []):
        # Extract page title
        title = "Untitled"
        props = page.get("properties", {})
        for prop in props.values():
            if prop.get("type") == "title" and prop.get("title"):
                title = prop["title"][0]["plain_text"]
                break
        pages.append({"id": page["id"], "title": title})
    return pages


def get_page_content(page_id):
    """Get all text content from a Notion page."""
    blocks = notion.blocks.children.list(block_id=page_id)
    content = []
    for block in blocks.get("results", []):
        block_type = block.get("type")
        block_data = block.get(block_type, {})
        rich_text = block_data.get("rich_text", [])
        text = "".join([t.get("plain_text", "") for t in rich_text])
        if text.strip():
            content.append(text)
    return "\n".join(content)


def fetch_notion_data():
    """Fetch all accessible pages as structured data."""
    pages = search_notion_pages()
    data = []
    for page in pages:
        content = get_page_content(page["id"])
        data.append({
            "page": page["title"],
            "content": content
        })
    return data


# ===== TEST =====
if __name__ == "__main__":
    print("🔍 Searching Notion pages...")
    data = fetch_notion_data()
    print(f"\n✅ Found {len(data)} pages:\n")
    for item in data:
        print(f"📄 {item['page']}")
        print(f"   {item['content'][:200]}...")
        print()