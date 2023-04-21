#!/usr/bin/env python3

"""
A Python script to configure SSH access on a jump box.

This script automates the process of creating user accounts for team members,
setting up their .ssh directories and authorized_keys files, and adding their
public SSH keys for access.

Please note that this script assumes that you have already SSH'ed into the jump
box using the private key associated with the key pair you used when launching
the instance.

Usage:
    Run the script as root or with sudo: `./configure_jump_box.py`
"""

import os
import subprocess

# Check if the script is run as root or with sudo
if os.getuid() != 0:
    print("Please run this script as root or with sudo.")
    exit(1)

def create_user(username):
    """
    Create a user account and add them to the sudo group.

    Args:
        username (str): The username for the new user account.
    """
    subprocess.run(["adduser", username])
    subprocess.run(["usermod", "-aG", "sudo", username])

def setup_ssh_directory(username):
    """
    Set up the .ssh directory and authorized_keys file for a user.

    Args:
        username (str): The username for the user account.
    """
    ssh_dir = f"/home/{username}/.ssh"
    authorized_keys_file = f"{ssh_dir}/authorized_keys"
    os.makedirs(ssh_dir)
    open(authorized_keys_file, "w").close()

    return authorized_keys_file

def add_public_key(username, public_key, authorized_keys_file):
    """
    Add a user's public SSH key to their authorized_keys file.

    Args:
        username (str): The username for the user account.
        public_key (str): The public SSH key for the user.
        authorized_keys_file (str): The path to the user's authorized_keys file.
    """
    with open(authorized_keys_file, "a") as f:
        f.write(f"{public_key}\n")

def set_permissions(username, ssh_dir, authorized_keys_file):
    """
    Set appropriate ownership and permissions for the .ssh directory and the authorized_keys file.

    Args:
        username (str): The username for the user account.
        ssh_dir (str): The path to the user's .ssh directory.
        authorized_keys_file (str): The path to the user's authorized_keys file.
    """
    subprocess.run(["chown", "-R", f"{username}:{username}", ssh_dir])
    os.chmod(ssh_dir, 0o700)
    os.chmod(authorized_keys_file, 0o600)

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
