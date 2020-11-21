#!/usr/bin/env python3

import os
import sys
import argparse
from github import Github
from jinja2 import Environment, FileSystemLoader
import json


class GithubContext(object):
    """ This class allow to access commit info from github.
    Uses  API https://developer.github.com/v3/
    """
    def __init__(self, base_url, repo_owner, repo_name, repo_branch, commit_history=5, 
                 ,verbosity=0):

        self.base_url       = base_url
        self.repo_owner     = repo_owner
        self.repo_name      = repo_name
        self.repo_branch    = repo_branch
        self.commit_history = commit_history

        self.verbosity=verbosity

    def token(self):
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print('github token  is missing\n Setup access token and export GITHUB_TOKEN')
            sys.exit(1)
        return token

    def git_repo(self):

        if self.base_url != "https://github.com/":
            github = Github(base_url=self.base_url+'api/v3', login_or_token=self.token(), per_page=self.commit_history)
        else:
            github = Github(login_or_token=self.token(), per_page=self.commit_history)

        #try:
        org = github.get_organization(self.repo_owner)
        repo = org.get_repo(self.repo_name)
        #except :
        #    print ('Failed to access to: ' + self.base_url + '/' + self.repo_owner + '/' + self.repo_name)

        return repo

    def git_commits(self):

        items = []

        repo=self.git_repo()
        commits=repo.get_commits(sha=self.repo_branch)[:self.commit_history]
        for commit in commits:
            if commit.commit is not None:
                sha=commit.sha
                gitcommit=repo.get_git_commit(commit.sha)  # GitCommit
                author=gitcommit.author.name
                message=gitcommit.message

                an_item=dict ( sha=sha, author=author, message=message ) 
                items.append(an_item)

                if self.verbosity > 1:
                    print('sha: ' + sha)
                    print('message: ' + message)
                    print('author: '  + author)
                    print('-'* 80)

                
        return items


def generate_html_report(items, output_file, template_file):
    """ This function generates html report

    Parameters:
    items (list): Each item in the list is a dictionary with keys: sha, author, message 
    output_file(string): The path for the output file. The file extension '.html' is added to the file
    template_file(string): The jinja template_file is placed in 'templates' directory  """

    # todo , externalize 'templates'
    file_loader=FileSystemLoader('templates')
    env=Environment(loader=file_loader)
    
    template = env.get_template(template_file)
    output=template.render(items=items)
    f = open(output_file + '.html', "w")
    f.write(output)
    f.close()


def generate_json_report(items, output_file):
    """ This function generates json report

    Parameters:
    items (list): Each item in the list is a dictionary with keys: sha, author, message 
    output_file(string): The path for the output file. The file extension '.json' is added to the file

    """
    with open(output_file + '.json' , 'w') as file:
        json.dump(items, file, indent=4, sort_keys=True)
    


def main():

    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Retrieves last n commits info from the github: sha, author and message.")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('-v', '--verbosity', action="count", default=0)
    parser.add_argument('-u', '--base-url', default='https://github.com/', help='url github')
    parser.add_argument('-o', '--repo-owner', required=True, help='The GitHub repo owner aka organisation.')
    parser.add_argument('-n', '--repo-name',  required=True, help='The GitHub repo name.')
    parser.add_argument('-b', '--repo-branch', default='master', help='The GitHub repo branch.')
    parser.add_argument('-y', '--commit-history',type=int, default=5 , help='The GitHub commits history')
    parser.add_argument('-f', '--output-file', default='output_report', help='Output file w/o extension')
    parser.add_argument('-t', '--template-file', default='report.html', help='Template file name in templates directory.')
    parser.add_argument('-m', '--format',default='html', choices=['html', 'json'],
                        help='format: html or json (default: %(default)s)')


    args = parser.parse_args()

    git=GithubContext(base_url=args.base_url, repo_owner=args.repo_owner, repo_name=args.repo_name,
                      repo_branch=args.repo_branch, verbosity=args.verbosity,
                      commit_history=args.commit_history)
    items=git.git_commits()

    if args.verbosity: 
        for item in items:  print(item)

    if args.format == 'html':
        generate_html_report(items, args.output_file, args.template_file)
    else:
        generate_json_report(items, args.output_file) 



if __name__== "__main__":
        main()
