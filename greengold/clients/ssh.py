import time
import logging
import paramiko
from greengold import exceptions as ggexc


log = logging.getLogger("greengold")


class SSHClient:
    def __init__(self, ip_address, user, ssh_key, passphrase=None, bastion_ip=None):
        self.ip_address = ip_address
        self.bastion_ip = bastion_ip
        self.user = user
        self.ssh_key = paramiko.RSAKey.from_private_key_file(ssh_key)
        self.passphrase = passphrase
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.bastion_ip:
            raise ggexc.SSHClientException(f"Bastion connections are not yet supported")

    def connect(self):
        self.client.connect(
            self.ip_address,
            username=self.user,
            port=22,
            pkey=self.ssh_key,
            passphrase=self.passphrase
        )
        return self.client

    def close(self):
        self.client.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def wait_until_ssh_ready(self, timeout=None, retry_interval=None):

        timeout = timeout or 60
        retry_interval = retry_interval or 5
        timeout_start = time.time()

        while time.time() < timeout_start + timeout:
            try:
                log.debug(f"Trying SSH connection to {self.ip_address} on port 22...")
                self.client.connect(self.ip_address, port=22, allow_agent=False, look_for_keys=False)
            except paramiko.ssh_exception.SSHException as exc:
                if "Error reading SSH protocol banner" in str(exc):
                    time.sleep(retry_interval)
                    continue
                log.debug(f"IP Address {self.ip_address} is now listening for SSH")
                return
            except paramiko.ssh_exception.NoValidConnectionsError:
                time.sleep(retry_interval)
                continue
        raise ggexc.SSHClientException(f"Timeout ({timeout}s) waiting for SSH availability to {self.ip_address}")

    def wait_on_command(self, command, exit_code=None, conn=None, timeout=None, retry_interval=None):

        exit_code = exit_code or 0
        timeout = timeout or 60
        retry_interval = retry_interval or 5
        timeout_start = time.time()

        manage_conn = bool(conn is None)
        if manage_conn:
            conn = self.connect()

        try:
            while time.time() < timeout_start + timeout:
                try:
                    return self.exec(command, conn=conn, expected_return_code=exit_code)
                except ggexc.SSHReturnCodeException:
                    time.sleep(retry_interval)
                    continue
        finally:
            if manage_conn:
                conn.close()
        raise ggexc.SSHClientException(f"Timeout ({timeout}s) waiting for "
                                       f"{command} with return code {exit_code} on "
                                       f"{self.ip_address}")

    def exec(self, command, conn=None, expected_return_code=None):
        manage_conn = bool(conn is None)
        if manage_conn:
            conn = self.connect()
        try:
            log.debug(f"Sending command '{command}' to IP Address {self.ip_address}")
            stdin, stdout, stderr = conn.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            stdout_lines = stdout.readlines()
            stderr_lines = stderr.readlines()
            log.info(f"Command '{command}' output:")
            if not stdout_lines and not stderr_lines:
                log.info(f"[no output]")
            if stdout_lines:
                stdout_text = '\t'.join(stdout_lines)
                log.info(f"stdout:\n\t{stdout_text}")
            if stderr_lines:
                stderr_text = '\t'.join(stderr_lines)
                log.warning(f"stderr:\n\t{stderr_text}")
            if expected_return_code is not None and exit_code != expected_return_code:
                raise ggexc.SSHReturnCodeException(f"Command '{command}' returned exit code {exit_code}. "
                                                   f"Expected {expected_return_code}")
            return [l.rstrip("\n") for l in stdout_lines], [l.rstrip("\n") for l in stderr_lines]
        except ggexc.SSHClientException:
            raise
        except Exception as exc:
            raise ggexc.SSHClientException(f"Command '{command}' failed to execute.") from exc
        finally:
            if manage_conn:
                conn.close()
