import shutil
import os

from numpy import absolute

rootPath = os.path.abspath('.')

print(rootPath)

for root, dirs, files in os.walk(rootPath):
    if root.endswith('migrations') and root.find('templates') == -1:
        for dir in dirs:
            if dir.endswith('__pycache__'):
                absoluteName = root + "/" + dir
                print("delete folder ", absoluteName)
                shutil.rmtree(absoluteName)
        for fileName in files:
            if not fileName.endswith("__init__.py"):
                absoluteName = root + "/" +fileName
                print("delete migration file:", absoluteName)
                os.remove(absoluteName)
