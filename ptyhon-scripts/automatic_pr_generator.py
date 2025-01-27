import os
import re
import requests
from git import Repo
from git.exc import InvalidGitRepositoryError
import openai
import argparse

"""
Automatic PR Generator
---------------------
This script generates a pull request description based on the current branch's changes
and associated JIRA ticket information.

Usage:
    From the root of the repository (i.e you are working in a change in package-data-sources, in the branch task/FOUR-1234, 
    make sure you are in that package-data-sources folder in your current working branch):
    
    python path_to_script/automatic_pr_generator.py [-p REPO_PATH] [-b BASE_BRANCH]

Arguments:
    -p, --repo-path    Path to the Git repository (default: current directory)
    -b, --base-branch  Base branch to compare changes against (e.g., 'develop', 'main', 'epic/FOUR-1234')
                       This is going to be used also to set the base branch for the PR.
                       This argument is required.

Example:
    # Run from your feature branch, comparing against the epic branch epic/FOUR-1234:
    python path_to_script/automatic_pr_generator.py -b epic/FOUR-1234

    # Run from a specific repository path:
    python path_to_script/automatic_pr_generator.py -p /path/to/repo -b main

Notes:
    - The script expects your branch name to contain a JIRA ticket ID (e.g., FOUR-123)
    - Make sure you have the required API tokens configured in the script
    - The script will fetch the latest changes from remote before generating the PR
"""

# Configuration
JIRA_BASE_URL = "https://processmaker.atlassian.net"
JIRA_USERNAME = "agustin.busso@processmaker.com"
JIRA_API_TOKEN = "ATAT..."
GITHUB_TOKEN = "ghp_..."
OPENAI_API_KEY = "sk-..."

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate PR description from Git changes')
    parser.add_argument('--repo-path', '-p', 
                       default=os.getcwd(),
                       help='Path to the Git repository')
    parser.add_argument('--base-branch', '-b',
                       help='Base branch to compare changes against')
    return parser.parse_args()

def get_current_branch(repo_path):
    """Gets the name of the current branch."""
    try:
        repo = Repo(repo_path)
        return repo.active_branch.name
    except InvalidGitRepositoryError:
        print("❌ Error: Current directory is not a Git repository.")
        print("Please run this script from within a Git repository.")
        exit(1)

def get_ticket_info(ticket_id):
    """Queries the JIRA API to get ticket information."""
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{ticket_id}"
    response = requests.get(url, auth=(JIRA_USERNAME, JIRA_API_TOKEN))
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error querying JIRA: {response.status_code}, {response.text}")

def analyze_changes(base_branch):
    """Gets the changes from the current branch compared to the specified base branch."""
    print("\n🔍 Analyzing changes in current branch...")
    try:
        repo = Repo(os.getcwd())
        
        # Try to fetch to update remote references
        print("Fetching latest changes from remote...")
        repo.remotes.origin.fetch()
        
        current_branch = repo.active_branch.name
        
        # Use specific format to compare branches and show content of changes
        print(f"Comparing {base_branch}...{current_branch}")
        diff = repo.git.diff(f'{base_branch}...{current_branch}', unified=0)  # unified=3 shows 3 lines of context
        
        if not diff:
            print("No changes detected.")
            return []

        # Modified to return complete diff instead of just file names
        return [diff]
        
    except Exception as e:
        print(f"❌ Error analyzing changes: {str(e)}")
        print("Using local changes only...")
        return []

def generate_natural_changes(changes):
    """Generates a natural language description of changes using OpenAI API."""
    print("\n🤖 Generating natural language description of changes...")
    changes_text = "\n".join(changes)
    prompt = (
        "You are a helpful assistant. Given the following list of changes in a codebase, "
        "generate a natural and professional summary of what was changed being brief:\n\n"
        f"{changes_text}\n\n"
        "Write the summary as a paragraph:"
    )
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes code changes. The goal is to write the changes in a way that is easy to understand for a non-technical person to include in the pull request description. Do it very brief."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    result = response.choices[0].message.content.strip()
    print(f"Generated summary: {result}")
    return result

def generate_how_to_use(changes):
    """Generates a 'How to use' section if relevant."""
    changes_text = "\n".join(changes)
    prompt = (
        "You are a programming assistant. Analyze the following changes in a codebase and determine if new functionality "
        "was added that might require usage instructions. If so, generate a very brief 'How to use' section with parameter details. "
        "If not, respond with 'No instructions needed':\n\n"
        f"{changes_text}\n\n"
    )
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates documentation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    result = response.choices[0].message.content.strip()
    return result if "No instructions needed" not in result else None

