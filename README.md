## Self TLS

### Run
- Go to anywhere have Go lang =)) <br>
  
- Change var hosts in `main.go` at line `63` if need. <br>
  
- Run this command: <br>
  ```bash
  git clone https://github.com/bpn2k4/self-tls
  cd self-tls
  go run main.go
  ```

It will generate 4 files into folder `cert`. <br>
- `ca.crt`: Root CA certificate, import it to system, Chrome, FireFox,... to use tls.
  
- `ca.key`: Root private key. Don't care about this file.
  
- `ssl.crt`: Certificate for host
  
- `ssl.key`: Private for host


### How to use tls (ssl)
- First, import root ca certificate to system:
  ```bash
  cd cert
  sudo cp ca.crt /usr/local/share/ca-certificates/
  sudo update-ca-certificates
  ```

- Config hosts:
  ```bash
  cat <<EOF | sudo tee -a /etc/hosts
  127.0.0.1 localhost.com
  EOF
  ```

#### Use with Nginx
- Install Nginx
- Run this command:
  ```bash
  cd cert
  sudo mkdir -p /tmp/cert
  sudo cp ssl.crt ssl.key /tmp/cert
  ```
- Config nginx:
  ```bash
  sudo vim /etc/nginx/conf.d/nginx.conf

  ### Add these line to this file
  server {
    listen 443 ssl;
    server_name localhost.com;
    ssl_certificate /cert/ssl.crt;
    ssl_certificate_key /cert/ssl.key;
    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }
  }

  ### Then restart Nginx
  sudo service nginx restart
  ```

- Then run:
  ```bash
  curl https://localhost.com
  ```

#### Use with Docker Nginx
- Go to cert folder, create 2 file: `docker-compose.yaml`, `nginx.conf`
  ```bash
  cd cert
  vim docker-compose.yaml
  vim nginx.conf
  ```

- `docker-compose.yaml` file
  ```bash
  name: "nginx"

  services:
    nginx:
      image: nginx:1.25
      container_name: nginx
      ports:
        - 80:80
        - 443:443
      volumes:
        - .:/cert
        - ./nginx.conf:/etc/nginx/conf.d/default.conf
  ```

- `nginx.conf` file
  ```bash
  server {
    listen 443 ssl;
    server_name localhost.com;
    ssl_certificate /cert/ssl.crt;
    ssl_certificate_key /cert/ssl.key;
    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }
  }
  ```

- Then run:
  ```bash
  docker compose up -d
  curl https://localhost.com
  ```

#### Use with Chrome
#### Use with FireFox
