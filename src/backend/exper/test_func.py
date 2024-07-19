from typing import Annotated

from tools_utils import tools_function
FUNCTIONS = {}

def func_foo(
        role: Annotated[str, ""], 
        description: Annotated[str, ""]

):
    """
    This is function returns a description along with the role. 
    """
