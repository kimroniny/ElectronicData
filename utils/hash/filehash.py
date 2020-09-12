import hashlib
import os
import queue

class FilesHash:
    def __init__(self):
        pass

    def calcHashForDir(self, dirPath):
        result = []
        if not os.path.exists(dirPath):
            return ""
        for root, _, files in os.walk(dirPath, topdown=True):
            for file_ in files:
                filepath = os.path.join(root, file_)
                filehashstr = self.calcHashForFile(filePath=filepath)
                result.append(filehashstr)
        return self.calcHashForStr("%".join(result))
        
        # 一段广搜遍历文件夹的小代码
        # dirQueue = queue.Queue()
        # dirQueue.put(dirPath)
        # while not dirQueue.empty():
        #     if os.path.exists(dirPath):
        #         continue
        #     for root, dirs, files in os.walk(dirPath):
        #         for dir_ in dirs:
        #             nextDirPath = os.path.join(root, dir_)
        #             dirQueue.put(nextDirPath)
        #         for file_ in files:
        #             filepath = os.path.join(root, file_)
        #             filehashstr = self.calcHashForFile(filePath=filepath)
        #             result.append(filehashstr)


    def calcHashForFile(self, filePath, blockSize = 2**20):
        if not os.path.exists(filePath):
            return ""
        thehash = hashlib.sha256()
        with open(filePath, 'rb') as f:
            while True:
                buf = f.read(blockSize)
                if not buf:
                    break
                thehash.update(buf)
        thehash.digest()
        return thehash.hexdigest()

    def calcHashForStr(self, *args):
        thehash = hashlib.sha256()
        for text in args:
            thehash.update(str(text).encode('utf-8'))
        return thehash.hexdigest()

if __name__ == "__main__":
    fileHash = FilesHash()
    result = fileHash.calcHashForDir('./resfiles')
    print(result)