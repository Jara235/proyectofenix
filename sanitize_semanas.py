import re

files = [r"c:\Users\JOSE\Desktop\Proyecto fenix\app_captura.py", r"c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py"]

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to find any variable assignment like: semana = data.get('semana', '')
    # and change it to: semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()
    
    # For app_captura.py where it uses data.get('semana') directly in queries:
    content = re.sub(r"data\.get\('semana'\)", r"str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()", content)
    
    # For assignments
    content = re.sub(r"semana\s*=\s*data\.get\('semana',\s*['\"]{0,2}\)", r"semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()", content)
    
    # For app_admin.py where it has semana = str(data.get('semana', ''))
    content = re.sub(r"semana\s*=\s*str\(data\.get\('semana',\s*['\"]{0,2}\)\)", r"semana = str(data.get('semana', '')).replace('Semana ', '').replace('Semana', '').strip()", content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Updated python files to sanitize 'semana'")
