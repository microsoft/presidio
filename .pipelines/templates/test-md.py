import os
import exdown


for root, dirs, files in os.walk("."):
  for file in files:
      if (file.endswith(".md") or file.endswith(".MD")):
        filename = os.path.join(root,file)
        print(filename)
        blocks = exdown.extract(filename, encoding=None, syntax_filter="python")
        for code, line in blocks:
          try:
            exec(code)
          except Exception:
            print(f"{filename} (line {line}) failed")
            raise