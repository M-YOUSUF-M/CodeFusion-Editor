import subprocess, shutil, platform
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

pkg_map = {
    "apt": "sudo apt install {} -y",
    "dnf": "sudo dnf install {} -y",
    "pacman": "sudo pacman -S {}",
    "apk": "sudo apk add {} -y",
    "zypper": "sudo zypper install {} -y",
    "brew": "brew install {} -y",
}

term_map = {
    "konsole": "konsole --hold -e {}",
    "alacritty": "alacritty --hold -e {}",
    "kitty": "kitty --hold --detach -e {}",
    "powershell":"powershell -NoExit -Command {}",
    "gnome-terminal": "gnome-terminal --hold -e {}",
    "xfce-terminal": "xfce-terminal --hold -e {}",
    "xterm": "xterm --hold -e {}",
}

def execute_cmd(cmd):
    for term in term_map:
        if shutil.which(term) is not None:
            final = term_map[term].format(cmd)
            subprocess.Popen(final, shell=True)
            break

def install(package):
    if not shutil.which(package):
        print(f"Package {package} is not installed")
    for pkg in pkg_map:
        if shutil.which(pkg) is not None:
            cmd = pkg_map[pkg].format(package)
            execute_cmd(cmd)

def prompt_pkg(package):
    app = QApplication([])
    main_context = QWidget()
    main_context.setFixedSize(360,80)
    main_context.setWindowTitle(f"Install {package}")

    text_box = QLabel(f"Do you want to install {package}?")

    ok_btn = QPushButton("OK")
    cc_btn = QPushButton("Cancel")
    ok_btn.clicked.connect(lambda: install(package) or app.closeAllWindows())
    cc_btn.clicked.connect(main_context.close)

    main_layout = QVBoxLayout()
    btn_layout = QHBoxLayout()
    btn_layout.addWidget(ok_btn)
    btn_layout.addWidget(cc_btn)
    main_layout.addWidget(text_box)
    main_layout.addLayout(btn_layout)
    # main_layout.addWidget(ok_btn)
    # main_layout.addWidget(cc_btn)

    main_context.setLayout(main_layout)
    main_context.show()
    app.exec_()