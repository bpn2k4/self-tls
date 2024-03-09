# SELF TLS

## Quick start
  - Window usage:
    ```bash
    curl -O https://github.com/bpn2k4/self-tls/releases/download/latest/tls.exe
    tls init
    tls sign localhost.com
    ```
  - Linux usage:
    ```bash
    curl -O https://github.com/bpn2k4/self-tls/releases/download/latest/tls
    ./tls init
    ./tls sign localhost.com
    ```
## Command
  `tls init` : Generate a root key pair private key and certificate
  `tls sign <hostname>` : Generate a key pair key and cert for [hostname]
## Build from source
- Clone this repo
  ```bash
  git clone https://github.com/bpn2k4/self-tls.git
  cd self-tls
  ```
- Create a environment
  + Window usage:
    ```bash
    virtualenv venv
    .\venv\Scripts\activate
    ```
      or
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
  + Linux usage:
    ```bash
    virtualenv venv
    source ./venv/Scripts/activate
    ```
    or
    ```bash
    python3 -m venv venv
    source ./venv/Scripts/activate
    ```
- Install requirement:
  ```bash
  pip install -r requirements.txt
  ```
- Build:
  ```bash
  pyinstaller --onefile --name tls tool.py
  cd dist
  ```