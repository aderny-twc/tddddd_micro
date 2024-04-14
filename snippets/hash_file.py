import hashlib
from pathlib import Path

BLOCKSIZE = 65536


def hash_file(path: str | Path) -> str:
    hasher = hashlib.sha1()

    with path.open("rb") as file:
        # Read block
        buf = file.read(BLOCKSIZE)
        # if file hasn't ended, update hash
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
        return hasher.hexdigest()


if __name__ == "__main__":
    path = Path(
        "/home/ando/MEGAsync/playground/tddddd_micro/snippets/test_sync/source/file.txt"
    )
    result = hash_file(path)
    print(result)
