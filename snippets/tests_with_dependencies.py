from pathlib import Path

from snippets.ref_sync import sync2


class FakeFileSystem(list):
    def copy(self, src, dest):
        self.append(("COPY", src, dest))

    def move(self, src, dest):
        self.append(("MOVE", src, dest))

    def delete(self, src, dest):
        self.append(("DELETE", src, dest))


def test_when_a_file_exists_in_the_source_but_not_the_destination():
    source = {"sha1": "my-file"}
    dest = {}
    filesystem = FakeFileSystem()
    reader = {Path("/source/"): source, Path("/dest/"): dest}
    sync2(reader.pop, filesystem, Path("/source/"), Path("/dest/"))
    assert filesystem == [("COPY", Path("/source/my-file"), Path("/dest/my-file"))]
