#from sqlalchemy import create_engine, func 
from sqlalchemy import Column, Date, Integer, String, Binary
from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import relationship, backref, sessionmaker 
from sqlalchemy.dialects.mysql import BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

Base = declarative_base()
 
########################################################################
class BaseFiles(Base):
	""""""
	__tablename__ = "BaseFiles"
	
	baseId = Column(INTEGER(10, unsigned = True), primary_key = True)
	baseJobId = Column(INTEGER(10, unsigned = True))
	jobId = Column(INTEGER(10, unsigned = True))
	fileId = Column(BIGINT(20, unsigned = True))
	fileIndex = Column(INTEGER(10, unsigned = True))
	
	def __init__(self):
		""""""""
		
class Client(Base): #OK
	""""""
	__tablename__ = "Client"
 
	clientId = Column(INTEGER(10, unsigned = True), primary_key=True)
	name = Column(TINYBLOB) 
	uname = Column(TINYBLOB)
	autoPrune = Column(TINYINT(4))
	fileRetention = Column(BIGINT(20, unsigned = True))
	JobRetention = Column(BIGINT(20, unsigned = True)) 
	 
	def __init__(self, name):
		""""""
		self.name = name   
 
class File(Base): #OK
	""""""
	__tablename__ = "File"
	
	fileId = Column(BIGINT(20, unsigned = True), primary_key=True)
	fileIndex = Column(INTEGER(10, unsigned = True )) 
	jobId = Column(INTEGER(10, unsigned = True)) 
	pathId = Column(INTEGER(10, unsigned = True)) 
	filenameId = Column(INTEGER(10 , unsigned = True))
	deltaSeq = Column(SMALLINT(5 , unsigned = True))
	markId = Column(INTEGER(10 , unsigned = True)) 
	lStat = Column(TINYBLOB)
	md5 = Column(TINYBLOB)
	
	def __init__(self):
		""""""""

class Filename(Base): #OK
	""""""
	__tablename__ = "Filename"
	
	filenameId = Column(INTEGER(10, unsigned = True), primary_key=True)
	name = Column(BLOB)
	
	def __init__(self):
		""""""""
 
class FileSet(Base): #OK
	""""""
	__tablename__ = "FileSet"
	
	fileSetId = Column(INTEGER(10, unsigned = True), primary_key=True)
	fileSet = Column(TINYBLOB)
	md5 = Column(TINYBLOB)
	createTim = Column(DATETIME)
	
	def __init__(self):
		""""""""	
		
class Job(Base): #OK
	""""""
	__tablename__ = "Job"	
	
	jobId = Column(INTEGER(10, unsigned = True), primary_key = True)
	job = Column(TINYBLOB) 
	name = Column(TINYBLOB)
	type = Column(BINARY(1))
	level = Column(BINARY(1))
	clientId = Column(INTEGER(11))
	jobStatus = Column(BINARY(1))
	schedTime = Column(TIMESTAMP)
	startTime = Column(DATETIME)
	endTime = Column(DATETIME)
	realEndTime = Column(DATETIME)
	jobTDate = Column(BIGINT(20, unsigned = True))
	volSessionId = Column(INTEGER(10, unsigned = True))
	volSessionTime = Column(INTEGER(10, unsigned = True)) 
	jobFiles = Column(INTEGER(10, unsigned = True))
	jobBytes = Column(BIGINT(20, unsigned = True))
	readBytes = Column(BIGINT(20, unsigned = True))
	jobErrors = Column(INTEGER(10, unsigned = True))
	jobMissingFiles = Column(INTEGER(10, unsigned = True))
	poolId = Column(INTEGER(10, unsigned = True))
	fileSetId = Column(INTEGER(10, unsigned = True))
	priorJobId = Column(INTEGER(10, unsigned = True))
	purgedFiles = Column(TINYINT(4))
	hasBase = Column(TINYINT(4))
	hasCache = Column(TINYINT(4))
	reviewed = Column(TINYINT(4))
	comment = Column(BLOB)
	
	def __init__(self):
		""""""""
		
