import tkinter as tk
from gui_classes.display import Display


def main(pages=None):
    """
    TODO: Write documentation
    """

    root = tk.Tk()
    Display(root, pages)
    root.mainloop()


if __name__ == '__main__':
    main()
