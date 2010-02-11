#!/usr/bin/python
import re
import sys 
import cgi

class ApacheLogLine:
  """A Python class whose attributes are the fields of Apache log line.

  Designed specifically with combined format access logs in mind.  For
  example, the log line

  127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"

  would have the following field values as an ApacheLogLine:

  ip = '127.0.0.1'
  ident = '-'
  http_user = 'frank'
  time = '10/Oct/2000:13:55:36 -0700'
  request_line = 'GET /apache_pb.gif HTTP/1.0'
  http_response_code = '200'
  http_response_size = 2326
  referrer = 'http://www.example.com/start.html'
  user_agent = 'Mozilla/4.08 [en] (Win98; I ;Nav)'

  Typically you would only read from instances of ApacheLogLine.  Some other
  code, e.g., that in ApacheLogFile._ApacheLogFileGenerator, should be relied
  upon to parse the log lines and instantiate appropriate ApacheLogLine 
  instances.
  """

  def __init__(self, ip, id, hu, t, rl, hrc, hrs, r, ua): 
    self.ip = ip
    self.ident = id
    self.http_user = hu
    self.time = t
    self.request_line = rl
    self.http_response_code = hrc
    self.http_response_size = hrs
    self.referrer = r
    self.user_agent = ua

  def __str__(self):
    """Return a simple string representation of an ApacheLogLine."""
    return ','.join([self.ip, self.ident, self.time, self.request_line,
        self.http_response_code, self.http_response_size, self.referrer,
        self.user_agent])

class ApacheLogLineParser:
  def __init__(self):
    # We only compile the regular expression which handles the log line
    # parsing once per pass over the file, i.e., when client code asks for
    # an iterator.
    self.r = re.compile(r'(\d+\.\d+\.\d+\.\d+) (.*) (.*) \[(.*)\] "(.*)" (\d+) (.*) "(.*)" "(.*)"')
  
  def parse(self,line):
    m = self.r.match(line)
    if m:
      log_line = ApacheLogLine(m.group(1), m.group(2), m.group(3),
                               m.group(4), m.group(5), m.group(6), m.group(7), m.group(8),
                               m.group(9))
      return log_line


def getId(data):
    """
    This gets Auxilary ID from Cookie Data stored in logs
    """
    for eachString in data.split():
        if(eachString.find("Apache") != -1):
            return eachString[eachString.find("=")+1:].replace(";","")

        if(eachString.find("Adserver") != -1):
            return eachString[eachString.find("=")+1:].replace(";","")

    return "-" 
def validateClickEvent(data):
    """
    This function is used to validate click event
    """
    return data.has_key("utm_source")
    

def validParamsRec(data):
  """
  This functions makes sure that we have a valid click URL
  """
  keys = ['utm_source','utm_medium','utm_campaign','utm_content']
  
  for eachKey in keys:
    if(data.has_key(eachKey) == False):
      return False

  return True 

def getUrlParams(data):
    """
    This function is used to get URL params data
    """
    if(data.find("?") != -1):
        data = data[data.find("?")+1:]
        params = cgi.parse_qs(data)

        #Flatten the list stored as value (v) for given key (k)
        for k,v in params.items():
            params[k] = "".join(v)

        return params


for eachLine in sys.stdin:
  a = ApacheLogLineParser()
  parsedLine =  a.parse(eachLine)

  try:
    #This is to handler lines that have missing values
    ts,http_user = parsedLine.time,parsedLine.http_user
    auxid = getId(parsedLine.user_agent)

    method,url,html = parsedLine.request_line.split()
    isClickEvent = False
    publisher = "-"
    medium = "-"
    campaign = "-" 
    content = "-"

    if(url.find("?") != -1):
      params = getUrlParams(url)
      
      isClickEvent = validateClickEvent(params)
      
      if(isClickEvent and validParamsRec(params)):
        publisher = params["utm_source"]
        medium = params["utm_medium"]
        campaign = params["utm_campaign"]
        content = params["utm_content"]
    
    print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (ts,http_user,auxid,isClickEvent,publisher,medium,campaign,content)
  except AttributeError:
    continue

