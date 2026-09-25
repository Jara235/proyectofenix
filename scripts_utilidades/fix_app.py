with open('dashboard_fenix.py', 'a', encoding='utf-8') as f:
    f.write('\n@app.route("/")\n')
    f.write('def index():\n')
    f.write('    return render_template("index.html")\n\n')
    f.write('if __name__ == "__main__":\n')
    f.write('    app.run(debug=True, port=5000, host="0.0.0.0")\n')
print('Restored app.run successfully')
