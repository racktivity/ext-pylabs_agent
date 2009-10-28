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
        self.dialogAskString('agentguid', 'The guid of the agent', 'agent1')
        self.dialogAskString('xmppserver', 'The dns-address of the xmpp server', 'dmachine.office.aserver.com')
        self.dialogAskPassword('password', 'The password for the agent on the xmpp server', 'test')
        self.dialogAskString('agentcontrollerguid', 'The guid of the agentcontroller', 'agentcontroller')
	self.dialogAskInteger('cron_interval', 'The time between cron executes', 60)

AgentConfig = ItemGroupClass(AgentConfigItem)
