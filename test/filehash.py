import hashlib
#读取文件
f = open('resfiles/1/郭仪.jpg', 'rb')
 
thehash = hashlib.md5()
#读取文件第一行
theline = f.readline()
 
#逐行读取文件，并计算
while(theline):
    thehash.update(theline)
    theline = f.readline()
#哈希值
print(thehash.hexdigest())