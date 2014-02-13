scalefunder_python
==================

ScaleFunder Python Client

The ScaleFunder python client handles the notification of a successful transaction to the Scalefunder system.Upon clearing the payment, the developer is responsible for posting the successful transaction to the scalefunder website and then redirecting the user to the provided ScaleFunder thank-you page URL.  

With every post to the payment page, ScaleFunder will pass along the ping_url and the redirect_url. The ping url is the url to post the successful transaction to, and the redirect url is the thank-you page url.  


```python
    oNotify = ScaleFunderNotify()
    oNotify.app_secret ="996a68d3af3b22411664ea14af4e418f4e021204a514b68242db5e902d94d4ff" 
    oNotify.amount = "25"
    oNotify.trans_ref = "ADEFDED"
    oNotify.ping_url = "https://ucla.adowds.sfunder-dev.com/pmt/mp"
    oNotify.donation_id = "52fc2dbe2cce540a992480b7"
    dResponse =  oNotify.notify()
```
