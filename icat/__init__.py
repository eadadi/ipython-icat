# modified from https://github.com/jktr/matplotlib-backend-kitty

from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.core.magic import Magics, magics_class, line_magic

from subprocess import run
from io import BytesIO
import sys
import os

from matplotlib.backend_bases import _Backend, FigureManagerBase
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib import interactive, is_interactive
from matplotlib._pylab_helpers import Gcf
import matplotlib

from PIL import Image
from . import utils


PACKAGE_NAME = "pycat"


if hasattr(sys, "ps1") or sys.flags.interactive:
    interactive(True)


def _run(*cmd):
    def f(*args, output=True, **kwargs):
        if output:
            kwargs["capture_output"] = True
            kwargs["text"] = True
        r = run(cmd + args, **kwargs)
        if output:
            return r.stdout.rstrip()

    return f


_icat = _run("kitten", "icat", "--align", "left")


class FigureManagerICat(FigureManagerBase):
    def show(self):
        with BytesIO() as buf:
            self.canvas.figure.savefig(buf, format="png")
            _icat(output=False, input=buf.getbuffer())


class FigureCanvasICat(FigureCanvasAgg):
    manager_class = FigureManagerICat


@_Backend.export
class _BackendICatAgg(_Backend):
    FigureCanvas = FigureCanvasICat
    FigureManager = FigureManagerICat
    mainloop = lambda: None

    @classmethod
    def draw_if_interactive(cls):
        manager = Gcf.get_active()
        if is_interactive() and manager.canvas.figure.get_axes():
            cls.show()

    @classmethod
    def show(cls, *args, **kwargs):
        _Backend.show(*args, **kwargs)
        Gcf.destroy_all()


@magics_class
class ICatMagics(Magics):
    @line_magic
    def plt_icat(self, line):
        matplotlib.use("module://icat")
        print("loaded icat backend for mpl")

    @magic_arguments()
    @argument("image", help="PIL Image object or path to image file")
    @argument("-w", "--width", type=int, help="Width to resize the image")
    @argument("-h", "--height", type=int, help="Height to resize the image")
    @line_magic
    def icat(self, line):
        args = parse_argstring(self.icat, line)
        image_arg = args.image.strip()

        # check if the input is a variable in the user's ns
        user_ns = self.shell.user_ns
        if image_arg in user_ns and isinstance(user_ns[image_arg], Image.Image):
            img = user_ns[image_arg]
        elif os.path.isfile(image_arg):
            img = Image.open(image_arg)
        else:
            print(
                f"Error: '{image_arg}' is neither a valid PIL Image nor a path to an image file."
            )
            return

        # resize the image if width or height is specified
        if args.width or args.height:
            img.thumbnail((args.width or img.width, args.height or img.height))

        # display image
        with BytesIO() as buf:
            img.save(buf, format="PNG")
            _icat(output=False, input=buf.getbuffer())


def icat(img: Image.Image, width: int = None, height: int = None):
    img_ = img.copy()
    with BytesIO() as buf:
        if width or height:
            img_.thumbnail((width or img.width, height or img.height))
        img_.save(buf, format="PNG")
        _icat(output=False, input=buf.getbuffer())


def load_ipython_extension(ipython):
    ipython.register_magics(ICatMagics)


def setup_ipython_profile(ipython_path=None, profile_name="default"):
    """Update or create an IPython profile to use the icat backend."""

    profile_path = utils.get_profile_path(ipython_path, profile_name)
    extensions_line, exec_lines_line = utils.dynamic_update_config(
        profile_path, os.path.dirname(profile_path)
    )
    lines = utils.dynamic_update_file(profile_path, extensions_line, exec_lines_line)
    with open(profile_path, "w") as f:
        f.writelines(lines)


def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_ipython_profile()
    else:
        print(f"Usage: {PACKAGE_NAME} setup")


if __name__ == "__main__":
    main()
