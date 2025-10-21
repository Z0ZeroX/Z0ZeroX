import os
import sys
from github import Github, Auth

from src.game_controller import process_game_action


def main():
    try:
        auth = Auth.Token(os.environ['GITHUB_TOKEN'])
        repo = Github(auth=auth).get_repo(os.environ['GITHUB_REPOSITORY'])
        issue = repo.get_issue(number=int(os.environ['ISSUE_NUMBER']))
        
        issue_author = '@' + issue.user.login
        repo_owner = '@' + os.environ['REPOSITORY_OWNER']
        
        success, error_message = process_game_action(issue, issue_author, repo_owner)
        
        if not success:
            sys.exit(error_message)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(f"Fatal error: {str(e)}")


if __name__ == '__main__':
    main()
