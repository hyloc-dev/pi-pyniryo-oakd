import os
import paramiko

host = '104.239.144.16'
port = 56029
username = 'hyloc'
key_path = '/Users/dipro/.ssh/id_rsa'
local_path = 'image_eval_data'
remote_path = ''

# Create an SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Load the private key
key = paramiko.RSAKey.from_private_key_file(key_path)

# Connect to the SFTP server
ssh.connect(hostname=host, port=port, username=username, pkey=key)

# Create an SFTP client
sftp = ssh.open_sftp()

# Copy the contents of the local directory to the remote directory
for file_name in os.listdir(local_path):
    local_file_path = os.path.join(local_path, file_name)
    remote_file_path = os.path.join(remote_path, file_name)
    sftp.put(local_file_path, remote_file_path)

# Close the SFTP session and SSH connection
sftp.close()
ssh.close()





