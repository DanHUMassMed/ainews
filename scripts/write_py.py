import sys, base64, pathlib
target = pathlib.Path(sys.argv[1])
content = base64.b64decode(sys.argv[2].encode('utf-8'))
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(content)
print(f'Wrote {len(content)} bytes to {target}')
