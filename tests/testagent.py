import unittest
import base64
import xmlrpclib
from pymonkey.InitBase import q,i

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.proxy = xmlrpclib.ServerProxy('http://localhost:8888')
        self.config = i.config.agent.getConfig('main')

    def testget_agent_id(self):
        id = self.config['agentguid']
        agent_guid = self.proxy.agent_service.get_agent_id()
        self.assertEqual(id,agent_guid)
    
    def testlistRunningProcesses(self):
        self.assertTrue(self.proxy.agent_service.listRunningProcesses(),'No processes running')

    def testlog(self):
        self.assertTrue(self.proxy.agent_service.log(100,5,base64.encodestring('working?')))

if __name__ == "__main__":
    unittest.main()
