import sys
import requests
import json
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urlparse import urljoin
import csv
import time

from cmd import Cmd

# Global variables
sess = None
baseurl = None
currentAccount = ''
promptText = '> '

CONST_EVENT_TEMPLATE = 'event-template.json'


def print_table(items, header=None, wrap=True, max_col_width=20, wrap_style="wrap", row_line=False, fix_col_width=False):
    ''' Prints a matrix of data as a human readable table. Matrix
    should be a list of lists containing any type of values that can
    be converted into text strings.

    Two different column adjustment methods are supported through
    the *wrap_style* argument:
    
       wrap: it will wrap values to fit max_col_width (by extending cell height)
       cut: it will strip values to max_col_width

    If the *wrap* argument is set to False, column widths are set to fit all
    values in each column.

    This code is free software. Updates can be found at
    https://gist.github.com/jhcepas/5884168
    
    '''
        
    if fix_col_width:
        c2maxw = dict([(i, max_col_width) for i in xrange(len(items[0]))])
        wrap = True
    elif not wrap:
        c2maxw = dict([(i, max([len(str(e[i])) for e in items])) for i in xrange(len(items[0]))])
    else:
        c2maxw = dict([(i, min(max_col_width, max([len(str(e[i])) for e in items])))
                        for i in xrange(len(items[0]))])
    if header:
        current_item = -1
        row = header
        if wrap and not fix_col_width:
            for col, maxw in c2maxw.iteritems():
                c2maxw[col] = max(maxw, len(header[col]))
                if wrap:
                    c2maxw[col] = min(c2maxw[col], max_col_width)
    else:
        current_item = 0
        row = items[current_item]
    while row:
        is_extra = False
        values = []
        extra_line = [""]*len(row)
        for col, val in enumerate(row):
            cwidth = c2maxw[col]
            wrap_width = cwidth
            val = str(val)
            try:
                newline_i = val.index("\n")
            except ValueError:
                pass
            else:
                wrap_width = min(newline_i+1, wrap_width)
                val = val.replace("\n", " ", 1)
            if wrap and len(val) > wrap_width:
                if wrap_style == "cut":
                    val = val[:wrap_width-1]+"+"
                elif wrap_style == "wrap":
                    extra_line[col] = val[wrap_width:]
                    val = val[:wrap_width]
            val = val.ljust(cwidth)
            values.append(val)
        print ' | '.join(values)
        if not set(extra_line) - set(['']):
            if header and current_item == -1:
                print ' | '.join(['='*c2maxw[col] for col in xrange(len(row)) ])
            current_item += 1
            try:
                row = items[current_item]
            except IndexError:
                row = None
        else:
            row = extra_line
            is_extra = True
 
        #if row_line and not is_extra and not (header and current_item == 0):
        #    if row:
        #        print ' | '.join(['-'*c2maxw[col] for col in xrange(len(row)) ])
        #    else:
        #        print ' | '.join(['='*c2maxw[col] for col in xrange(len(extra_line)) ])


