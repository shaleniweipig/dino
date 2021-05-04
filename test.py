from collections import deque

a = [1,2,3,5,3,8,10, 2,3,4]
rm_count = 3
while rm_count:
    a.pop(0)
    rm_count -= 1
print(a)