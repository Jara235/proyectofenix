import re

with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start marker (after the styles/setup block)
start_marker = "        # ── CONSULTA DE DATOS ─────────────────────────────────────────────────"
end_marker = "    except Exception as e:\n        import traceback\n        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()})"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print(f"Markers not found. start={start_idx}, end={end_idx}")
    # Try to find alternate markers
    print("Searching for 'CONSULTA DE DATOS':", "CONSULTA DE DATOS" in content)
    print("Searching for old version...")
    idx = content.find("# ── CONSULTA DE DATOS")
    print(f"Found at: {idx}")
else:
    print(f"Found start at {start_idx}, end at {end_idx}")
