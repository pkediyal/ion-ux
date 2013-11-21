import threading
import sys
sys.path.append('.')
import unittest
#from nose.plugins.attrib import attr
import urllib

#@attr('INT')
class ERDDAPUnitTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def multithread_read(self):
        instances = 50
        threads = []
        url='http://r2-erddap-prod.oceanobservatories.org:8080/erddap/griddap/96f5f221e6a44a1d86502c310beeffbd.htmlTable?absolute_pressure[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],date_time_string[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],driver_timestamp[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],ingestion_timestamp[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],internal_timestamp[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],port_timestamp[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],preferred_timestamp[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],pressure_temp[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],sample_number[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],sample_type[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],seafloor_pressure[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)],time[(2013-11-19T22:27:10Z):1:(2013-11-21T17:49:05Z)]'
        print
        for instance in range(1,instances+1):
            thread = ThreadedRead(url, instance)
            #print '\n starting thread ... ' + str(instance)
            thread.start()
            threads.append(thread)
        print
        print '     TOTAL THREADS STARTED: ' +str(instance)
        print
        for instance in range(0,instances):
            threads[instance].join()

        print
        print '     TOTAL THREADS FINISHED: ' +str(instance+1)
        print



class ThreadedRead(threading.Thread):

    def __init__(self, url, thread_instance):
        threading.Thread.__init__(self)
        self.url = url
        self.thread_instance = str(thread_instance)

    def run(self):
        try:
            #print '\nthread ['+self.thread_instance + '] making request '
            f = urllib.urlopen(self.url)
            contents = f.read()
            self.length = len(contents)
            if len(contents) < 50000:
                print contents
            f.close()
            print '\nthread ['+self.thread_instance + '] retrieved ' + str(len(contents)) + ' bytes'

        except IOError:
            print "Could not open document: %s" % self.url

    def get_results(self):
        return self.length

if __name__ == '__main__':
    unittest.main()