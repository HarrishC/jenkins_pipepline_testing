import os
import subprocess
import sys
import tempfile

GITLAB_REPO_URL = os.environ.get('GITLAB_REPO_URL', 'https://gitlab.com/your-username/your-repo.git')
GIT_BRANCH = os.environ.get('GIT_BRANCH', 'main')

AWS_SERVER_IP = os.environ.get('AWS_SERVER_IP', 'your.aws.ec2.ip.address')
AWS_USER = os.environ.get('AWS_USER', 'ubuntu')
DEPLOY_PATH = os.environ.get('DEPLOY_PATH', '/var/www/html')

SSH_KEY_PATH = os.environ.get('SSH_KEY_PATH', '~/.ssh/id_rsa')


def run_command(command, cwd=None, shell=False):
    """Utility to run shell commands and stream output."""
    try:
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        print(f"Running: {cmd_str}")
        
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print(e.stdout)
        return False


def main():
    print("Starting deployment pipeline...")

    with tempfile.TemporaryDirectory() as temp_dir:
        
        print("\n--- Stage: Checkout from GitLab ---")
        print("Pulling website files from GitLab...")
        
        clone_cmd = [
            'git', 'clone', 
            '--branch', GIT_BRANCH, 
            '--depth', '1', 
            GITLAB_REPO_URL, 
            temp_dir
        ]
        
        if not run_command(clone_cmd):
            print("❌ Pipeline failed during checkout! Please check the logs.")
            sys.exit(1)


        print("\n--- Stage: Deploy to AWS Server ---")
        print("Deploying files to AWS EC2 instance...")

        ssh_dir = os.path.expanduser("~/.ssh")
        os.makedirs(ssh_dir, exist_ok=True)
        known_hosts_path = os.path.join(ssh_dir, "known_hosts")
        
        keyscan_cmd = f"ssh-keyscan -H {AWS_SERVER_IP} >> {known_hosts_path}"
        if not run_command(keyscan_cmd, shell=True):
            print("⚠️ Warning: Failed to add host to known_hosts. Deployment might require interactive prompt.")

        print("Transferring files...")
        
        ssh_options = f'ssh -i {os.path.expanduser(SSH_KEY_PATH)} -o StrictHostKeyChecking=no'
        
        rsync_cmd = [
            'rsync', '-avz', '--delete', 
            '--exclude', '.git/',
            '-e', ssh_options,
            f"{temp_dir}/",
            f"{AWS_USER}@{AWS_SERVER_IP}:{DEPLOY_PATH}"
        ]

        if not run_command(rsync_cmd):
            print("❌ Pipeline failed during rsync! Please check the logs.")
            sys.exit(1)

    print("\n✅ Deployment to AWS was successful!")


if __name__ == "__main__":
    main()
