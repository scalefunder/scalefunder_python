ScaleFunder Python Client
=========================

The ScaleFunder python client handles the notification of a successful transaction to the Scalefunder system. It digitally signs key parameters and then transmits the transaction to ScaleFunder. 
Upon clearing the payment, the developer is responsible for posting the successful transaction to the scalefunder website and then redirecting the user to the provided ScaleFunder thank-you page URL.  

With every post to the payment page, ScaleFunder will pass along the ping_url and the redirect_url. The ping url is the url to post the successful transaction to, and the redirect url is the thank-you page url.  

 Here is a list of the minimum variable set ScaleFunder  will post to payment page. The names of these variables can be changed if your system has exisiting immutable conventions.
 * Amount (amount) 
 * Donation ID (donation_id)
 * Ping URL (ping_url)
 * Thank-you URL (thankyou_url)

Other variables will also be passed if desired:
 * Project Fund ID
 * Project Appeal ID
 * Project Name 
 * Perk Name Selected 
 * Perk Code Selected
 * Perk Fair Market Value
 * Donor First Name
 * Donor Last Name
 * Donor Email Address


The main purpose of this module, however, is to notify ScaleFunder of a successful transaction, and that involves the variables referenced in the code example below.  
In addition to the named properties you may also wish to store certain data in ScaleFunder along with the transaction. For example, in addition to a transaction reference number,
you may want to store a human readable message from the payment provider, or a result code. In order to do that, simply add that parameter to the ScaleFunder notify object before passing it along.
See the code example below:

Please Note: Do not call notify unless the transaction is successful. ScaleFunder assumes that errors in transaction processing are handled by the client.


```python
    oNotify = ScaleFunderNotify()
    dPost = get_post_params()
    #This the app secret generated in the scalefunder platform
    oNotify.app_secret ="996a68d3af3b22411664ea14af4e418f4e021204a514b68242db5e902d94d4ff" 

    #The amount of the transaction 
    oNotify.amount = "25"

    #The transaction reference ID that uniquely identifies this transaction. This can be from your payment provider or custom system.
    oNotify.trans_ref = "ADEFDED"

    #The ping url is passed to your page on the initial post. That URL should be used here.
    oNotify.ping_url = dPost.get("ping_url")

    #donation_id is ScaleFunder's unique transaction id for this transaction. It is passed in on the initial post.
    oNotify.donation_id = "52fc2dbe2cce540a992480b7"

    #Add optional data to store with transaction.
    oNotify.add_param("response_text","Successful")
    oNotify.add_param("response_code",1)

    dResponse =  oNotify.notify()

    #Redirect user to ScaleFunder thankyou_page. Your method of issuing an HTTP redirect will vary depending on your framework.
    redirect(dPost.get("thankyou_url"))

```
