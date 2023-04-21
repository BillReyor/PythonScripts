#!/usr/bin/env python3

import os
import subprocess

def update_sudoers_file():
    """
    Update the sudoers file to allow passwordless sudo for users in the sudo group.
    """
    sudoers_file = "/etc/sudoers"
    new_line = "%sudo ALL=(ALL:ALL) NOPASSWD:ALL\n"

    with open(sudoers_file, "r") as f:
        content = f.readlines()

    if new_line in content:
        print("sudoers file already allows passwordless sudo for the sudo group.")
        return

    with open(sudoers_file, "a") as f:
        f.write(new_line)
    
    print("Updated sudoers file to allow passwordless sudo for the sudo group.")

# Check if the script is run as root or with sudo
if os.getuid() != 0:
    print("Please run this script as root or with sudo.")
    exit(1)

# Update sudoers file to allow passwordless sudo for users in the sudo group
update_sudoers_file()

# Create a new user account for each team member
num_members = int(input("Enter the number of team members: "))

for i in range(1, num_members + 1):
    username = input(f"Enter username for team member {i}: ")
    create_user(username)

    authorized_keys_file = setup_ssh_directory(username)

    public_ssh_key = input(f"Enter the public SSH key for user {username}: ")
    add_public_key(username, public_ssh_key, authorized_keys_file)

    ssh_dir = f"/home/{username}/.ssh"
    set_permissions(username, ssh_dir, authorized_keys_file)

# Share the jump box's public IP address or DNS name with your team members
print("SSH access configuration complete. Share the jump box's public IP address or DNS name with your team members.")
