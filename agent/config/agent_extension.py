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
        if not 'cron_interval' in self.params: self.params['cron_interval'] = 60
        self.dialogAskInteger('cron_interval', 'The time between cron executes', 60)
        if not 'enable_cron' in self.params: self.params['enable_cron'] = True
        self.dialogAskYesNo('enable_cron', 'Enable Cron Tasklets Execution')

AgentConfig = ItemGroupClass(AgentConfigItem)
