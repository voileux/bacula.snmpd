from pysnmp.entity import engine, config
from pysnmp import debug
from pysnmp.entity.rfc3413 import cmdrsp, context, ntforg
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.smi import builder 

import os
import threading
import collections
import time

#can be useful
#debug.setLogger(debug.Debug('all'))

MibObject = collections.namedtuple('MibObject', ['mibName', 'objectType','flagTable', 'valueFunc' ])

class Mib(object):
    """Stores the data we want to serve. 
    """

    def __init__(self):
        self._lock = threading.RLock()

    def getBaculaVersion(self):
        return "Version de Bacula"

    def getBaculaTotalClient(self):
	return "10"


class MibClientError(object):
    """Va contenir les fonctions et element pour la table clientError
    """
    def setName(self,name):
	self.__name__= name

    def getBaculaClientsErrorIndex(self):
	return self.__name__[-1]

    def getBaculaClientErrorName(self):
        return "names_" + str(self.__name__[-1])



def createVariable(SuperClass, flagTable, getValue, *args):
    """This is going to create a instance variable that we can export. 
    getValue is a function to call to retreive the value of the scalar
    """
    """permet d'associer la fonction a l'oid defini dans la variable object  
    """

    class Var(SuperClass):
        def readGet(self, name, *args):
            print "readGet de Var est appele"
            return name, self.syntax.clone(getValue())

    class VarTable(SuperClass):
	def readGet(self, name, *args):
	    print "readGet de VarTable"
	    return name, self.syntax.clone(getValue())

    
    if flagTable:
	#je suis une table 
	return VarTable(*args)
    else :
	# je ne suis pas une table 
	return Var(*args)

def createVariable2(SuperClass, flagTable, objMibInstance, getValue, *args):

    class Var(SuperClass):
        def readGet(self, name, *args):
            print "readGet de Var est appele"
            return name, self.syntax.clone(getValue())

    class VarTable(SuperClass):
        def readGet(self, name, *args):
            print "readGet de VarTable"
	    objMibInstance.setName(name)
            return name, self.syntax.clone(getValue())


    if flagTable:
        #je suis une table 
        return VarTable(*args)
    else :
        # je ne suis pas une table 
        return Var(*args)



class SNMPAgent(object):
    """Implements an Agent that serves the custom MIB and
    can send a trap.
    """

    def __init__(self, mibObjects):
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
	    #import pdb ; pdb.set_trace()
	    """ cela va associer la fonction qui renvopi la valeur l'oid """
            if mibObject.flagTable:
		#je suis une table 
		for clientIndex in [0,1,3,56,87]:
		    instance = createVariable2(MibScalarInstance, mibObject.flagTable, mibClientError, mibObject.valueFunc, nextVar.name,(clientIndex,), nextVar.syntax)
		    listName = list(nextVar.name)
		    listName.append(clientIndex)
		    newName = tuple(listName)
	    	    instanceDict = {str(newName)+"Instance":instance}
#		    import pdb ; pdb.set_trace()
           	    mibBuilder.exportSymbols(mibObject.mibName, **instanceDict)

	    else :
		instance = createVariable(MibScalarInstance, mibObject.flagTable, mibObject.valueFunc, nextVar.name,(0,), nextVar.syntax)
                                             #class            ,flag si c une table  ,nom de la fonction , oid          , type d'oid

            	#need to export as <var name>Instance
	        instanceDict = {str(nextVar.name)+"Instance2":instance}
#n		import pdb ; pdb.set_trace()
	   	mibBuilder.exportSymbols(mibObject.mibName, **instanceDict)



#	(clientErrorIndex, clientErrorName) = mibBuilder.importSymbols('AXIONE-MIB' ,'clientErrorIndex', 'clientErrorName')
#	mibBuilder.exportSymbols(ClientErrorIndexInstance(MibScalarInstance, clientErrorIndex.getName(),0,clientErrorIndex.getSyntax()))
#	mibBuilder.exportSymbols(ClientErrorNameInstance(MibScalarInstance, clientErrorName.getName(),0,clientErrorName.getSyntax()))

	

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


# car mib et agent sont des variables globales 
mib = Mib()
mibClientError = MibClientError()
objects = [MibObject('AXIONE-MIB', 'baculaVersion', False ,mib.getBaculaVersion), 
	   MibObject('AXIONE-MIB', 'baculaTotalClients', False, mib.getBaculaTotalClient),
	   MibObject('AXIONE-MIB', 'baculaClientsErrorIndex', True  ,mibClientError.getBaculaClientsErrorIndex),
           MibObject('AXIONE-MIB', 'baculaClientErrorName', True, mibClientError.getBaculaClientErrorName)]
agent = SNMPAgent(objects)


def main():
#    objects = [MibObject('AXIONE-MIB', 'baculaVersion', mib.getBaculaVersion)]
    Worker(agent, mib).start()
    try:
        agent.serve_forever()
    except KeyboardInterrupt:
        print "Shutting down"

if __name__ == '__main__':
#    import pdb ; pdb.set_trace()
    main()
