import sys
import requests
import json
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urlparse import urljoin
import csv


from cmd import Cmd

# Global variables
sess = None
baseurl = None
currentAccount = 'current-account'
promptText = '> '

CONST_EVENT_TEMPLATE = 'event-template.json'




class MyPrompt(Cmd):

    def emptyline(self):
         pass

    def updatePrompt(self):
        
        global currentAccount

        if (currentAccount != None):
            promptText = currentAccount + '> '
        else:
            promptText = '> '

        self.prompt = promptText


    def createEvent(self, data):
        url_path = '/events/v2/' + currentAccount + '/events/'
        result = sess.post(urljoin(baseurl, url_path), json.dumps(data), headers={'Content-Type': 'application/json'})
        if (result.status_code == 200):
            print json.dumps(result.json(), sort_keys=True, indent=2, separators=(',', ': '))
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
        """\nList all events in a given time range.\n\nls <Start Range (in milliseconds)> <End Range (in milliseconds)>\n"""
        global baseurl
        global sess

        if (args != None):
            params = args.split(' ')
            if (len(params) == 2):

                startRange = params[0]
                endRange = params[1]
                url_path = '/events/v2/' + currentAccount + '/events?startRange=' + startRange + '&endRange=' + endRange
                result = sess.get(urljoin(baseurl, url_path))
                if (result.status_code == 200):
                    print json.dumps(result.json(), sort_keys=True, indent=2, separators=(',', ': '))
                else:
                    print 'ERROR: ' + str(result.status_code) + ' ' + result.reason



    def do_rm(self, args):
        """\nDelete an Event: rm <Event ID>\n"""
        global baseurl
        global sess

        if (args != None):
            params = args.split(' ')
            if (len(params) == 1):
                eventId = params[0]
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
