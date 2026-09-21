import subprocess

with open('scripts/extracted_bm.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace ; with ;\n and { with {\n and } with }\n
formatted = c.replace(';', ';\n').replace('{', '{\n').replace('}', '}\n')

with open('scripts/formatted_bm.js', 'w', encoding='utf-8') as f:
    f.write(formatted)

r = subprocess.run(['node', '-c', 'scripts/formatted_bm.js'], capture_output=True, text=True)
print("Return code:", r.returncode)
print("STDOUT:", r.stdout)
print("STDERR:", r.stderr)
