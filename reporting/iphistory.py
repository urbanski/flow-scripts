#!/usr/bin/python
import tempfile
import shutil
import os
import sys
import subprocess
import shlex
import locale
from optparse import OptionParser
from datetime import date
from dateutil.rrule import rrule, DAILY
from subprocess import Popen, PIPE

def check_options(options, args):
	global ip_address
	global destination_dir
	#todo: preg-match start and end dates
	if(len(args) == 0):
		return False
	elif(len(args)==2):
		ip_address = args[0]
		destination_dir = args[1]
		
		#todo: validate IP address format
		
		#validate output directory
		if (os.path.exists(destination_dir) == False):
			os.mkdir(destination_dir)
		
		
		return True
	else:
		return False
	
def get_datastore_size(datastore_path):
	process = Popen(["du", "-sL", datastore_path], stdout=PIPE)
	exit_code = os.waitpid(process.pid, 0)
	output = process.communicate()[0]
	return int(output.split("	")[0])

def estimate_runtime(datastore_size):
	SECONDS_PER_B = 0.000032856
	return number_format((datastore_size * SECONDS_PER_B)/60,2)

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)

def number_format(num, places=0):
    return locale.format("%.*f", (places, num), True)


#APPLICATION ENTRYPOINT
##########################

#constants
DATA_SOURCE="/opt/flows/data"
destination_dir = ""
ip_address = ""

#set locale
locale.setlocale(locale.LC_NUMERIC, '')

#setup command line options
usage = "usage: %prog [options] <IP Address> <output directory>"
parser = OptionParser(usage)
parser.add_option("-s", "--start",dest="start", help="start date (yyyy-mm-dd)")
parser.add_option("-e", "--end",dest="end",help="end date (yyyy-mm-dd)")

(options, args) = parser.parse_args()


#verify that those options have been met
if (check_options(options, args) == False):
	print "Missing required arguments."
	parser.print_help()
	sys.exit(-1)


#we are ready for takeoff
temp_dir = tempfile.mkdtemp()
#print "Temporary directory is %s" % temp_dir

#determine the date ranges first
bDateRange = False
bSingleDate = False
if (options.start == None and options.end == None):
	#no start or end date...query all availible data.
	source_dir = DATA_SOURCE
	target_date_string = "All availible"
elif (options.start != None and options.end == None):
	#only one day
	bDateRange = True
	bSingleDate = True
	target_date_string = options.start
else:
	#multiple day(s)
	bDateRange = True
	bSingleDate = False
	target_date_string = "%s -> %s" % (options.start, options.end)
	
#setup symlinks
if (bDateRange == True and bSingleDate == False):
	#create a sources directory
	source_dir = "%s/src" % temp_dir
	os.mkdir(source_dir)

	#build date containers
	start_split = options.start.split('-')
	end_split = options.end.split('-')
	
	a = date(int(start_split[0]),int(start_split[1]),int(start_split[2]))
	b = date(int(end_split[0]),int(end_split[1]),int(end_split[2]))

	#date range start->end
	for dt in rrule(DAILY, dtstart=a, until=b):
		#print dt.strftime("%Y-%m-%d")
		temp_link_date=dt.strftime("%Y-%m-%d")
		link_source = "%s/%s/lts" % (DATA_SOURCE, temp_link_date)
		link_name = "%s/src/%s" % (temp_dir, temp_link_date)
		os.symlink(link_source, link_name)
elif (bDateRange == True and bSingleDate == True):
	#single date search
	source_dir = "%s/%s/" % (DATA_SOURCE, options.start)

#start argus
#print "Source dir: %s" % source_dir
#print "starting argus"

output_file = "%s/%s.ra" % (temp_dir,ip_address)


#determine datastore size and estimated runtime
ds_size = get_datastore_size(source_dir);
source_dir = "%s/*" % source_dir

#print a summary before we actually start the job
print "Job Summary"
print "--------------"
print "Target: %s" % ip_address
print "Date Range(s): %s " % target_date_string
print "Datastore size: %s bytes" % number_format(ds_size,0)
print "Est. Runtime: ~%s minutes" % estimate_runtime(ds_size)
print "Output file: %s/%s.ra" % (destination_dir, ip_address)
print ""

#get confirmation
confirmation = raw_input("Is this information correct? y/n:")
while (confirmation != 'y' and confirmation != 'n'):
	confirmation = raw_input("Is this information correct? y/n:")

if (confirmation == "n"):
	sys.exit(0)

command_line = "time /usr/local/bin/ra -R %s -w %s - host %s" % (source_dir, output_file, args[0])
print command_line
print "Running Argus, please wait..."
print os.system(command_line)
#args = shlex.split(command_line)
#p = subprocess.Popen(args)
shutil.copy(output_file, destination_dir)

#clean up temp directory
shutil.rmtree(temp_dir)
