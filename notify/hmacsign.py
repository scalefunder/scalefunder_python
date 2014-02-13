"""
2014 @copyright ScaleFunder, a RuffaloCody Platform
Contact: Andrew Dowds
Email: andrew.dowds@scalefunder.com
License: Module may not be used without expressed written consent of ScaleFunder
"""

from time import time
from copy import copy
import hmac
import os
from hashlib import sha256

class NoSigException(Exception):
    pass
class MissingParamException(Exception):
    pass


class HMACSign(object):

    def org_request_sig(self, dData, oOrg):
        return self.sign_request(dData,sKey)

    def get_concat_string(self,dData):
        lList = dData.keys()
        lList.sort()
        sReq = ""
        for k in lList:
            sReq += k
            sReq += "%s" % dData.get(k)
        return sReq

    def request_sig(self,dData, sKey):
        sReq = self.get_concat_string(dData)
        sMac = hmac.new(str(sKey), str(sReq), sha256).hexdigest()
        return sMac

    def validate_request(self,dParams,sKey):
        if not dParams.get("sf_sig"):
            raise NoSigException("No signature passed to validate request")
        dVal = copy(dict(dParams.items()))
        sSig = dVal.get("sf_sig")
        del dVal["sf_sig"]
        sCalcSig = self.request_sig(dVal,sKey)
        return sSig==sCalcSig

class HMACAuthNet(HMACSign):
    def request_sig(self,dData,sKey):
        dSign = dict()
        dData["sf_timestamp"] = "%s" % int(time())
        sToSign = "^".join([dData["sf_trans_id"],dData["sf_timestamp"]])
        sMac = hmac.new(str(sKey),str(sToSign),sha256).hexdigest()
        return sMac

class HMACScaleFunder(HMACSign):
    def request_sig(self,dData,sKey):
        dSign = dict()
        lKeys = dData.keys()
        if not 'sf_don_id' in lKeys or not 'sf_amount' in lKeys:
            raise MissingParamException, "Missing sf_don_id or sf_amount"
        sToSign = "^".join([dData["sf_don_id"],dData["sf_amount"]]) + "^"
        sMac = hmac.new(str(sKey),str(sToSign),sha256).hexdigest()
        return sMac
    def get_concat_string(self,dData):
        sToSign = "^".join([dData["sf_don_id"],dData["sf_amount"]]) + "^"
        return sToSign 
