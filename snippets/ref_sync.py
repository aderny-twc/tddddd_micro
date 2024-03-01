import os
import shutil
from pathlib import Path

from snippets.hash_file import hash_file


def sync(source: Path, dest: Path) -> None:
    # Imperative shell
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    # Functional core
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # Imperative shell
    for action, *paths in actions:
        if action == 'COPY':
            shutil.copyfile(*paths)
        if action == 'MOVE':
            shutil.move(*paths)
        if action == 'DELETE':
            os.remove(paths[0])


def sync2(reader, filesystem, source_root, dest_root):
    source_hashes = reader(source_root)
    dest_hashes = reader(dest_root)
    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            sourcepath = source_root / filename
            destpath = dest_root / filename
            filesystem.copy(sourcepath, destpath)
        elif dest_hashes[sha] != filename:
            olddestpath = dest_root / dest_hashes[sha]
            newdestpath = dest_root / filename
            filesystem.move(olddestpath, newdestpath)
    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            filesystem.delete(dest_root / filename)


def determine_actions(src_hashes, dst_hashes, src_folder, dst_folder):
    for sha, filename in src_hashes.items():
        if sha not in dst_hashes:
            sourcepath = Path(src_folder) / filename
            destpath = Path(dst_folder) / filename
            yield 'COPY', sourcepath, destpath
        elif dst_hashes[sha] != filename:
            olddestpath = Path(dst_folder) / dst_hashes[sha]
            newdestpath = Path(dst_folder) / filename
            yield 'MOVE', olddestpath, newdestpath
    for sha, filename in dst_hashes.items():
        if sha not in src_hashes:
            yield 'DELETE', dst_folder / filename


def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes


if __name__ == "__main__":
    source = Path("/home/ando/MEGAsync/playground/tddddd_micro/snippets/test_sync/source/")
    dest = Path("/home/ando/MEGAsync/playground/tddddd_micro/snippets/test_sync/dest/")

    sync(source, dest)