class JobMedia(Base): #OK
	""""""
	__tablename__ = "JobMedia"	

	jobMediaId = Column(INTEGER(10, unsigned = True),  primary_key = True)
	jobId = Column(INTEGER(10, unsigned = True))
	mediaId = Column(INTEGER(10, unsigned = True))
	firstIndex = Column(INTEGER(10, unsigned = True))
	lastIndex = Column(INTEGER(10, unsigned = True))
	startFile = Column(INTEGER(10, unsigned = True))
	endFile = Column(INTEGER(10, unsigned = True))
	startBlock = Column(INTEGER(10, unsigned = True))
	endBlock = Column(INTEGER(10, unsigned = True))
	volIndex = Column(INTEGER(10, unsigned = True))
	
	def __init__(self):
		""""""""	
		
class Log(Base): #OK
	""""""
	__tablename__ = "Log"	
	
	logId = Column(INTEGER(10, unsigned = True), primary_key = True)
	jobId = Column(INTEGER(10))
	time = Column(DATETIME)
	logText = Column(BLOB)
	
	
	def __init__(self):
		""""""""

class Media(Base): #OK
	""""""
	__tablename__ = "Media"	
	
	mediaId = Column(INTEGER(10, unsigned = True), primary_key = True)
	volumeName = Column(TINYBLOB)
	slot = Column(INTEGER(11))
	poolId = Column(INTEGER(10, unsigned = True))
	mediaType = Column(TINYBLOB)
	mediaTypeId = Column(INTEGER(10, unsigned = True))
	labelType = Column(TINYINT(4))
	firstWritten = Column(DATETIME)
	lastWritten = Column(DATETIME)
	labelDate = Column(DATETIME)
	volJobs = Column(INTEGER(10, unsigned = True))
	volFiles = Column(INTEGER(10, unsigned = True))
	volBlocks = Column(INTEGER(10, unsigned = True))
	volMounts = Column(INTEGER(10, unsigned = True))
	volBytes = Column(BIGINT(20, unsigned = True))
	volParts = Column(INTEGER(10, unsigned = True))
	volErrors = Column(INTEGER(10, unsigned = True))
	volWrites = Column(INTEGER(10, unsigned = True))
	volCapacityBytes = Column(BIGINT(20, unsigned = True))
	volStatus = Column('myStatus', ENUM('Full','Archive','Append','Recycle','Purged','Read-Only','Disabled','Error','Busy','Used','Cleaning'))
	enabled = Column(TINYINT(4))
	recycle = Column(TINYINT(4))
	actionOnPurge = Column(TINYINT(4))
	volRetention = Column(BIGINT(20, unsigned = True))
	volUseDuration = Column(BIGINT(20, unsigned = True))
	maxVolJobs = Column(INTEGER(10, unsigned = True))
	maxVolFiles  = Column(INTEGER(10, unsigned = True))
	maxVolBytes = Column(BIGINT(20, unsigned = True))
	inChanger = Column(TINYINT(4))
	storageId = Column(INTEGER(10, unsigned = True))
	deviceId = Column(INTEGER(10, unsigned = True))
	mediaAddressing = Column(TINYINT(4))
	volReadTime = Column(BIGINT(20, unsigned = True))
	volWriteTime = Column(BIGINT(20, unsigned = True))
	endFile = Column(INTEGER(10, unsigned = True))
	endBlock = Column(INTEGER(10, unsigned = True))
	locationId = Column(INTEGER(10, unsigned = True))
	recycleCount = Column(INTEGER(10, unsigned = True))
	initialWrite = Column(DATETIME)
	scratchPoolId = Column(INTEGER(10, unsigned = True))
	recyclePoolId = Column(INTEGER(10, unsigned = True))
	comment = Column(BLOB)
	
	def __init__(self):
		""""""""

class MediaType(Base): #OK
	""""""
	__tablename__ = "MediaType"	
	
	mediaTypeId = Column(INTEGER(10, unsigned = True), primary_key = True)
	mediaType = Column(TINYBLOB)
	readOnly = Column(TINYINT(4))
	
	def __init__(self):
		""""""""

