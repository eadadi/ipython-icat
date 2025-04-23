import os
import subprocess
from traitlets.config import Config
from traitlets.config.loader import PyFileConfigLoader


def get_profile_path(ipython_path, profile_name):
    """Silently create a default profile if it doesn't exist"""
    if ipython_path is None:
        ipython_path = os.path.expanduser("~/.ipython")
    profile_dir = os.path.join(ipython_path, f"profile_{profile_name}")
    if not os.path.exists(profile_dir):
        subprocess.run(["ipython", "profile", "create", profile_name])
    profile_path = os.path.join(profile_dir, "ipython_config.py")
    return profile_path


def dynamic_update_config(profile_path, profile_dir):
    """Returns updated extensions and exec_lines"""
    # Create Config object and load existing configuration if available
    config = Config()
    if os.path.exists(profile_path):
        config_loader = PyFileConfigLoader(
            filename="ipython_config.py", path=profile_dir
        )
        config = config_loader.load_config()

    # Ensure extensions and exec_lines are lists
    extensions = config.get("InteractiveShellApp", {}).get("extensions", [])
    exec_lines = config.get("InteractiveShellApp", {}).get("exec_lines", [])

    if "icat" not in extensions:
        extensions.append("icat")

    if "%plt_icat" not in exec_lines:
        exec_lines.append("%plt_icat")

    extensions_line = f"c.InteractiveShellApp.extensions = {extensions}\n"
    exec_lines_line = f"c.InteractiveShellApp.exec_lines = {exec_lines}\n"

    return extensions_line, exec_lines_line


def dynamic_update_file(profile_path, extensions_line, exec_lines_line):
    # Read and modify only the necessary lines
    if os.path.exists(profile_path):
        with open(profile_path, "r") as f:
            lines = f.readlines()

        # Modify lines if they exist; otherwise, add them
        found_extensions = False
        found_exec_lines = False

        for i, line in enumerate(lines):
            if line.startswith("c.InteractiveShellApp.extensions ="):
                lines[i] = extensions_line
                found_extensions = True
            elif line.startswith("c.InteractiveShellApp.exec_lines ="):
                lines[i] = exec_lines_line
                found_exec_lines = True

        if not found_extensions:
            lines.append(extensions_line)
        if not found_exec_lines:
            lines.append(exec_lines_line)

        return lines
    else:
        return [extensions_line, exec_lines_line]
