import inspect
from langchain_core.tools import tool, BaseTool
import Tools.MySQL as MySQL



var1= True
a = 5
b = 5
@tool
def pin():
    """
    return var1 that assign externally
 
    Returns:
        var1 (str): string assigned externally.
    """
    
    if var1:
        return a+b
    else:
        return "no variable is assigned"