def generate_review_notes(changes):
    """Generates review notes and testing focus areas based on the changes."""
    print("\n🔍 Generating review notes...")
    changes_text = "\n".join(changes)
    prompt = (
        "Recommend some testing scenarios for the changes in the pull request. Be very brief:\n"
        f"Code changes:\n{changes_text}\n\n"
        "Format the response in bullet points."
    )
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior developer providing review guidance."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

def generate_pre_code_review(changes):
    """Generates a pre-code review analysis based on the changes."""
    print("\n🔍 Generating pre-code review analysis...")
    changes_text = "\n".join(changes)
    prompt = (
        "As a senior developer, perform a pre-code review analysis of these changes. Focus ONLY on:\n"
        "- Code style and best practices\n"
        f"Code changes:\n{changes_text}\n\n"
        "Be concise but thorough. Format the response in bullet points."
    )
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior developer performing a code review."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

def create_pr(branch_name, description, base_branch, ticket_id, ticket_summary):
    """Creates a Pull Request on GitHub with the generated description."""
    repo_name = get_repo_info()
    url = f"https://api.github.com/repos/{repo_name}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Format the PR title according to convention: Task/FOUR-xxx: Ticket Title
    pr_title = f"Task/{ticket_id}: {ticket_summary}"
    
    payload = {
        "title": pr_title,
        "head": branch_name,
        "base": base_branch,
        "body": description
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print("PR created successfully!")
    else:
        print(f"Error creating PR: {response.status_code}, {response.text}")

def get_repo_info():
    """Gets the repository name and owner from the git remote URL."""
    try:
        repo = Repo(os.getcwd())
        # Get the 'origin' remote URL
        remote_url = repo.remotes.origin.url
        
        # Handle different GitHub URL formats
        if remote_url.startswith('git@github.com:'):
            # Format: git@github.com:owner/repo.git
            path = remote_url.split('git@github.com:')[1]
        elif remote_url.startswith('https://github.com/'):
            # Format: https://github.com/owner/repo.git
            path = remote_url.split('https://github.com/')[1]
        else:
            raise Exception("No valid GitHub repository found")
        
        # Remove .git from the end if it exists
        path = path.replace('.git', '')
        
        # Split owner and repo
        owner, repo_name = path.split('/')
        return f"{owner}/{repo_name}"
    except Exception as e:
        print(f"❌ Error getting repository information: {str(e)}")
        exit(1)

def main():
    args = parse_args()
    print("\n🚀 Starting PR generation process...")
    
    branch_name = get_current_branch(args.repo_path)
    print(f"\n📌 Current branch: {branch_name}")
    
    match = re.search(r"FOUR-\d+", branch_name)
    if not match:
        print("❌ No JIRA ticket found in branch name.")
        return

    ticket_id = match.group(0)
    print(f"\n🎫 Found JIRA ticket: {ticket_id}")
    print("Fetching ticket information...")
    ticket_info = get_ticket_info(ticket_id)

    # Handle errors if fields are missing in the ticket
    summary = ticket_info['fields'].get('summary', 'No summary available')
    description = ticket_info['fields'].get('description', 'No description available')
    ticket_url = f"{JIRA_BASE_URL}/browse/{ticket_id}"

    # Analyze changes and generate natural description
    raw_changes = analyze_changes(args.base_branch)
    natural_changes = generate_natural_changes(raw_changes)

    # Generate "How to use" if relevant
    how_to_use = generate_how_to_use(raw_changes)
    # how_to_use = None

    # Generate review notes
    # review_notes = generate_review_notes(raw_changes)

    # Generate pre-code review
    # pre_code_review = generate_pre_code_review(raw_changes)

    # Create PR description
    pr_description = (
        f"### Description\n"
        f"{summary}\n\n"
        f"{description if description is not None else ''}\n"
        f"**Changes**\n"
        f"{natural_changes}\n\n"
        f"### Related tickets\n"
        f"- [{ticket_id}]({ticket_url})\n\n"
        f"### Related PRs\n"
        f"- (Add related PRs manually if needed)\n\n"
        # f"### Pre-Code Review Analysis\n"
        # f"{pre_code_review}\n\n"
        # f"### Notes for Reviewers\n"
        # f"{review_notes}\n\n"
    )
    if how_to_use:
        pr_description += f"### How to use\n{how_to_use}\n"

    github_repo = get_repo_info()
    print(f"GITHUB_REPO: {github_repo}")
    # create_pr(branch_name, pr_description, args.base_branch, ticket_id, summary)
    print("\n✅ PR description generated successfully!")
    print("\nGenerated PR Description:")
    print("------------------------")
    print(pr_description)
    print("------------------------")

if __name__ == "__main__":
    main()
