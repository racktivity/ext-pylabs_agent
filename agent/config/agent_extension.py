import pymonkey
from pymonkey.config import *
from pymonkey import q

class AgentConfigItem(ConfigManagementItem):
    """
    Configuration of the agent.
    """

    CONFIGTYPE = "agent"
    DESCRIPTION = "agent configuration"

    def ask(self):
        pass
    
AgentConfig = ItemGroupClass(AgentConfigItem)
