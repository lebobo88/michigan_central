"""Create output folders without changing supplied model or material inputs."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ['models','exports','renders','manifests','qa']:(root/name).mkdir(parents=True,exist_ok=True)
print('Output folders ready:',root)
