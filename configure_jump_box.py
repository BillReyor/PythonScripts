#!/usr/bin/env python3

import os
import subprocess
import getpass

# This script assumes you have already SSH'ed into the jump box using the
# private key associated with the key pair you used when launching the instance.

# Check if the script is run as root or with sudo
if os.getuid() != 0:
    print("Please run this script as root or with sudo.")
    exit(1)

# Create a new user account for each team member
num_members = int(input("Enter the number of team members: "))

for i in range(1, num_members + 1):
    username = input(f"Enter username for team member {i}: ")
    subprocess.run(["adduser", username])
    subprocess.run(["usermod", "-aG", "sudo", username])

    # Create the .ssh directory and the authorized_keys file
    ssh_dir = f"/home/{username}/.ssh"
    authorized_keys_file = f"{ssh_dir}/authorized_keys"
    os.makedirs(ssh_dir)
    open(authorized_keys_file, "w").close()

    # Add the user's public SSH key to their respective authorized_keys file
    public_ssh_key = input(f"Enter the public SSH key for user {username}: ")
    with open(authorized_keys_file, "a") as f:
        f.write(f"{public_ssh_key}\n")

    # Set appropriate ownership and permissions for the .ssh directory and the authorized_keys file
    subprocess.run(["chown", "-R", f"{username}:{username}", ssh_dir])
    os.chmod(ssh_dir, 0o700)
    os.chmod(authorized_keys_file, 0o600)

# Share the jump box's public IP address or DNS name with your team members
print("SSH access configuration complete. Share the jump box's public IP address or DNS name with your team members.")
