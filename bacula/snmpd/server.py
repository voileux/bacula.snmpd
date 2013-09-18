from pysnmp.entity import engine, config
from pysnmp import debug
from pysnmp.entity.rfc3413 import cmdrsp, context, ntforg
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.smi import builder 

from bacula.snmpd.utils import getdefaults

import MySQLdb as mdb
import os
import threading
import collections
import time
import datetime

#can be useful
#debug.setLogger(debug.Debug('all'))

MibObject = collections.namedtuple('MibObject', ['mibName', 'objectType','objMib', 'valueFunc' ])

class SQLObject(object):
    """ Class of managed SQL's interaction.
	contains connexion to SQL server and query to BDD 
    """

    def __init__(self, paramsDict):
    	con = mdb.connect(paramsDict['server'], paramsDict['user'], paramsDict['password'] ,paramsDict['database'])
	self.cur = con.cursor(mdb.cursors.DictCursor)
	self.cur.execute("SELECT count(*) as nbClient FROM Client")
	
	result = self.cur.fetchone()
	self.nbClient = result['nbClient'] #because it's a Dict with header

    def getClientsId(self):
	"""A list of Clients.
	   return the Client list 
        """
	self.cur.execute("SELECT ClientId FROM Client")
	return self.cur.fetchall()
    
    def getClient(self, clientId):
	"""A Bacula Client.
           return a definition of a bacula Client 
	"""
	self.cur.execute("SELECT * from Client WHERE ClientId =" + str(clientId) )
	return self.cur.fetchone()

 
    def getJobs24H(self, clientId):
	heure24 = datetime.datetime.now() - datetime.timedelta(1)
	self.cur.execute("SELECT * FROM Job WHERE ClientId="+ str(clientId) + " AND EndTime>'" + str(heure24) + "'" )
	
	return self.cur.fetchall()


    def getTotalSizeBackup(self, clientId):
	self.cur.execute("SELECT sum(JobBytes) as totalSizeBackup FROM Job WHERE ClientId =" + str(clientId) )
	totalSizeBackup = self.cur.fetchone()['totalSizeBackup']
	if not totalSizeBackup:
		totalSizeBackup = 0
	return totalSizeBackup/(1024*1024)

    def getSizeBackup24H(self, clientId):
	heure24 = datetime.datetime.now() - datetime.timedelta(1)
	self.cur.execute("SELECT sum(JobBytes) as sizeBackup24h FROM Job WHERE ClientId =" + str(clientId) +" AND EndTime>'" + str(heure24) + "'" )
	sizeBackup24h  = self.cur.fetchone()['sizeBackup24h']
	if not sizeBackup24h:
		sizeBackup24h = 0
	return sizeBackup24h/(1024*1024)

    def getTotalNumberFiles(self, clientId):
	self.cur.execute("SELECT sum(JobFiles) as totalNumberFiles FROM Job WHERE ClientId =" + str(clientId) )
	totalNumberFiles  = self.cur.fetchone()['totalNumberFiles']
	if not totalNumberFiles:
		totalNumberFiles = 0
	return totalNumberFiles

    def getNumberFiles24H(self, clientId):
	heure24 = datetime.datetime.now() - datetime.timedelta(1)
	self.cur.execute("SELECT sum(JobFiles) as numberFiles24H FROM Job WHERE ClientId =" + str(clientId) +" AND EndTime>'" + str(heure24) + "'" )
	numberFiles24H  = self.cur.fetchone()['numberFiles24H']
	if not numberFiles24H:
		numberFiles24H = 0 
	return numberFiles24H


class Mib(object):
    """ Class of simple oid : baculaVersion and baculaTotalClients.
        Stores the fonction we want to serve this oid . 
    """

    def __init__(self):
	self.oid = (0, 0) # because it's a tuple 
	self.flag = False

    def __init__(self):
        self._lock = threading.RLock()

    def getBaculaVersion(self):
        return "Bacula Version"

    def getBaculaTotalClient(self):
	return self.sqlObject.nbClient


