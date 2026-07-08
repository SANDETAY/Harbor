import subprocess
import sys

r = subprocess.run(
    [sys.executable, r"C:\Users\Taylor\Rythm\scripts\sim-test.py"],
    cwd=r"C:\Users\Taylor\Rythm",
    capture_output=True,
    text=True,
)
out = (r.stdout or "") + (r.stderr or "") + f"\nEXIT:{r.returncode}\n"
with open(r"C:\Users\Taylor\Rythm\sim-out3.txt", "w", encoding="utf-8") as f:
    f.write(out)
print(out, end="")
sys.exit(r.returncode)