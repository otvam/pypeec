import shutil

print("a")
shutil.unpack_archive("tmp.tar.xz", "extract", format="xztar")

print("b")
shutil.unpack_archive("tmp.tar.xz", "extract", format="xztar", filter="data")

print("c")
