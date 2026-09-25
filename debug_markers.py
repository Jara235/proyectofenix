with open(r'c:\Users\JOSE\Desktop\Proyecto fenix\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "        # ── CONSULTA DE DATOS ─────────────────────────────────────────────────"
end_marker = "    except Exception as e:\n        import traceback\n        return jsonify({'success': False, 'error': str(e), 'trace': traceback.format_exc()})"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

print(f"start={start_idx}, end={end_idx}")
print("Snippet around start marker:")
print(repr(content[start_idx-5:start_idx+80]))
