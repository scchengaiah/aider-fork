import os
import math
import logging
from collections import defaultdict, namedtuple
from pathlib import Path
import networkx as nx
from tree_sitter import Language, Parser
from tree_sitter_languages import get_language, get_parser
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token
import concurrent.futures

"""
    This is an AI Generated code to prepare repository graph. Not to the level of Aider, but does the job 😊
    AI conversation and the response can be found in extract_repo_map_2.json.

    We have used Melty VSCode extension with Anthropic to generate this code.
"""

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Tag = namedtuple("Tag", "rel_fname fname line name kind")

class EnhancedRepoMap: 
    def __init__(self, root):
        self.root = Path(root)
        self.tag_cache = {}
        self.tree_sitter_parsers = {}
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'cpp',
            '.cs': 'c_sharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
        }

    def get_rel_fname(self, fname):
        return os.path.relpath(fname, self.root)

    def get_language(self, file_path):
        return self.supported_languages.get(Path(file_path).suffix.lower())

    def get_parser(self, language):
        if language not in self.tree_sitter_parsers:
            try:
                parser = get_parser(language)
                self.tree_sitter_parsers[language] = parser
            except Exception as e:
                logger.error(f"Error loading parser for {language}: {e}")
                return None
        return self.tree_sitter_parsers[language]

    def get_tags_tree_sitter(self, fname, content, language):
        parser = self.get_parser(language)
        if not parser:
            return []

        tree = parser.parse(bytes(content, "utf8"))
        query = get_language(language).query("""
            (function_definition name: (identifier) @function.def)
            (class_definition name: (identifier) @class.def)
            (identifier) @identifier
        """)

        tags = []
        for node, tag_type in query.captures(tree.root_node):
            kind = "def" if tag_type.endswith(".def") else "ref"
            tags.append(Tag(self.get_rel_fname(fname), fname, node.start_point[0], node.text.decode('utf8'), kind))

        return tags

    def get_tags_pygments(self, fname, content):
        tags = []
        try:
            lexer = guess_lexer_for_filename(fname, content)
            tokens = list(lexer.get_tokens(content))

            for i, (token_type, token_value) in enumerate(tokens):
                if token_type in Token.Name:
                    kind = "def" if i > 0 and tokens[i-1][0] in Token.Keyword else "ref"
                    tags.append(Tag(self.get_rel_fname(fname), fname, -1, token_value, kind))
        except Exception as e:
            logger.error(f"Error processing file {fname} with Pygments: {e}")

        return tags

    def get_tags(self, fname):
        if fname in self.tag_cache:
            return self.tag_cache[fname]

        try:
            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read()
            
            language = self.get_language(fname)
            if language:
                tags = self.get_tags_tree_sitter(fname, content, language)
            else:
                tags = self.get_tags_pygments(fname, content)

            self.tag_cache[fname] = tags
            return tags

        except Exception as e:
            logger.error(f"Error processing file {fname}: {e}")
            return []

    def build_graph(self, files):
        G = nx.MultiDiGraph()
        defines = defaultdict(set)
        references = defaultdict(list)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(self.get_tags, fname): fname for fname in files}
            for future in concurrent.futures.as_completed(future_to_file):
                fname = future_to_file[future]
                try:
                    tags = future.result()
                except Exception as e:
                    logger.error(f"Error processing file {fname}: {e}")
                    continue

                rel_fname = self.get_rel_fname(fname)
                for tag in tags:
                    if tag.kind == "def":
                        defines[tag.name].add(rel_fname)
                    elif tag.kind == "ref":
                        references[tag.name].append(rel_fname)

        for ident in set(defines.keys()).intersection(set(references.keys())):
            definers = defines[ident]
            for referencer, num_refs in defaultdict(int, [(f, references[ident].count(f)) for f in references[ident]]).items():
                for definer in definers:
                    if referencer != definer:
                        G.add_edge(referencer, definer, weight=math.sqrt(num_refs), ident=ident)

        return G

    def rank_files(self, G):
        return nx.pagerank(G, weight="weight")

    def generate_map(self, ranked_files):
        map_content = ""
        for fname, rank in sorted(ranked_files.items(), key=lambda x: x[1], reverse=True):
            file_content = self.get_file_preview(fname)
            map_content += f"\n{fname} (rank: {rank:.4f}):\n{file_content}\n"
        return map_content.strip()

    def get_file_preview(self, fname):
        try:
            with open(self.root / fname, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]  # Get first 20 lines as preview
            return ''.join(lines).strip()
        except Exception as e:
            logger.error(f"Error reading file {fname}: {e}")
            return f"Error reading file: {e}"

    def get_repo_map(self, files):
        logger.info("Building graph...")
        G = self.build_graph(files)
        logger.info("Ranking files...")
        ranked_files = self.rank_files(G)
        logger.info("Generating map...")
        return self.generate_map(ranked_files)

def find_src_files(directory):
    src_files = []
    repo_map = EnhancedRepoMap(directory)  # Create an instance to access supported_languages
    for root, _, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in repo_map.supported_languages:
                src_files.append(os.path.join(root, file))
    return src_files

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python enhanced_repo_map.py <repository_root>")
        sys.exit(1)

    repo_root = sys.argv[1]
    repo_map = EnhancedRepoMap(repo_root)
    files = find_src_files(repo_root)
    
    logger.info(f"Found {len(files)} source files.")
    logger.info("Generating repository map...")
    
    map_content = repo_map.get_repo_map(files)
    print("\nRepository Map:")
    print(map_content)

    # Optionally, save the map to a file
    with open('repo_map.txt', 'w', encoding='utf-8') as f:
        f.write(map_content)
    logger.info("Repository map saved to repo_map.txt")