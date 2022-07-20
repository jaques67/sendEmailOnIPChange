# sendEmailOnIPChange

## Scenario
In many 3rd world countries power is not stable.
When a power outage occured the ISP will issue a new IP.
This IP might be used for various different purposes.

## Solution:
When power is restored the python script will run and check whether the password has changed from the IP address stored on the file.
If the IP address has changed, an email will be sent via GMail informing you that the IP address changed and wht the new IP address is.

The following functionality has also been added:
Due to a chance that the email has not been sent, the program will now check Gmail every 15 minutes (set in the config file). It checks whether an email with a subject of ###Resend IP Address
After the email has been resent containing the IP address, the email will be set to Seen so that it will not continuously trigger the email.
