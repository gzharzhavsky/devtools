import pytest
import os.path

from github_commit_report import GithubContext , generate_html_report

def test_commit():
    sha='153b391a8d6bf36264e5b44786faf844c0df2d76'
    owner='gzharzhavsky'
    repo='devtools'
    branch='main'
    git=GithubContext(repo_owner=owner, repo_name=repo , repo_branch=branch )
    items=git.git_commits()
    
    for item in items:
        if not  'sha' in item: assert False
        if not  'author' in item: assert False
        if not  'message' in item: assert False


def test_html_report():
    items=[{'sha':'a1b2c3d','author':'Gary', 'message':'This is a test commit'}]
    generate_html_report(items, 'test/output', 'report.html')
   
    if not os.path.exists('test/output.html' ): assert False

    seen=0
    with open('test/output.html') as f:
        if 'a1b2c3d' in f.read():
            seen=1

    assert seen == 1

