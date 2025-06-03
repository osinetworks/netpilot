from netmiko import ConnectHandler


connection_params = {
    "device_type": "arista_eos",
    "host": "172.20.20.101",
    "username": "admin",
    "password": "admin",
    "session_log": "netmiko_session.log"
}

commands = [
    "vlan 100",
    "name USERS"
]

with ConnectHandler(**connection_params) as net_connect:
    net_connect.enable()
    output = net_connect.send_config_set(commands)
    output += "\n" + net_connect.save_config()

print(output)
