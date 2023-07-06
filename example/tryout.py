from optoid import Commander

commander = Commander()
commander.attach()
print("success to attach")
commander.send_command("lis;len;lis;lis;lis")
print("success to send command")
