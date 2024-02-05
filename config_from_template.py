import os
import toml
import time


def toml_data(toml_path):
    data = toml.load(toml_path)
    return data


TOML_DATA = toml_data("/home/alban/Desktop/config_from_template/config.toml")
SSH_PORT = TOML_DATA['config']['ssh_port']
HTTPS_PORT = TOML_DATA['config']['https_port']
LAN_ADDRESS = TOML_DATA['config']['lan_address']
HOSTNAME = TOML_DATA['config']['hostname']
DOMAIN = TOML_DATA['config']['domain']
USERNAME = TOML_DATA['user']['username']
PASSWORD = TOML_DATA['user']['password']
CONFIG_PATH = TOML_DATA['config']['config_path']
SNORT_TEMPLATE_PATH = TOML_DATA['config']['snort_template_path']

CRT_DESCRIPTION = TOML_DATA['certificate']['description']
CRT_CITY = TOML_DATA['certificate']['city']
CRT_COUNTRY = TOML_DATA['certificate']['country']
CRT_ORGANIZATION = TOML_DATA['certificate']['organization']
CRT_ORGANIZATIONALUNIT = TOML_DATA['certificate']['organizationalunit']
CRT_STATE = TOML_DATA['certificate']['state']
CRT_TYPE = TOML_DATA['certificate']['type']
CRT_COMMONNAME = f"{HOSTNAME}.{DOMAIN}"

VPN_DESCRIPTION = TOML_DATA['vpn']['description']
TLS_PATH = TOML_DATA['vpn']['tls_path']
SERVER_ADDR = TOML_DATA['vpn']['server_addr']
SERVER_PORT = TOML_DATA['vpn']['server_port']


def create_config():
    os.system(f"pfsense-manager create-config --file1-path {CONFIG_PATH} --lan-value {LAN_ADDRESS} --hostname-value {HOSTNAME} --domain-value {DOMAIN} --upload --host {LAN_ADDRESS} --name {HOSTNAME} --username {USERNAME} --password {PASSWORD} --port 22 --reboot")


def install_api():
    os.system(f"pfsense-manager install-api --host {LAN_ADDRESS} --username {USERNAME} --password {PASSWORD} --port {SSH_PORT}")


def install_snort():
    os.system(f"pfsense-manager add-package --host {LAN_ADDRESS} --port {SSH_PORT} --username {USERNAME} --password {PASSWORD} --package pfSense-pkg-snort")


def replace_snort():
    os.system(f"pfsense-manager transfert-field --host {LAN_ADDRESS} --name {HOSTNAME} --port {SSH_PORT} --username {USERNAME} --password {PASSWORD} --field snortglobal --template {SNORT_TEMPLATE_PATH} --reboot")


def read_ca():
    os.system(f"pfsense-manager read-ca --host {LAN_ADDRESS}:{HTTPS_PORT} --username {USERNAME} --password {PASSWORD}")


def read_certs():
    os.system(f"pfsense-manager read-certificates --host {LAN_ADDRESS}:{HTTPS_PORT} --username {USERNAME} --password {PASSWORD}")


def create_certificate():
    read_ca()
    caref = input("Enter the caref to use for creating certificate for vpn: ")
    os.system(f"pfsense-manager create-certificate --host {LAN_ADDRESS}:{HTTPS_PORT} --username {USERNAME} --password {PASSWORD} --caref {caref} --description {CRT_DESCRIPTION} --city {CRT_CITY} --commonname {CRT_COMMONNAME} --country {CRT_COUNTRY} --organization {CRT_ORGANIZATION} --organizationalunit {CRT_ORGANIZATIONALUNIT} --state {CRT_STATE} --type {CRT_TYPE}")


def create_vpn():
    read_ca()
    caref = input("Enter the caref to use for creating vpn client: ")
    read_certs()
    certref = input("Enter the certref to use for creating vpn client: ")
    os.system(f"pfsense-manager create-vpn --host {LAN_ADDRESS}:{HTTPS_PORT} --username {USERNAME} --password {PASSWORD} --caref {caref} --certref {certref} --description '{VPN_DESCRIPTION}' --tls-path {TLS_PATH} --server-addr {SERVER_ADDR} --server-port {SERVER_PORT}")


def main():
    print("This script will create a config and upload it on the new router")
    create_config()
    time.sleep(60)
    install_api()
    time.sleep(30)
    install_snort()
    time.sleep(40)
    replace_snort()
    time.sleep(40)
    create_certificate()
    create_vpn()


if __name__ == "__main__":
    main()