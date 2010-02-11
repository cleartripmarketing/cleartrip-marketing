#!/usr/bin/python

import sys
import cgi

VALID_REC_LEN = 11

def getId(data):
    """
    This gets Auxilary ID from Cookie Data stored in logs
    """
    result = "-"
    for eachString in data.split():
        if(eachString.find("Apache") != -1):
            result = eachString[eachString.find("=")+1:].replace(";","")
    return result

def validParamsRec(data):
    """
    This function is used to validate params record
    """
    try:
        if(len(data) != 4):
            return False
    except:
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
    eachLine = eachLine.strip()
    if(len(eachLine.split("\t")) == VALID_REC_LEN):
        ip,http_user,ts,method,url,http_status_code,http_response_time,refferal,user_agent,var1,var2 = eachLine.split("\t")
        auxid = "-"
        if(http_user != "-" and user_agent != "-"):
            auxid = getId(user_agent)
        
        params = getUrlParams(url)
        if(validParamsRec(params)):
            try:
                print "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (ts,http_user,auxid,params["utm_source"],params["utm_medium"],params["utm_campaign"],params["utm_content"])
            except:
                continue
            

