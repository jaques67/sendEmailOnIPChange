#!/usr/bin/python
import os
from os.path import exists
import requests
import logging


class IpInfo:
    """
    If the ip address file does not exist or a request has been made to resend the ip address, both scenarios are
    treated the same, asif the file does not exist. In the second case the ip file is deleted.
    If the file does exist and the value on the file is different from the current ip address the ip on file will
    be updated and an email will be sent
    If the file does exist and the value on the file is the same as the current ip address no email will be sent
    """
    logger = logging.getLogger(__name__)

    def __init__(self, config) -> None:
        general = dict(config['GENERAL'])
        self.file_name = general.get('ip_config_file')
        self.ip_check_service = general.get('ip_check_service')
        self.time_out = int(general.get('time_out'))
        self.old_ip_address = None
        self.current_ip_address = None
        IpInfo.logger.info(f'IP Info has been initialised')

    def __get_ip_address_from_file(self) -> None:
        """
        If the old_ip_address value is not None then it still has the old IP address and can skip the file read.
        If it is None, read the ip address file to retrieve the previous saved IP address if it exists.
        If the file does not exist, a value of 0.0.0.0 is returned.
        :return:
        """
        if self.old_ip_address is not None and self.old_ip_address != "0.0.0.0":
            IpInfo.logger.info('IP address did not change')
            return

        if not exists(self.file_name):
            IpInfo.logger.info('ip config file does not exist')
            print('ip config file does not exist')
            self.old_ip_address = "0.0.0.0"
        else:
            with open(self.file_name, "r") as file:
                self.old_ip_address = file.read()
                IpInfo.logger.debug(f'old ip address: {self.old_ip_address}')

    def __fetch_current_ip_address(self) -> None:
        """
        Use a web service to find the current IP address used by the router
        :return:
        """
        response = requests.get(self.ip_check_service)
        self.current_ip_address = response.text
        IpInfo.logger.debug(f'current ip address: {self.current_ip_address}')

    def __write_current_ip_address(self) -> None:
        """
        Write the current IP address to the ip file
        :return:
        """
        print('Writing ip config file')
        with open(self.file_name, "w") as f:
            f.write(self.current_ip_address)
            # update the ip address in memory as well
            self.old_ip_address = self.current_ip_address
            IpInfo.logger.info(f'old ip address has been updated')

    def get_current_ip_address(self) -> str:
        """
        Retrieve the value of the current IP address
        :return:
        """
        IpInfo.logger.info(f'requesting current ip address value')
        return self.current_ip_address

    def different_ip_address(self) -> bool:
        """
        Compare the old and new IP address values and return True if they differ and False if they are the same.
        If the result is false, the ip file and old_ip_address will be updated with the new IP address.
        :return:
        """
        self.__get_ip_address_from_file()
        self.__fetch_current_ip_address()

        # store result of ip address comparison in result as the old_ip_address is updated to the current value
        result = self.current_ip_address != self.old_ip_address
        IpInfo.logger.debug(f'old ip address: {self.old_ip_address}')

        self.__write_current_ip_address()

        return result

    def delete_ip_file(self):
        """
        Delete the IP file to indicate that this is a first run and the IP address must be re-sent.
        :return:
        """
        if os.path.exists(self.file_name):
            os.remove(self.file_name)
            IpInfo.logger.info(f'ip file has been deleted')

