from components.root_window import RootWindow

# main entrypoint for the program
# in the future, we could use something like this to package it into an executable:
# https://pyinstaller.org/en/stable/


def main():
    root_window = RootWindow()
    root_window.start()


if __name__ == "__main__":
    main()
