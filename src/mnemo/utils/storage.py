from pathlib import Path
import pickle


def save_pickle(data, path):

    with open(path, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_pickle(path):
    pass


def find_project_root(start: Path | None = None) -> Path:
    current = start or Path.cwd()

    while True:
        if (current / ".mnemo").is_dir():
            return current

        if current.parent == current:
            break

        current = current.parent

    raise RuntimeError("mnemo project not found (run `mnemo init` first)")
