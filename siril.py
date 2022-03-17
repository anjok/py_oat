from pysiril.siril import Siril
from pysiril.wrapper import Wrapper
from pysiril.addons import Addons

app = Siril()  # Starts pySiril
cmd = Wrapper(app)  # Starts the command wrapper

help(Siril)  # Get help on Siril functions
help(Wrapper)  # Get help on all Wrapper functions
help(Addons)  # Get help on all Addons functions

cmd.help()  # Lists of all commands
cmd.help("bgnoise")  # Get help for bgnoise command

del app
