import json
from playwright.sync_api import sync_playwright


def fetch_raw_jobsdb_json(max_pages=1):

    base_url = "https://th.jobsdb.com/th/jobs"
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # ดักจับ response
        def handle_response(response):
            try:
                if "search" in response.url and response.request.resource_type == "xhr":
                    if "application/json" in response.headers.get("content-type", ""):
                        data = response.json()
                        all_data.append(data)
            except:
                pass

        page.on("response", handle_response)

        for page_no in range(1, max_pages + 1):
            print(f"🔍 Visiting page {page_no}")
            page.goto(f"{base_url}?page={page_no}", wait_until="networkidle")

        browser.close()

    # print JSON ทั้งหมด
    print("\n========== RAW JSON ==========\n")
    print(json.dumps(all_data, indent=2, ensure_ascii=False))

    # save file
    with open("jobsdb_raw_output.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print("\n✅ Saved to jobsdb_raw_output.json")

    return all_data


if __name__ == "__main__":
    fetch_raw_jobsdb_json(max_pages=1)
