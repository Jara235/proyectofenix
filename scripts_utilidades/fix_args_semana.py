import re

file = r"c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py"
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# We look for semana  = request.args.get('semana', '') or semana = request.args.get('semana', '')
content = re.sub(
    r"semana\s*=\s*request\.args\.get\('semana',\s*['\"]{0,2}\)", 
    r"semana = str(request.args.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()", 
    content
)

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Replaced args.get('semana')")
