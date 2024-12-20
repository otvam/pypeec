import shutil

print("a")
shutil.unpack_archive("tmp.tar.xz", "extract", format="xztar")

print("c")
