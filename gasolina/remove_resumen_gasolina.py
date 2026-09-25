import re

file_path = r'c:\Users\JOSE\Desktop\Proyecto fenix\servidor\templates\admin\admin_gasolina.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove button
content = re.sub(r'<button id="btnTabResumen".*?</button>\s*', '', content)

# 2. Remove table
content = re.sub(r'<table class="admin-table" id="tabla-resumen".*?</table>\s*', '', content, flags=re.DOTALL)

# 3. Remove from switchTab
content = re.sub(r"document\.getElementById\('btnTabResumen'\)\.classList\.remove\('active'\);\s*", '', content)
content = re.sub(r"document\.getElementById\('tabla-resumen'\)\.style\.display = 'none';\s*", '', content)
content = re.sub(r"} else if \(tab === 'resumen'\) \{.*?\}\s*", '} ', content, flags=re.DOTALL)

# 4. Remove from cargarDatos url
content = re.sub(r"else if \(currentTab === 'resumen'\) url = `/api/admin/autorizaciones\?tipo=GASOLINA&resumen=true\${semanaNumParam}`;\s*", '', content)

# 5. Remove from cargarDatos rendering
render_regex = r"\} else if \(currentTab === 'resumen'\) \{.*?\}\s*(?=\}\);)"
content = re.sub(render_regex, '}', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed resumen from admin_gasolina.html")
