from pysnmp.entity import engine, config
from pysnmp import debug
from pysnmp.entity.rfc3413 import cmdrsp, context, ntforg
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.smi import builder 

from bacula.snmpd.utils import getdefaults, print_log

import traceback as trbk
import MySQLdb as mdb
import os
import threading
import collections
import time
import datetime

import sys

import logging
import inspect

#can be useful
#debug.setLogger(debug.Debug('all'))

MibObject = collections.namedtuple('MibObject', ['mibName', 'objectType','objMib', 'valueFunc' ])
nb_sql_requete = 0

class SQLObject(object):
    """ Class of managed SQL's interaction.
	contains connexion to SQL server and query to BDD 
    """

    def __init__(self, paramsDict):
	txt  = " Start Connexion to BDD (server = " + paramsDict['server'] + "database = " + paramsDict['database'] +", user = " + paramsDict['user'] + ", password = " + paramsDict['password'] 
        print_log('debug', self.__class__.__name__ +"."+ inspect.stack()[0][3], msg = txt  )
    	
	self.con = mdb.connect(paramsDict['server'], paramsDict['user'], paramsDict['password'] ,paramsDict['database'])
	self.cur = self.con.cursor(mdb.cursors.DictCursor)
        
	query = "SELECT count(*) as nbClient FROM Client"
	self.cur.execute(query)
	print_log('debug', self.__class__.__name__ + "." + inspect.stack()[0][3], query = query) 
	
	global nb_sql_requete 
	nb_sql_requete = nb_sql_requete + 1
	print_log('debug',self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)
	
	result = self.cur.fetchone()
	self.nbClient = result['nbClient'] #because it's a Dict

    def getClientsId(self):
	"""A list of Clients.
	   return the Client list 
        """
	try: 
	    self.con.ping()
	    query = "SELECT ClientId FROM Client"
	    self.cur.execute(query)
	    print_log('debug' ,self.__class__.__name__ + "." + inspect.stack()[0][3] , query = query)
	
	    global nb_sql_requete 
	    nb_sql_requete = nb_sql_requete + 1
	    print_log('debug' , self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)
	
	except mdb.ProgrammingError:
	    print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , ProgrammingError = str(trbk.print_exc()))
	    print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , nb_sql_requete = nb_sql_requete)
	  
	except:
	    print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(trbk.print_exc()))
	    print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(sys.exc_info()[0]))
	    print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  nb_sql_requete =  nb_sql_requete) 
	
	return self.cur.fetchall()
    
    def getClient(self, clientId):
	"""A Bacula Client.
           return a definition of a bacula Client 
	"""
	try:
    	    self.con.ping()
	    query = "SELECT * from Client WHERE ClientId =" + str(clientId) 
	    self.cur.execute(query)
	    print_log('debug',self.__class__.__name__ + "." + inspect.stack()[0][3] , query = query)

	    global nb_sql_requete 
	    nb_sql_requete = nb_sql_requete + 1
	    print_log('debug' , self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)
	
	except mdb.ProgrammingError:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , ProgrammingError = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , nb_sql_requete = nb_sql_requete)

        except:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(sys.exc_info()[0]))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  nb_sql_requete =  nb_sql_requete)

	return self.cur.fetchone()

 
    def getJobs24H(self):
	""" A list of last 24h Bacula Job for all clients
	   return the last 24h job for all clients 
	"""
	heure24 = datetime.datetime.now() - datetime.timedelta(1)
	try:
 	    self.con.ping()
	    query = "SELECT ClientId, JobErrors  FROM Job  WHERE EndTime>'" + str(heure24) + "'"
	    self.cur.execute(query)
	    print_log('debug',self.__class__.__name__ + "." + inspect.stack()[0][3] , query = query)
	    
	    global nb_sql_requete 
	    nb_sql_requete = nb_sql_requete + 1
            print_log('debug' , self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)
 
	except mdb.ProgrammingError:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , ProgrammingError = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , nb_sql_requete = nb_sql_requete)

        except:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(sys.exc_info()[0]))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  nb_sql_requete =  nb_sql_requete)
    
	return self.cur.fetchall()


    def getClientJobs24H(self , clientId):
        """ A list of last 24h Bacula Job for all clients
           return the last 24h job for all clients 
        """
        heure24 = datetime.datetime.now() - datetime.timedelta(1)
        try:
            self.con.ping()
	    query = "SELECT ClientId, JobErrors  FROM Job  WHERE ClientId = '" + str(clientId) + "'AND  EndTime>'" + str(heure24) + "'"
            self.cur.execute(query)
	    print_log('debug',self.__class__.__name__ + "." + inspect.stack()[0][3] , query = query) 
            
	    global nb_sql_requete
            nb_sql_requete = nb_sql_requete + 1
	    print_log('debug' , self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)

        except mdb.ProgrammingError:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , ProgrammingError = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , nb_sql_requete = nb_sql_requete)

        except:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(sys.exc_info()[0]))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  nb_sql_requete =  nb_sql_requete)

        return self.cur.fetchall()


    def getTotalSizeBackup(self, clientId):
	try:
	    self.con.ping()
	    query = "SELECT sum(JobBytes) as totalSizeBackup FROM Job WHERE ClientId =" + str(clientId)
	    self.cur.execute(query)
            print_log('debug',self.__class__.__name__ + "." + inspect.stack()[0][3] , query = query)
	    
	    totalSizeBackup = self.cur.fetchone()['totalSizeBackup']
	    global nb_sql_requete 
	    nb_sql_requete = nb_sql_requete + 1
	    print_log('debug' , self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)

	    if not totalSizeBackup:
                totalSizeBackup = 0

	except mdb.ProgrammingError:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , ProgrammingError = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , nb_sql_requete = nb_sql_requete)

        except:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(sys.exc_info()[0]))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  nb_sql_requete =  nb_sql_requete)

	return totalSizeBackup/(1024*1024)

    def getSizeBackup24H(self, clientId):
	heure24 = datetime.datetime.now() - datetime.timedelta(1)
	try:
	    self.con.ping()
	    query = "SELECT sum(JobBytes) as sizeBackup24h FROM Job WHERE ClientId =" + str(clientId) +" AND EndTime>'" + str(heure24) + "'" 
	    self.cur.execute(query)
	    print_log('debug',self.__class__.__name__ + "." + inspect.stack()[0][3] , query = query)

	    sizeBackup24h  = self.cur.fetchone()['sizeBackup24h']
	    
            global nb_sql_requete 
	    nb_sql_requete = nb_sql_requete + 1
	    print_log('debug' , self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)
	    
	    if not sizeBackup24h:
	        sizeBackup24h = 0

	except mdb.ProgrammingError:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , ProgrammingError = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , nb_sql_requete = nb_sql_requete)

        except:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(sys.exc_info()[0]))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  nb_sql_requete =  nb_sql_requete)

	return sizeBackup24h/(1024*1024)

    def getTotalNumberFiles(self, clientId):
	try:
	    self.con.ping()
	    query = "SELECT sum(JobFiles) as totalNumberFiles FROM Job WHERE ClientId =" + str(clientId)
	    self.cur.execute(query ) 
	    print_log('debug',self.__class__.__name__ + "." + inspect.stack()[0][3] , query = query)

	    totalNumberFiles  = self.cur.fetchone()['totalNumberFiles']

	    global nb_sql_requete 
	    nb_sql_requete = nb_sql_requete + 1
            print_log('debug' , self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)
 
	    if not totalNumberFiles:
		totalNumberFiles = 0
	
	except mdb.ProgrammingError:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , ProgrammingError = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , nb_sql_requete = nb_sql_requete)

        except:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(sys.exc_info()[0]))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  nb_sql_requete =  nb_sql_requete)

	return totalNumberFiles

    def getNumberFiles24H(self, clientId):
	heure24 = datetime.datetime.now() - datetime.timedelta(1)
	try:
	    self.con.ping()
	    query = "SELECT sum(JobFiles) as numberFiles24H FROM Job WHERE ClientId =" + str(clientId) +" AND EndTime>'" + str(heure24) + "'"
	    self.cur.execute(query )
	    print_log('debug',self.__class__.__name__ + "." + inspect.stack()[0][3] , query = query)

	    numberFiles24H  = self.cur.fetchone()['numberFiles24H']
	    global nb_sql_requete 
	    nb_sql_requete = nb_sql_requete + 1
	    print_log('debug' , self.__class__.__name__ + "." + inspect.stack()[0][3], nb_sql_requete = nb_sql_requete)

	    if not numberFiles24H:
		numberFiles24H = 0 
	except mdb.ProgrammingError:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , ProgrammingError = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3] , nb_sql_requete = nb_sql_requete)

        except:
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(trbk.print_exc()))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  Unexpected_Error = str(sys.exc_info()[0]))
            print_log('warning', self.__class__.__name__ + "." + inspect.stack()[0][3],  nb_sql_requete =  nb_sql_requete)

	return numberFiles24H

    def clientInError(self, clientId):
	jobs = self.getClientJobs24H(clientId)
        if len(jobs) == 0:
            return "1"

        for job in jobs:
            if job['JobErrors'] == 1:
                return "1"

        return "0"



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

    def getBaculaTotalClientError(self):
	clientIds = self.sqlObject.getClientsId()
	totalClientError = 0
	for clientId in clientIds:
	    totalClientError = totalClientError + int(self.sqlObject.clientInError(clientId['ClientId']))
	
	return totalClientError 
	    


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
        return  self.sqlObject.clientInError(clientId)

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

    def __init__(self, mibObjects, sqlObject, _rootDir, server_options):
        """
        mibObjects - a list of MibObject tuples that this agent
        will serve
        """
        #each SNMP-based application has an engine
        self._snmpEngine = engine.SnmpEngine()

        #open a UDP socket to listen for snmp requests
        config.addSocketTransport(self._snmpEngine, udp.domainName,
                                  udp.UdpTransport().openServerMode(('', int(server_options['port']))))

        #add a v2 user with the community string public
        config.addV1System(self._snmpEngine, "agent", server_options['community'])
        #let anyone accessing 'public' read anything in the subtree below,
        #which is the enterprises subtree that we defined our MIB to be in
        config.addVacmUser(self._snmpEngine, int(server_options['version']), "agent", "noAuthNoPriv", readSubTree=(1,3,6,1,4,1))

        #each app has one or more contexts
        self._snmpContext = context.SnmpContext(self._snmpEngine)

        #the builder is used to load mibs. tell it to look in the
        #current directory for our new MIB. We'll also use it to
        #export our symbols later
        mibBuilder = self._snmpContext.getMibInstrum().getMibBuilder()
        mibSources = mibBuilder.getMibSources() + (builder.DirMibSource(os.path.join(_rootDir, 'lib_mib_py')),)
        mibBuilder.setMibSources(*mibSources)

        #our variables will subclass this since we only have scalar types
        #can't load this type directly, need to import it
        MibScalarInstance, = mibBuilder.importSymbols('SNMPv2-SMI', 'MibScalarInstance')

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
        logging.info("Starting Agent")
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
    nb_sql_requete = 0
    pathTest, null = os.path.split(os.path.abspath(__file__))
