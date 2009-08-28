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
        self.dialogAskString('agentguid', 'The guid of the agent', None)
        self.dialogAskString('xmppserver', 'The dns-address of the xmpp server', None)
        self.dialogAskPassword('password', 'The password for the agent on the xmpp server', None)
        self.dialogAskString('agentcontrollerguid', 'The guid of the agentcontroller', None)

AgentConfig = ItemGroupClass(AgentConfigItem)