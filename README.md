# sendEmailOnIPChange

## Scenario
In many 3rd world countries power is not stable.
When a power outage occured the ISP will issue a new IP.
This IP might be used for various different purposes.

## Solution:
When power is restored the python script will run and check whether the password has changed from the IP address stored on the file.
If the IP address has changed, an email will be sent via GMail informing you that the IP address changed and wht the new IP address is.
