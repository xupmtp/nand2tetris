import os

print(list(filter(lambda f: f.endswith('.vm'), os.listdir('../FunctionCalls/StaticsTest'))))

with open('../FunctionCalls/StaticsTest/Sys.vm') as f:
    print(f.readlines())