class MibClient(object):
    """Content of BaculaClientTable.
    """

    def __init__(self ):
	self.oid = (0,0) # because it's a tuple 
	self.flag = True 

    def getBaculaClientIndex(self):
	return self.oid[-1]

    def getBaculaClientName(self):
	clientId = self.oid[-1]
	name = self.sqlObject.getClient(clientId)['Name']
        return name

    def getBaculaClientError(self):
	clientId = self.oid[-1]
        jobs = self.sqlObject.getJobs24H(clientId)
	if len(jobs) == 0: 
	    return "1"

	for job in jobs:
	    if job['JobErrors'] == 1: 
	        return "1" 

        return "0"

    def getBaculaClientSizeBackup(self):
        clientId = self.oid[-1]
        return self.sqlObject.getSizeBackup24H(clientId)

    def getBaculaClientTotalSizeBackup(self):
	clientId = self.oid[-1]
        return self.sqlObject.getTotalSizeBackup(clientId)

    def getBaculaClientNumberFiles(self):
        clientId = self.oid[-1]
        return self.sqlObject.getNumberFiles24H(clientId)

    def getBaculaClientTotalNumberFiles(self):
        clientId = self.oid[-1]
        return self.sqlObject.getTotalNumberFiles(clientId)
	

def createVariable(SuperClass, objMib, getValue, *args):
    """This is going to create a instance variable that we can export. 
    getValue is a function to call to retreive the value of the scalar
    """

    class Var(SuperClass):
        def readGet(self, name, *args):
	    objMib.oid = name
	    
            return name, self.syntax.clone(getValue())
    return Var(*args) 

class SNMPAgent(object):
    """Implements an Agent that serves the custom MIB     
    """

    def __init__(self, mibObjects, sqlObject, _rootDir):
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
        mibSources = mibBuilder.getMibSources() + (builder.DirMibSource(os.path.join(_rootDir, 'src/lib_mib_py')),)
        mibBuilder.setMibSources(*mibSources)

        #our variables will subclass this since we only have scalar types
        #can't load this type directly, need to import it
        MibScalarInstance, = mibBuilder.importSymbols('SNMPv2-SMI',
                                                      'MibScalarInstance')
        #export our custom mib
        for mibObject in mibObjects:
            nextVar, = mibBuilder.importSymbols(mibObject.mibName, mibObject.objectType)
            if mibObject.objMib.flag:
		#je suis une table
		
		for client in sqlObject.getClientsId():
		    instance = createVariable(MibScalarInstance, mibObject.objMib, mibObject.valueFunc, nextVar.name,(client['ClientId'],), nextVar.syntax)
		    listName = list(nextVar.name)
		    listName.append(client['ClientId'] )
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
    pathTest, null = os.path.split(os.path.abspath(__file__))
#   /home/simon/paulla/snmpd-server/src/bacula.snmpd/bacula/snmpd/server.py
    pathTest, null  = os.path.split(pathTest)
    pathTest, null  = os.path.split(pathTest)
    pathTest, null  = os.path.split(pathTest)
    _rootDir, null  = os.path.split(pathTest)
#    /home/simon/paulla/snmpd-server/src
    options = getdefaults('BDD', _rootDir)
    sqlObject = SQLObject(options)
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
               MibObject('AXIONE-MIB', 'baculaClientTotalSizeBackup', mibClient, mibClient.getBaculaClientTotalSizeBackup),
	       MibObject('AXIONE-MIB', 'baculaClientNumberFiles', mibClient, mibClient.getBaculaClientNumberFiles),
	       MibObject('AXIONE-MIB', 'baculaClientTotalNumberFiles', mibClient, mibClient.getBaculaClientTotalNumberFiles)]
    agent = SNMPAgent(objects, sqlObject, _rootDir)

    Worker(agent, mib).start()
    try:
        agent.serve_forever()
    except KeyboardInterrupt:
        print "Shutting down"

if __name__ == '__main__':
    main()
