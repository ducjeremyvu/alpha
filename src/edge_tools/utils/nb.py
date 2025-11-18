import os


def change_to_root_dir(target_dir_name="alpha"):
    """
    Change the current working directory to the nearest parent directory named `target_dir_name`.

    Parameters
    ----------
    target_dir_name : str, optional
        The name of the directory you want to move up to.


    Notes
    -----
    This function walks upward from the current directory until it
    finds `target_dir_name` or hits the filesystem root.
    """

    if not target_dir_name:
        raise ValueError("target_dir_name must be provided")

    cur = os.getcwd()

    while os.path.basename(cur) != target_dir_name and cur != "/":
        cur = os.path.dirname(cur)

    os.chdir(cur)
    print("Now in:", os.getcwd())