class MyPrompt(Cmd):

    def emptyline(self):
         pass

    def updatePrompt(self):
        
        global currentAccount

        if (currentAccount != None and currentAccount != 'current-account'):
            promptText = currentAccount + '> '
        else:
            promptText = '> '

        self.prompt = promptText


    def createEvent(self, data):
        url_path = '/events/v2/' + currentAccount + '/events/'
        result = sess.post(urljoin(baseurl, url_path), json.dumps(data), headers={'Content-Type': 'application/json'})
        if (result.status_code == 200):
            j = result.json()
            print "Event '" + j["contents"]["name"] + "' successfully created with ID " + str(j["contents"]["id"]) + "."
        else:
            print 'ERROR: ' + str(result.status_code) + ' ' + result.reason




    def do_cd(self, args):

        global baseurl
        global sess
        global currentAccount

        if (args == '..'):
            currentAccount = 'current-account'
            self.updatePrompt()   
        else:
            if (args == ''):
                self.updatePrompt()
            else: 
                currentAccount = args
                self.updatePrompt()


    def do_get(self, args):
        """Retrieve an Event and displays its details.\nGet Event summary: get <Event ID>\nGet Event services: get <Event ID> services"""
        global baseurl
        global sess

        if (args != None):
            params = args.split(' ')

            # Show Event Summary
            if (len(params) == 1):
                url_path = '/events/v2/' + currentAccount + '/events/' + params[0]
                result = sess.get(urljoin(baseurl, url_path))
                if (result.status_code == 200):
                    print json.dumps(result.json(), sort_keys=True, indent=2, separators=(',', ': '))
                else:
                    print 'ERROR: ' + str(result.status_code) + ' ' + result.reason

            # Show Event Details
            if (len(params) == 2 and params[1] == "services"):
                url_path = '/events/v2/' + currentAccount + '/events/' + params[0] + '?services=detail'
                result = sess.get(urljoin(baseurl, url_path))
                if (result.status_code == 200):
                    print json.dumps(result.json(), sort_keys=True, indent=2, separators=(',', ': '))
                else:
                    print 'ERROR: ' + str(result.status_code) + ' ' + result.reason


    def do_create(self, args):
        """\nCreate a new Event based on a JSON file called 'event-template.json'.\n\ncreate <Event Name> <Start Time (in milliseconds)> <End Time (in milliseconds)>\n"""
        global baseurl
        global sess

        if (args != None):
            params = args.split(' ')

            # 
            if (len(params) == 3):

                eventName = params[0]
                startTime = params[1]
                endTime = params[2]

                with open(CONST_EVENT_TEMPLATE, "r") as read_file:
                    data = json.load(read_file)

                data["name"] = eventName
                data["start"] = startTime
                data["end"] = endTime

                self.createEvent(data)


    def do_createFromCsv(self, args):
        """\nCreate new Events based a CSV file. First column of the file should contain the event name, second column, the start time in milliseconds and third column, the end time in milliseconds.\n\nCreate multiple events: createFromCsv <CSV file name and path>\n"""
        if (args != None):
            params = args.split(' ')
            if (len(params) == 1):
                csvFile = params[0]
                with open(csvFile, 'rb') as csvfile:
                    csvReader = csv.reader(csvfile, delimiter=',')
                    for row in csvReader:

                        eventName = row[0]
                        startTime = row[1]
                        endTime = row[2]

                        with open(CONST_EVENT_TEMPLATE, "r") as read_file:
                            data = json.load(read_file)

                        data["name"] = eventName
                        data["start"] = startTime
                        data["end"] = endTime

                        print 'Creating event ' + eventName + ' ...'
                        self.createEvent(data)


    def do_ls(self, args):
        """\nList events in a given time range.\n\nEvents in a time range: ls <Start Range (in milliseconds)> <End Range (in milliseconds)>\nList events for the coming 30 days: ls\n"""
        global baseurl
        global sess
        eventTable = []

        if (args != None):
            params = args.split(' ')
            if (len(params) == 2):
                startRange = params[0]
                endRange = params[1]
                url_path = '/events/v2/' + currentAccount + '/events?startRange=' + startRange + '&endRange=' + endRange
                result = sess.get(urljoin(baseurl, url_path))
                if (result.status_code == 200):
                    j = result.json()
                    for event in j["contents"]["dataSet"]:
                        eventName = event["name"]
                        eventId = str(event["id"])
                        eventStart = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(event["start"]) / 1000))
                        eventEnd = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(event["end"]) / 1000))
                        eventTable.append([eventName, eventId, eventStart, eventEnd])
                    if (len(eventTable)>0):
                        print 
                        print_table(eventTable, 
                            header=[ "Event Name", "Event ID", "Start", "End"], 
                            wrap=True, max_col_width=40, 
                            wrap_style='wrap', row_line=True, fix_col_width=False)
                        print 

                else:
                    print 'ERROR: ' + str(result.status_code) + ' ' + result.reason
            else:
                ts = int(time.time()) * 1000
                startRange = str(ts)
                endRange = str(int(ts + 2592000000))
                url_path = '/events/v2/' + currentAccount + '/events?startRange=' + startRange + '&endRange=' + endRange
                result = sess.get(urljoin(baseurl, url_path))
                if (result.status_code == 200):
                    j = result.json()
                    for event in j["contents"]["dataSet"]:
                        eventName = event["name"]
                        eventId = str(event["id"])
                        eventStart = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(event["start"]) / 1000))
                        eventEnd = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(event["end"]) / 1000))
                        eventTable.append([eventName, eventId, eventStart, eventEnd])
                    if (len(eventTable)>0):
                        print 
                        print_table(eventTable, 
                            header=[ "Event Name", "Event ID", "Start", "End"], 
                            wrap=True, max_col_width=40, 
                            wrap_style='wrap', row_line=True, fix_col_width=False)
                        print 


                else:
                    print 'ERROR: ' + str(result.status_code) + ' ' + result.reason



    def do_rm(self, args):
        """\nDelete one or more Event: rm <Event ID> [<Envent ID>] ...\n"""
        global baseurl
        global sess

        if (args != None):
            params = args.split(' ')
            if (len(params) >= 1):
                for i in range(0, len(params)):
                    eventId = params[i]
                    print "Removing Event ID " + eventId + "..."
                    url_path = '/events/v2/' + currentAccount + '/events/' + eventId
                    result = sess.delete(urljoin(baseurl, url_path))
                    if (result.status_code == 200):
                        print "Event ID " + eventId + " successfully removed."
                    else:
                        print 'ERROR: ' + str(result.status_code) + ' ' + result.reason



    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."
        raise SystemExit

    def do_q(self, args):
        """Quits the program."""
        self.do_quit(args);



if __name__ == '__main__':

    # Initialize credentials for Akamai {OPEN} API
    edgerc = EdgeRc('.edgerc')
    section = sys.argv[1]
    baseurl = 'https://%s' % edgerc.get(section, 'host')
    sess = requests.Session()
    sess.auth = EdgeGridAuth.from_edgerc(edgerc, section)

    prompt = MyPrompt()
    prompt.prompt = promptText
    prompt.updatePrompt()
    prompt.intro = 'Welcome to CLI for Akamai Event Center'
    prompt.cmdloop('Starting prompt...')
