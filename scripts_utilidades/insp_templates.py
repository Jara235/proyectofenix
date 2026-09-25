import os
for root, dirs, files in os.walk(r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates'):
    for f in files:
        if 'dashboard' in f or 'index' in f:
            print(os.path.join(root, f))