class Path(Base): #OK
	""""""
	__tablename__ = "Path"
	
	pathId = Column(INTEGER(10, unsigned = True), primary_key = True)
	path = Column(BLOB)
	
	def __init__(self):
		""""""""
		
class Pool(Base): #OK
	""""""
	__tablename__ = "PoolId"	
	
	poolId = Column(INTEGER(10, unsigned = True), primary_key = True)
	name = Column(TINYBLOB)
	numVols = Column(INTEGER(10, unsigned = True))
	maxVols = Column(INTEGER(10, unsigned = True))
	useOnce  = Column(TINYINT(4))
	useCatalog = Column(TINYINT(4))
	acceptAnyVolume  = Column(TINYINT(4))
	volRetention = Column(BIGINT(20, unsigned = True))
	volUseDuration = Column(BIGINT(20, unsigned = True))
	maxVolJobs = Column(INTEGER(10, unsigned = True))
	maxVolFiles = Column(INTEGER(10, unsigned = True))
	maxVolBytes = Column(BIGINT(20, unsigned = True))
	autoPrune = Column(TINYINT(4))
	recycle = Column(TINYINT(4))
	actionOnPurge = Column(TINYINT(4))
	poolType = Column("myType",ENUM('Backup','Copy','Cloned','Archive','Migration','Scratch'))
	labelType = Column(TINYINT(4))
	labelFormat = Column(TINYBLOB)
	enabled = Column(TINYINT(4))
	scratchPoolId = Column(INTEGER(10, unsigned = True))
	recyclePoolId = Column(INTEGER(10, unsigned = True))
	nextPoolId = Column(INTEGER(10, unsigned = True))
	migrationHighBytes  = Column(BIGINT(20, unsigned = True))
	migrationLowBytes  = Column(BIGINT(20, unsigned = True))
	migrationTime  = Column(BIGINT(20, unsigned = True))
	
	def __init__(self):
		""""""""
		
class RestoreObject(Base): #OK
	""""""
	__tablename__ = "RestoreObject"	
	
	restoreObjectId = Column(INTEGER(10, unsigned = True), primary_key = True)
	objectName = Column(BLOB)
	restoreObject = Column(LONGBLOB)
	pluginName = Column(TINYBLOB)
	objectLength = Column(INTEGER(11))
	objectFullLength = Column(INTEGER(11))
	objectIndex = Column(INTEGER(11))
	objectType = Column(INTEGER(11))
	fileIndex = Column(INTEGER(10, unsigned = True))
	jobId = Column(INTEGER(10, unsigned = True))
	objectCompression = Column(INTEGER(11))
	
	def __init__(self):
		""""""""
	
class Status(Base): #OK
	""""""
	__tablename__ = "Status"
	
	jobStatus = Column(CHAR(1), primary_key = True)
	jobStatusLong = Column(BLOB)
	severity = Column(INTEGER(11))
	
	def __init__(self):
		""""""""
		
class Storage(Base): #OK
	""""""
	__tablename__ = "Storage"
	
	storageId = Column(INTEGER(10, unsigned = True), primary_key = True)
	name = Column(TINYBLOB)
	autoChanger = Column(TINYINT(4))
	
	def __init__(self):
		""""""""
		
########################################################################

#engine = create_engine('mysql+mysqlconnector://test:test123@localhost/bacula2', echo=True)
#Base = declarative_base()

# create a Session
#Session = sessionmaker(bind=engine)
#session = Session()
 
# querying for a record in the Client table
#clients = session.query(Job)
#clients2 = session.query(Job,Client).mon_filter(Job.clientId = Client.clientId)
#clients2 = session.query(Job,Client).filter(Job.clientId == Client.clientId)
#for client in clients2: 
#	print client.Job.name + " | " + client.Client.name + " | " + client.Client.uname  + " | " + client.Job.jobStatus

#client =  session.query(Client).filter(Client.clientId == "1").one()

#totalSizeBackup = session.query(func.sum(Job.jobBytes)).filter(Job.clientId == "4")
#import pdb ; pdb.set_trace()
#print totalSizeBackup

#session.close()

