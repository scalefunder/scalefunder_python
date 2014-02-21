"""
2014 @copyright ScaleFunder, a RuffaloCody Platform
Contact: Andrew Dowds
Email: andrew.dowds@scalefunder.com
License: Module may not be used without expressed written consent of ScaleFunder
"""

import json
import urllib2,urllib
from urllib2 import URLError
from hmacsign import HMACScaleFunder

class NotifyParamException(Exception):
    pass

class ScaleFunderNotify(object):

    def __init__(self):
        self.sAppSecret = None
        self.sPingUrl = None
        self.sDonId = None
        self.nAmount = None
        self.sTransRef = None
        self.dParams = dict()

    @property
    def app_secret(self):
        return self.sAppSecret
    @app_secret.setter
    def app_secret(self, value):
        self.sAppSecret=value

    @property
    def ping_url(self):
        return self.sPingUrl

    @ping_url.setter
    def ping_url(self, value):
        self.sPingUrl = value

    @property
    def donation_id(self):
        return self.sDonId

    @donation_id.setter
    def donation_id(self, value):
        self.sDonId=value

    @property
    def amount(self):
        return self.nAmount

    @amount.setter
    def amount(self, value):
        self.nAmount = value

    @property
    def trans_ref(self):
        return self.sTransRef

    @trans_ref.setter
    def trans_ref(self, value):
        self.sTransRef = value

    def add_param(self, sKey,sValue):
        if sKey == "sf_sig" or sKey == "sf_don_id" or sKey=="sf_amount":
            raise NotifyParamException, "Cannot set param with reserved keys sf_sig,sf_don_id, or sf_amount"
        self.dParams[sKey] = sValue


    def notify(self):
        if not self.app_secret or not self.ping_url or not self.donation_id or not self.amount:
           raise MissingPropertyException, "Must set donation_id,ping_url,app_key, and amount"
        oHmac = HMACScaleFunder()
        dParams = self.dParams
        dParams["sf_don_id"] = self.donation_id
        dParams["sf_amount"] = self.amount
        sSig = oHmac.request_sig(dParams,self.app_secret)
        dParams["sf_sig"] = sSig
        if self.trans_ref:
            dParams["service_ref"] = self.trans_ref
        sCurlString = urllib.urlencode(dParams)
        try:
            req = urllib2.Request(self.ping_url , sCurlString)
            response = urllib2.urlopen(req)
            sResponse = response.read()
            dResponse = json.loads(sResponse)
            return dResponse
        except URLError, e:
            raise e
        except TypeError, e:
            raise e

def main():

    oNotify = ScaleFunderNotify()
    oNotify.app_secret ="996a68d3af3b22411664ea14af4e418f4e021204a514b68242db5e902d94d4ff" 
    oNotify.amount = "25"
    oNotify.trans_ref = "ADEFDED"
    oNotify.ping_url = "https://ucla.adowds.sfunder-dev.com/pmt/mp"
    oNotify.donation_id = "5307ac7a2cce5446f2bcf7dc"
    oNotify.add_param("response_text","Success")
    oNotify.add_param("response_code",1)
    dResponse =  oNotify.notify()
    print "%s" % dResponse


if __name__ == "__main__":
    main()
