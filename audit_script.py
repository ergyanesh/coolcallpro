import os
import re
from bs4 import BeautifulSoup

def get_html_files(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))
    return html_files

def calculate_flesch_reading_ease(text):
    if not text:
        return 0
    sentences = len(re.split(r'[.!?]+', text))
    words = len(re.findall(r'\w+', text))
    syllables = 0
    for word in re.findall(r'\w+', text):
        syllables += len(re.findall(r'[aeiouy]+', word.lower()))
    
    if words == 0 or sentences == 0:
        return 0
    
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    return score

def audit_files(directory):
    html_files = get_html_files(directory)
    results = []
    
    for file_path in html_files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            soup = BeautifulSoup(content, "html.parser")
            
            # Meta Tags
            title = soup.title.string if soup.title else None
            description = soup.find("meta", attrs={"name": "description"})
            description = description["content"] if description else None
            
            # Links
            links = soup.find_all("a", href=True)
            broken_links = []
            for link in links:
                href = link["href"]
                if not href.startswith(("http", "mailto", "tel", "#")):
                    # Internal link
                    target_path = os.path.normpath(os.path.join(os.path.dirname(file_path), href))
                    # Handle anchor links in files
                    target_file = target_path.split("#")[0]
                    if not os.path.exists(target_file):
                        broken_links.append(href)
            
            # Schema
            schemas = soup.find_all("script", type="application/ld+json")
            
            # Readability
            # Extract text from main content if possible, else body
            main = soup.find("main") or soup.find("body")
            text = main.get_text(separator=" ", strip=True) if main else ""
            readability_score = calculate_flesch_reading_ease(text)
            
            results.append({
                "file": os.path.relpath(file_path, directory),
                "title": title,
                "description": description,
                "broken_links": broken_links,
                "schema_count": len(schemas),
                "readability_score": readability_score
            })
    
    return results

if __name__ == "__main__":
    project_dir = r"c:/Users/gyane/Desktop/Antigravity Projects/WIP - 12 March 2026 - CCP - CloudFlare"
    audit_results = audit_files(project_dir)
    
    # Analyze and Output
    missing_meta = 0
    total_broken_links = 0
    total_schema = 0
    low_readability = 0
    
    print("--- Detailed Audit Report ---")
    for res in audit_results:
        # Check for missing meta
        if not res["title"] or not res["description"]:
            missing_meta += 1
            # print(f"Missing Meta: {res['file']}")
            
        # Check broken links
        if res["broken_links"]:
            total_broken_links += len(res["broken_links"])
            print(f"Broken Links in {res['file']}: {res['broken_links']}")
            
        # Schema
        total_schema += res["schema_count"]
        
        # Readability
        if res["readability_score"] < 60: # 60-70 is standard 8th/9th grade
            low_readability += 1
            # print(f"Low Readability ({res['readability_score']:.1f}): {res['file']}")

    print("\n--- Summary ---")
    print(f"Total HTML Files: {len(audit_results)}")
    print(f"Files Missing Meta Tags: {missing_meta} ({missing_meta/len(audit_results)*100:.1f}%)")
    print(f"Total Broken Internal Links: {total_broken_links}")
    print(f"Total Schema LD+JSON Blocks: {total_schema}")
    print(f"Files with Low Readability (<60): {low_readability} ({low_readability/len(audit_results)*100:.1f}%)")
