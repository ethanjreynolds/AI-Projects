# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 21:52:49 2025

@author: clash
"""

def checkpal(str):
    for i in range(int(len(str)/2)):
        if str[i] != str[len(str)-(i+1)]:
            return False
    return True
        
print(checkpal("aghga"))

def reverse_words(str):
    s = str.split(" ")
    out = ""
    for i in range(len(s)):
        if i != 0:
            out = out + " " + s[len(s)-(i+1)]
        else:
            out = s[len(s)-(i+1)]
    return out
        
def count_unique(str):
    count = 0
    seen = []
    for ch in str:
        if ch not in seen:
            count += 1
            seen.append(ch)
            
    return count

def swap(a, b):
    temp = a
    a = b
    b = temp
    return a, b

# def firstnonrepeat(nums):
#     seen = []
#     for i in nums:
#         if i not in seen:
#             seen.append((i, True))
#         else:
#             seen
#     if seen is empty:
#         return None
#     else:
#         return seen[0]

def anagram(a, b):
    return sorted(a) == sorted(b)
    
    
    
    