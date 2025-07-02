from opcua import Client
from typing import List, Any, Optional


class OPCUAReader:
    def __init__(self, address: str, port: Optional[int] = None, authentication_mode: str = "anonymous",
                 username: str = "", password: str = ""):
        """
        :param address: Can be 'opc.tcp://host' or full URL like 'opc.tcp://host:port'
        :param port: Optional port. Used only if address doesn't contain one.
        :param authentication_mode: 'anonymous' or 'username_password'
        :param username: Used only for username_password mode
        :param password: Used only for username_password mode
        """
        self.address = address
        self.port = port
        self.authentication_mode = authentication_mode.lower()
        self.username = username
        self.password = password
        self.client: Optional[Client] = None

    def connect(self):
        if self.address.startswith("opc.tcp://"):
            server_url = self.address if self.port is None else f"{self.address}:{self.port}"
        else:
            server_url = f"opc.tcp://{self.address}:{self.port or 4840}"

        try:
            self.client = Client(server_url)

            if self.authentication_mode == "username_password":
                self.client.set_user(self.username)
                self.client.set_password(self.password)
            elif self.authentication_mode != "anonymous":
                raise ValueError(f"Unsupported authentication mode: {self.authentication_mode}")

            self.client.connect()
            print(f"[✔] Connected to OPC UA Server: {server_url}")

        except Exception as e:
            raise ConnectionError(f"Failed to connect to OPC UA Server: {server_url}") from e

    def disconnect(self):
        if self.client:
            try:
                self.client.disconnect()
                print("[✔] Disconnected from OPC UA Server.")
            except Exception as e:
                raise RuntimeError("Disconnection failed.") from e

    def read_node(self, node_id: str) -> Any:
        try:
            node = self.client.get_node(node_id)
            value = node.get_value()
            return value
        except Exception as e:
            raise RuntimeError(f"Failed to read node '{node_id}'") from e

    def read_nodes(self, node_ids: List[str]) -> List[Any]:
        return [self.read_node(node_id) for node_id in node_ids]

    def write_node(self, node_id: str, value: Any):
        try:
            node = self.client.get_node(node_id)
            node.set_value(value)
            print(f"[✔] Wrote value '{value}' to node '{node_id}'")
        except Exception as e:
            raise RuntimeError(f"Failed to write to node '{node_id}'") from e
