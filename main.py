import sys
from src.luo_markdown import Create_html
if __name__ == "__main__":
    cmd_arg = sys.argv
    if (cmd_len := len(cmd_arg)) == 2:
        cmd_arg[2] = "index.html"
    Create_html(cmd_arg[1], cmd_arg[2])
