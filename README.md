# sendEmailOnIPChange

## Scenario
At random times, an ISP might issue a new IP address which means that you can no longer access that PC if you have port forwarding enabled.
As Dynamic DNS is not allways an option this might allow a temporary reprieve until you find a better solution.

## Solution:
Depending on the OS set the python script to start running at startup.
It will compare the current IP address with that of the IP address stored on the file. If the file does not exist, it will continue as if the IP address has changed.
If the IP address has changed, an email will be sent via GMail informing you that the IP address changed and what the new IP address is.

The following functionality has also been added:
* Due to a chance that the IP address might change again, the program will compare the IP address every 15 minutes (set in the config file). 
* The script will also access the email account and scan the inbox to determine whether an unread email with a subject of "Resend IP Address" exists. If it does find such an email, it will then perform full validation and resend the IP address and mark the email as read.

## First Run
On first run the following files should be updated/created.
* config.ini file
    * config.ini.example should be renamed to config.ini;
    * populate the fields that have been placed between angular brackets <>;
    * paste the email password in plain text in the config.ini file in the password section. It will be encrypted during the first run after the encryption key has been generated;
    * ensure the fernet-key entry is set to None;
    * If the preference is to save the fernet key to the config file, change the value of the update_fernet key value to True;
    * If the .env file does not exist, the config.ini file will automatically be updated with the fernet key.
* .env file
    * if you want to make use of an environment file, rename .env.example to .env;
    * leave the fernet-key entry as is. It will be populated after the first run;
    * Processing always reads the config.ini file first;
    * If this is not the first run the key in the config.ini file will have to be changed to None. ***Do NOT delete the values if you do not know or remember what your password is***:
        * First retrieve your password by using your existing fernet-key and password found in the config.ini file;
        * Run the decode_password.py script to retrieve your password. Use the fernet-key and password as parameters to the script
        * The password will be printed to the terminal/console. Remember to overwrite the value in the config.ini with this decoded password for encryption with the new key.

