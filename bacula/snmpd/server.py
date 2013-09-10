from pysnmp.entity import engine, config
from pysnmp import debug
from pysnmp.entity.rfc3413 import cmdrsp, context, ntforg
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.smi import builder 

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker

from bacula.snmpd.sql_classBacula import Job, Client
import os
import threading
import collections
import time
import datetime

#can be useful
#debug.setLogger(debug.Debug('all'))

MibObject = collections.namedtuple('MibObject', ['mibName', 'objectType','objMib', 'valueFunc' ])

class SQLObject(object):

    def __init__(self):
        engine = create_engine('mysql+mysqlconnector://test:test123@localhost/bacula2', echo=True)

        # create a Session
        Session = sessionmaker(bind=engine)
        self.session = Session()
	self.nbClient = self.session.query(Client).count()

    def getClients(self):
	return self.session.query(Client)
    
    def getClient(self, clientId): 
       # querying for Client table
        client = self.session.query(Client).filter(Client.clientId == clientId).one()
	return client
        
    def getJobs(self, clientId):
	heure24 = datetime.datetime.now() - datetime.timedelta(1)
	print heure24
        return self.session.query(Job).filter(Job.clientId == clientId).filter(Job.endTime > heure24)

    #for client in clients2:
    #       print client.Job.name + " | " + client.Client.name + " | " + client.Client.uname  + " | " + client.Job.jobStatus

class Mib(object):
    """Stores the data we want to serve. 
    """

    def __init__(self):
	self.oid = (0, 0) # car c'est un tuple 
	self.flag = False

    def __init__(self):
        self._lock = threading.RLock()

    def getBaculaVersion(self):
        return "Version de Bacula"

    def getBaculaTotalClient(self):
	return self.sqlObject.nbClient

class MibClient(object):
    """Va contenir les fonctions et element pour la table clientError
    """

    def __init__(self ):
	self.oid = (0,0) # car c'est un tuple 
	self.flag = True 

    def getBaculaClientIndex(self):
	return self.oid[-1]

    def getBaculaClientName(self):
	clientId = self.oid[-1]
	name = self.sqlObject.getClient(clientId).name
        return name

    def getBaculaClientError(self):
	clientId = self.oid[-1]
        jobs = self.sqlObject.getJobs(clientId)
	for job in jobs:
	    import pdb ; pdb.set_trace()
	    if job.jobErrors == "1": 
	        return "1" 

        return "0"

    def getBaculaClientSizeBackup(self):
        clientId = self.oid[-1]
        jobs = self.sqlObject.getJobs(clientId)
	size = 0 
        for job in jobs:
	    size = size + job.jobBytes
        return size

    def getBaculaClientNumberFiles(self):
	clientId = self.oid[-1]
        jobs = self.sqlObject.getJobs(clientId)
        numberFiles = 0
        for job in jobs:
            numberFiles = numberFiles + job.jobFiles
        return numberFiles



def createVariable(SuperClass, objMib, getValue, *args):
    """This is going to create a instance variable that we can export. 
    getValue is a function to call to retreive the value of the scalar
    """
    """permet d'associer la fonction a l'oid defini dans la variable object  
    """

    class Var(SuperClass):
        def readGet(self, name, *args):
	    objMib.oid = name
	    
            return name, self.syntax.clone(getValue())
    return Var(*args) 

