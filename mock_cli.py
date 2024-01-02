import re
import ipaddress

class Router:
    # modes: ['user', 'enable', 'conf']

    def __init__(self):
        self.hostname = "Router"
        self.mode = 'user'
        self.ip_address = None
        self.netmask = None

        # command matches
        self.enable_match = [r"^(en|ena|enab|enabl|enable)$", self.enable_command]
        self.exit_match = [r"^(ex|exi|exit)$", self.exit_command]
        self.end_match = [r"^(end)$", self.end_command]
        self.hostname_match = [r"^(host|hostn|hostna|hostnam|hostname)\s+([a-zA-Z0-9]+)$", self.hostname_command]
        self.configure_terminal_match = [r"^(conf|confi|config|configu|configur|configure)\s+(t|te|ter|term|termi|termin|termin|terminal)$", self.configure_terminal_command]
        self.ip_address_match = [r"^(ip address) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})( (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))?$", self.ip_address_command]
        self.show_match = [r"^(sh|sho|show)\s+([a-z]+)$", self.show_command]

        # dictionaries of {mode: [available commands]}
        self.patterns = {
            'user': [
                self.enable_match,
                self.show_match,
                self.end_match
            ],
            'enable': [
                self.exit_match,
                self.hostname_match,
                self.configure_terminal_match,
                self.show_match,
                self.end_match
            ],
            'conf': [
                self.exit_match,
                self.ip_address_match,
                self.end_match
            ]
        }

    # universal commands
    def exit_command(self, *args):
        if self.mode == 'conf':
            self.mode = 'enable'
        elif self.mode == 'enable':
            self.mode = 'user'
    def end_command(self, *args):
        self.mode = 'user'
    def show_command(self, *args):
        if re.match(r"^(ip)$", args[1]):
            print(f"IP Address: {self.ip_address}\nSubnet: {self.netmask}")

    # user mode commands
    def enable_command(self, *args):
        self.mode = 'enable'

    # enable mode commands
    def configure_terminal_command(self, *args):
        self.mode = 'conf'
    def hostname_command(self, *args):
        self.hostname = args[1]

    # configure terminal mode commands
    def ip_address_command(self, *args):
        try:
            ipaddress.ip_address(args[2])
            netmask = args[3] if len(args) > 3 else None
            if netmask:
                ipaddress.ip_address(netmask)
            self.ip_address = args[2]
            self.netmask = netmask if netmask else None
        except ValueError:
            print("Invalid format. Use: ip address <ip address> [<subnet mask>]")
        except IndexError:
            print("Not enough arguments. Use: ip address <ip address> [<subnet mask>]")

    # format input prompt
    def format_input(self):
        if self.mode == 'user':
            return input(f"{self.hostname}> ").strip()
        elif self.mode == 'enable':
            return input(f"{self.hostname}# ").strip()
        elif self.mode == 'conf':
            return input(f"{self.hostname}(config)# ").strip()
        else:
            return input(f"{self.hostname}(unknown)> ").strip()

    # execute command per given input
    def get_input(self):
        user_input = self.format_input().split()
        for pattern, action in self.patterns[self.mode]:
            match = re.match(pattern, ' '.join(user_input))
            if match:
                action(*user_input)
                return True
        print("Invalid command")
        return False

    # loop command line
    def initialize(self):
        while True:
            self.get_input()

router = Router()
router.initialize()
