import logging
import pexpect

class XMPPUserManagement:
    def __init__(self, container_name):
        self.container_name = container_name

    def add_user(self, username, domain, password):
        """Create a user inside the Prosody container using docker exec and handle password input by reading output."""
        try:
            # Step 1: Start docker exec to run the prosodyctl adduser command in the container
            add_user_command = f"docker exec -it {self.container_name} /bin/bash -c 'prosodyctl adduser {username}@{domain}'"

            # Start the command with pexpect (use '-i' for interactive mode, and shell=True)
            child = pexpect.spawn(add_user_command, encoding='utf-8', shell=True)

            # Step 2: Read the output and check for password prompts
            output = child.read()  # Read the initial output
            print(output)

            # Step 3: Look for the "Enter new password:" prompt in the output
            while "Enter new password:" not in output:
                output += child.read()  # Continue reading output

            logging.info("Password prompt detected.")
            child.sendline(password)  # Send the password

            # Step 4: Now wait for the "Retype new password:" prompt
            output = child.read()  # Read the next part of the output
            while "Retype new password:" not in output:
                output += child.read()  # Continue reading output

            logging.info("Retype password prompt detected.")
            child.sendline(password)  # Confirm the password

            # Step 5: Wait for the command to complete (successful completion)
            output = child.read()  # Read until end of process
            logging.info(f"Process output: {output}")

            child.close()

            logging.info(f"User {username}@{domain} created successfully.")
        except pexpect.exceptions.ExceptionPexpect as e:
            logging.error(f"Failed to create user {username}@{domain}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

# Usage
xmpp_user_management = XMPPUserManagement(container_name="prosody_xmpp")
xmpp_user_management.add_user("userA", "domain", "passwordA")
xmpp_user_management.add_user("userB", "domain", "passwordB")