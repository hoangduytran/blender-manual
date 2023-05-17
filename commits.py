from pathlib import Path
from git import Repo

repo_path = "/home/aaroncarlisle/Documents/projects/blender_foundation/blender/src/"

repo = Repo(Path(repo_path))

commit_log = open('blender-3.6', 'r')
commits = commit_log.readlines()

for commit_hash in commits:
    commit = repo.commit(commit_hash)
    commit_hash_short = commit_hash[:10]
    commit_url = "https://projects.blender.org/blender/blender/commit/" + commit_hash_short
    commit_title = commit.message.partition('\n')[0]
    commit_author = commit.author

    print("- [ ] [{}]({}) {} ({})".format(commit_hash_short,
          commit_url, commit_title, commit_author))
