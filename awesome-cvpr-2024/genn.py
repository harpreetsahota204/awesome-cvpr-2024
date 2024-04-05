import csv
import argparse
from collections import defaultdict
from typing import Any, Dict, List

def load_data_from_csv(csv_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load data from a CSV file into a dictionary.

    :param csv_path: Path to the CSV file.
    :return: A dictionary with topics as keys and list of entries as values.
    """
    data = defaultdict(list)
    with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:  # Adjusted encoding to 'utf-8-sig'
        reader = csv.DictReader(csvfile)
        print(f"Detected column names: {reader.fieldnames}")  # Debug print statement
        
        # Ensure 'topic' column is correctly identified after adjusting for BOM
        if 'topic' not in reader.fieldnames:
            raise ValueError("CSV must contain a 'topic' column.")
        
        for row in reader:
            data[row['topic']].append(row)  # Directly using 'topic' as key
    return data


def collect_manual_data(entries: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """
    Collect manual data entries into a dictionary.

    Adjusts for entries format to include summaries, potentially using a different delimiter
    to safely include commas within summaries.

    :param entries: List of comma-separated string entries.
    :return: A dictionary with topics as keys and list of entries as values.
    """
    data = defaultdict(list)
    for entry in entries:
        try:
            # Assuming a semicolon is used as a delimiter for entries
            parts = entry.split(';')
            # Ensure we have exactly 6 parts: topic, title, authors, code, arxiv_page, project_page, and summary
            if len(parts) == 7:
                topic, title, authors, code, arxiv_page, project_page, summary = parts
                data[topic].append({
                    'title': title.strip(),
                    'authors': authors.strip(),
                    'code': code.strip(),
                    'arxiv page': arxiv_page.strip(),
                    'project page': project_page.strip(),
                    'summary': summary.strip()
                })
            else:
                print(f"Skipping malformed entry: {entry}")
        except ValueError as e:
            print(f"Error processing entry: {entry}. Error: {e}")
    return data

def generate_code_badge(code_url: str) -> str:
    """
    Generate a markdown badge for GitHub repositories, handling potential trailing slash in the URL.
    
    :param code_url: URL of the code repository.
    :return: Markdown formatted badge.
    """
    if 'github.com' in code_url:
        # Remove trailing slash if present and extract the repository name
        repo_name = code_url.rstrip('/').replace('https://github.com/', '')
        return f"[![GitHub](https://img.shields.io/github/stars/{repo_name}?style=social)]({code_url})"
    return f""

def generate_arxiv_badge(arxiv_url: str) -> str:
    """
    Generate a markdown badge for arXiv or ar5iv links.
    
    :param arxiv_url: URL of the arXiv or ar5iv page.
    :return: Markdown formatted badge.
    """
    if 'arxiv.org' in arxiv_url or 'ar5iv.labs' in arxiv_url:
        arxiv_id = arxiv_url.split('/')[-1]
        return f"[![arXiv](https://img.shields.io/badge/arXiv-{arxiv_id}-b31b1b.svg?style=for-the-badge)]({arxiv_url})"
    return ""


def generate_markdown_tables(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
    """
    Generate Markdown tables from the data dictionary, combining the code and arXiv columns,
    and hyperlinking the title to the project page if available.

    :param data: Data dictionary with topics as keys and list of entries as values.
    :return: A dictionary of Markdown tables by topic.
    """
    tables = defaultdict(str)
    for topic, entries in data.items():
        # Adjusted header for center alignment and removed Project Page column
        header = "|:-------------------|:-------------------|:-------------------:|:-------------------|\n"
        table = "| Title | Authors | Code / arXiv Page | Summary |\n" + header
        for entry in entries:
            code_badge = generate_code_badge(entry['code'])
            arxiv_badge = generate_arxiv_badge(entry.get('arxiv page', ''))
            summary = entry.get('summary', '')

            # Combine code and arXiv badges into a single column
            code_arxiv_combined = f"{code_badge} {arxiv_badge}".strip()

            # Hyperlink the title to the project page if available
            title = entry['title']
            if entry.get('project page'):
                title = f"[{title}]({entry['project page']})"

            table += f"| {title} | {entry['authors']} | {code_arxiv_combined} | {summary} |\n"
        tables[topic] = table
    return tables

def update_readme_with_tables(tables: Dict[str, str], readme_path: str):
    """
    Update the README file by inserting Markdown tables at a specific token location.

    :param tables: Dictionary of Markdown tables by topic.
    :param readme_path: Path to the README file.
    """
    token = "<!-- TABLES_START -->"
    new_content = ""
    for topic, table in tables.items():
        new_content += f"\n## {topic}\n{table}\n"

    # Read the existing README content
    with open(readme_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content at the token and replace anything after it with the new tables
    if token in content:
        parts = content.split(token, 1)  # Only split at the first occurrence of the token
        updated_content = parts[0] + token + new_content
    else:
        print(f"Token '{token}' not found in {readme_path}. Appending tables at the end.")
        updated_content = content + "\n" + token + new_content

    # Write the updated content back to the README
    with open(readme_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

    print(f"README has been updated with new tables at {readme_path}")

def main():
    """
    Main function to orchestrate the script's logic based on command line arguments.
    """
    parser = argparse.ArgumentParser(description="Generate Markdown tables from CSV or manual input and write to a file.")
    parser.add_argument('--csv', type=str, help="Path to the CSV file.")
    parser.add_argument('--entries', nargs='+', help="Manual entries in the format: topic,title,authors,code,arxiv_page,project_page,summary")
    parser.add_argument('--output', type=str, required=True, help="Path to the output Markdown file.")
    args = parser.parse_args()

    if args.csv:
        data = load_data_from_csv(args.csv)
    elif args.entries:
        data = collect_manual_data(args.entries)
    else:
        raise ValueError("No input provided. Use --csv for CSV input or --entries for manual input.")

    tables = generate_markdown_tables(data)
    update_readme_with_tables(tables, args.output)

    print(f"Markdown tables have been written to {args.output}")

if __name__ == "__main__":
    main()