class SNMPAgent(object):
    """Implements an Agent that serves the custom MIB     
    """

    def __init__(self, mibObjects, sqlObject):
        """
        mibObjects - a list of MibObject tuples that this agent
        will serve
        """

        #each SNMP-based application has an engine
        self._snmpEngine = engine.SnmpEngine()

        #open a UDP socket to listen for snmp requests
        config.addSocketTransport(self._snmpEngine, udp.domainName,
                                  udp.UdpTransport().openServerMode(('', 161)))

        #add a v2 user with the community string public
        config.addV1System(self._snmpEngine, "agent", "public")
        #let anyone accessing 'public' read anything in the subtree below,
        #which is the enterprises subtree that we defined our MIB to be in
        config.addVacmUser(self._snmpEngine, 2, "agent", "noAuthNoPriv",
                           readSubTree=(1,3,6,1,4,1))

        #each app has one or more contexts
        self._snmpContext = context.SnmpContext(self._snmpEngine)

        #the builder is used to load mibs. tell it to look in the
        #current directory for our new MIB. We'll also use it to
        #export our symbols later
        mibBuilder = self._snmpContext.getMibInstrum().getMibBuilder()
        mibSources = mibBuilder.getMibSources() + (builder.DirMibSource(os.path.abspath('.')),)
        mibBuilder.setMibSources(*mibSources)

        #our variables will subclass this since we only have scalar types
        #can't load this type directly, need to import it
        MibScalarInstance, = mibBuilder.importSymbols('SNMPv2-SMI',
                                                      'MibScalarInstance')
        #export our custom mib
        for mibObject in mibObjects:
            nextVar, = mibBuilder.importSymbols(mibObject.mibName, mibObject.objectType)
	    """ cela va associer la fonction qui renvopi la valeur l'oid"""
            if mibObject.objMib.flag:
		#je suis une table
		
		for client in sqlObject.getClients():
#                    import pdb ; pdb.set_trace()
		    instance = createVariable(MibScalarInstance, mibObject.objMib, mibObject.valueFunc, nextVar.name,(client.clientId,), nextVar.syntax)
		    listName = list(nextVar.name)
		    listName.append(client.clientId)
		    newName = tuple(listName)
	    	    instanceDict = {str(newName)+"Instance":instance}
           	    mibBuilder.exportSymbols(mibObject.mibName, **instanceDict)

	    else :
		instance = createVariable(MibScalarInstance, mibObject.objMib, mibObject.valueFunc, nextVar.name,(0,), nextVar.syntax)
                                             #class         ,class with fonc , nom de la fonction , oid               , type d'oid

            	#need to export as <var name>Instance
	        instanceDict = {str(nextVar.name)+"Instance":instance}
	   	mibBuilder.exportSymbols(mibObject.mibName, **instanceDict)


        # tell pysnmp to respotd to get, getnext, and getbulk
        cmdrsp.GetCommandResponder(self._snmpEngine, self._snmpContext)
        cmdrsp.NextCommandResponder(self._snmpEngine, self._snmpContext)
        cmdrsp.BulkCommandResponder(self._snmpEngine, self._snmpContext)


    def serve_forever(self):
        print "Starting agent"
        self._snmpEngine.transportDispatcher.jobStarted(1)
        try:
           self._snmpEngine.transportDispatcher.runDispatcher()
        except:
            self._snmpEngine.transportDispatcher.closeDispatcher()
            raise

class Worker(threading.Thread):
    """Just to demonstrate updating the MIB
    and sending traps
    """

    def __init__(self, agent, mib):
        threading.Thread.__init__(self)
        self._agent = agent
        self._mib = mib
        self.setDaemon(True)


def main():
    sqlObject = SQLObject()
    mib = Mib()
    mib.flag = False
    mib.sqlObject = sqlObject
    mibClient = MibClient()
    mibClient.flag = True
    mibClient.sqlObject = sqlObject
    objects = [MibObject('AXIONE-MIB', 'baculaVersion', mib ,mib.getBaculaVersion),
               MibObject('AXIONE-MIB', 'baculaTotalClients', mib , mib.getBaculaTotalClient),
               MibObject('AXIONE-MIB', 'baculaClientIndex', mibClient , mibClient.getBaculaClientIndex),
               MibObject('AXIONE-MIB', 'baculaClientName', mibClient, mibClient.getBaculaClientName),
               MibObject('AXIONE-MIB', 'baculaClientError', mibClient, mibClient.getBaculaClientError),
               MibObject('AXIONE-MIB', 'baculaClientSizeBackup', mibClient, mibClient.getBaculaClientSizeBackup),
	       MibObject('AXIONE-MIB', 'baculaClientNumberFiles', mibClient, mibClient.getBaculaClientNumberFiles)]
    agent = SNMPAgent(objects, sqlObject)

    Worker(agent, mib).start()
    try:
        agent.serve_forever()
    except KeyboardInterrupt:
	sqlObject.session.close()
        print "Shutting down"

if __name__ == '__main__':
    main()
