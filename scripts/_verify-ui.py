from pathlib import Path
import re

t = Path("index.html").read_text(encoding="utf-8")
print("Task span", t.count(">Task</span>"))
print("Today nav label", "nav-tab-label\">Today" in t)
print("life-flyout", t.count("life-flyout"))
print("life-panels-scroll", t.count("life-panels-scroll"))
print("Add to Task", t.count("Add to Task"))
print("Add to Today", t.count("Add to Today"))
print("Open Task", t.count("Open Task"))
print(re.search(r"HARBOR_BUILD_NUMBER = \d+", t).group(0))
# structural check
assert 'id="tab-today"' in t
assert 'id="life-flyout"' in t
assert "selectLifeSection" in t
assert "onLifeNavClick" in t
assert "life-panels-scroll" in t
assert ">Task</span>" in t
print("structure ok")
