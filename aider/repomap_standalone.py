from aider.io import InputOutput
from aider.repo import GitRepo
from aider.coders import Coder
from aider import models
import os

def get_repo_map(git_root = ".", 
                 repo_content_prefix = None, 
                 aider_ignore_file=".aiderignore", 
                 model="gpt-4o-2024-08-06",
                 map_tokens=1024, 
                 map_mul_no_files=2):
    
    aider_ignore_file_path = os.path.join(git_root, aider_ignore_file) if git_root else aider_ignore_file
    io = InputOutput(yes=True)
    
    repo = GitRepo(io=io, fnames= None, git_dname=git_root, aider_ignore_file=aider_ignore_file_path)
    
    coder = Coder.create(main_model=models.Model(model), 
                         edit_format="whole", repo=repo, io=io, 
                         map_tokens=map_tokens, map_mul_no_files=map_mul_no_files,
                         repo_content_prefix = repo_content_prefix)
    
    repo_map = coder.get_repo_map(force_refresh=True)
    
    return repo_map

if __name__ == "__main__":
    git_root = "D:/tmp/genai/agency-swarm"
    repo_map = get_repo_map(git_root)
    print(repo_map)