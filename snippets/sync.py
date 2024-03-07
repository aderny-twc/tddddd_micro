import os
import shutil
from pathlib import Path

from snippets.hash_file import hash_file


def sync(source: Path, dest: Path) -> None:
    source_hashes = {}
    for folder, _, files in os.walk(source):
        for filename in files:
            source_hashes[hash_file(Path(folder) / filename)] = filename

    seen = set()

    for folder, _, files in os.walk(dest):
        for filename in files:
            dest_path = Path(folder) / filename
            dest_hash = hash_file(dest_path)
            seen.add(dest_hash)

            if dest_hash not in source_hashes:
                # dest_path.resolve()
                os.remove(dest_path)

            elif dest_hash in source_hashes and filename != source_hashes[dest_hash]:
                shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])

    for src_hash, filename in source_hashes.items():
        if src_hash not in seen:
            shutil.copy(Path(source) / filename, Path(dest) / filename)


if __name__ == "__main__":
    source = Path("/home/ando/MEGAsync/playground/tddddd_micro/snippets/test_sync/source/")
    dest = Path("/home/ando/MEGAsync/playground/tddddd_micro/snippets/test_sync/dest/")

    sync(source, dest)