#    /home/simon/paulla/snmpd-server/src/bacula.snmpd/bacula/snmpd/server.py
    pathTest, null  = os.path.split(pathTest)
    _rootDir_pkg, null  = os.path.split(pathTest)
    _rootDir, null  = os.path.split(_rootDir_pkg)
    _rootDir, null  = os.path.split(_rootDir)
#    /home/simon/paulla/snmpd-server/src/bacula.snmpd
    bdd_options = getdefaults('BDD', _rootDir)
    mib_options = getdefaults('MIBS', _rootDir)
    server_options = getdefaults('SERVER', _rootDir)
    log_options = getdefaults('LOG', _rootDir)
    if log_options['level'] == "DEBUG":
	log_options['level'] = logging.DEBUG
    
    logging.basicConfig(filename=log_options['file'], level=log_options['level'], format='%(asctime)s | %(levelname)s:%(message)s', datfmt='%d/%m/%y %H:%M:%S' )
    logging.info("Daemon Started") 

    mib_name = mib_options['name']
    sqlObject = SQLObject(bdd_options)
    mib = Mib()
    mib.flag = False
    mib.sqlObject = sqlObject
    mibClient = MibClient()
    mibClient.flag = True
    mibClient.sqlObject = sqlObject
    objects = [MibObject(mib_name, 'baculaVersion', mib ,mib.getBaculaVersion),
               MibObject(mib_name, 'baculaTotalClients', mib , mib.getBaculaTotalClient),
               MibObject(mib_name, 'baculaTotalClientsErrors', mib , mib.getBaculaTotalClientError),
               MibObject(mib_name, 'baculaClientIndex', mibClient , mibClient.getBaculaClientIndex),
               MibObject(mib_name, 'baculaClientName', mibClient, mibClient.getBaculaClientName),
               MibObject(mib_name, 'baculaClientError', mibClient, mibClient.getBaculaClientError),
               MibObject(mib_name, 'baculaClientSizeBackup', mibClient, mibClient.getBaculaClientSizeBackup),
               MibObject(mib_name, 'baculaClientTotalSizeBackup', mibClient, mibClient.getBaculaClientTotalSizeBackup),
	       MibObject(mib_name, 'baculaClientNumberFiles', mibClient, mibClient.getBaculaClientNumberFiles),
	       MibObject(mib_name, 'baculaClientTotalNumberFiles', mibClient, mibClient.getBaculaClientTotalNumberFiles)]
    agent = SNMPAgent(objects, sqlObject, _rootDir_pkg, server_options)

    Worker(agent, mib).start()
    try:
        agent.serve_forever()
    except KeyboardInterrupt:
        print "Shutting down"

if __name__ == '__main__':
    main()
