import sys

with open(f"./out/Pong/{sys.argv[1]}.vm", "r") as f1, open(f"./out/Pong/{sys.argv[2]}.vm", "r") as f2:
    l1 = f1.readlines()
    l2 = f2.readlines()
    i = min(len(l1), len(l2)) - 1
    end = 0 if len(sys.argv) <= 3 else int(sys.argv[3])
    while i >= end:
        s1, s2 = l1[i].strip(), l2[i].strip()
        if s1 != s2:
            print(f"{i+1} {l1[i].strip() :30}     {l2[i].strip()}")
        i -= 1

