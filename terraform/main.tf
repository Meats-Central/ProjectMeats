# Add delay to stagger droplet operations
resource "time_sleep" "wait_between_droplets" {
  create_duration = "30s"
  destroy_duration = "30s"
}

# Define Digital Ocean droplets for DEV, UAT, and PROD
resource "digitalocean_droplet" "projectmeats_dev" {
  name       = "projectmeats-dev"
  region     = var.region
  size       = "s-1vcpu-1gb"
  image      = "ubuntu-22-04-x64"
  ssh_keys   = [digitalocean_ssh_key.deploy_key.fingerprint]
  timeouts {
    create = "5m"
    delete = "5m"
  }
  user_data  = <<-EOT
    #cloud-config
    users:
      - name: deploy
        groups: sudo
        shell: /bin/bash
        sudo: ['ALL=(ALL) NOPASSWD:ALL']
        ssh-authorized-keys:
          - ${var.ssh_public_key}
    packages:
      - apt-transport-https
      - ca-certificates
      - curl
      - software-properties-common
      - python3
      - python3-pip
      - python3-venv
      - git
      - postgresql
      - postgresql-contrib
    runcmd:
      # Wait for network
      - sleep 10
      # Add swap
      - fallocate -l 2G /swapfile || true
      - chmod 600 /swapfile || true
      - mkswap /swapfile || true
      - swapon /swapfile || true
      - echo '/swapfile none swap sw 0 0' >> /etc/fstab
      # Install Docker
      - apt-get update -y >> /var/log/user-data.log 2>&1
      - apt-get install -y ca-certificates curl >> /var/log/user-data.log 2>&1
      - install -m 0755 -d /etc/apt/keyrings || true
      - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg >> /var/log/user-data.log 2>&1
      - chmod a+r /etc/apt/keyrings/docker.gpg
      - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      - apt-get update -y >> /var/log/user-data.log 2>&1
      - apt-get install -y docker-ce docker-ce-cli containerd.io >> /var/log/user-data.log 2>&1
      - systemctl enable docker >> /var/log/user-data.log 2>&1
      - systemctl start docker >> /var/log/user-data.log 2>&1
      - usermod -aG docker deploy >> /var/log/user-data.log 2>&1
      # Install Docker Compose plugin
      - mkdir -p /usr/libexec/docker/cli-plugins || true
      - curl -SL https://github.com/docker/compose/releases/download/v2.24.7/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose >> /var/log/user-data.log 2>&1
      - chmod +x /usr/libexec/docker/cli-plugins/docker-compose || true
      # Configure firewall
      - ufw allow OpenSSH >> /var/log/user-data.log 2>&1
      - ufw allow 80 >> /var/log/user-data.log 2>&1
      - ufw allow 443 >> /var/log/user-data.log 2>&1
      - ufw --force enable >> /var/log/user-data.log 2>&1
      # Create deployment directory
      - mkdir -p /opt/projectmeats/env >> /var/log/user-data.log 2>&1
      - chown -R deploy:deploy /opt/projectmeats >> /var/log/user-data.log 2>&1
      - chmod 700 /opt/projectmeats/env >> /var/log/user-data.log 2>&1
      # Log completion
      - echo "Cloud-init completed" >> /var/log/user-data.log
  EOT
}

resource "digitalocean_droplet" "projectmeats_uat" {
  name       = "projectmeats-uat"
  region     = var.region
  size       = "s-2vcpu-2gb"
  image      = "ubuntu-22-04-x64"
  ssh_keys   = [digitalocean_ssh_key.deploy_key.fingerprint]
  timeouts {
    create = "5m"
    delete = "5m"
  }
  user_data  = <<-EOT
    #cloud-config
    users:
      - name: deploy
        groups: sudo
        shell: /bin/bash
        sudo: ['ALL=(ALL) NOPASSWD:ALL']
        ssh-authorized-keys:
          - ${var.ssh_public_key}
    packages:
      - apt-transport-https
      - ca-certificates
      - curl
      - software-properties-common
      - python3
      - python3-pip
      - python3-venv
      - git
    runcmd:
      # Wait for network
      - sleep 10
      # Add swap
      - fallocate -l 2G /swapfile || true
      - chmod 600 /swapfile || true
      - mkswap /swapfile || true
      - swapon /swapfile || true
      - echo '/swapfile none swap sw 0 0' >> /etc/fstab
      # Install Docker
      - apt-get update -y >> /var/log/user-data.log 2>&1
      - apt-get install -y ca-certificates curl >> /var/log/user-data.log 2>&1
      - install -m 0755 -d /etc/apt/keyrings || true
      - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg >> /var/log/user-data.log 2>&1
      - chmod a+r /etc/apt/keyrings/docker.gpg
      - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      - apt-get update -y >> /var/log/user-data.log 2>&1
      - apt-get install -y docker-ce docker-ce-cli containerd.io >> /var/log/user-data.log 2>&1
      - systemctl enable docker >> /var/log/user-data.log 2>&1
      - systemctl start docker >> /var/log/user-data.log 2>&1
      - usermod -aG docker deploy >> /var/log/user-data.log 2>&1
      # Install Docker Compose plugin
      - mkdir -p /usr/libexec/docker/cli-plugins || true
      - curl -SL https://github.com/docker/compose/releases/download/v2.24.7/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose >> /var/log/user-data.log 2>&1
      - chmod +x /usr/libexec/docker/cli-plugins/docker-compose || true
      # Configure firewall
      - ufw allow OpenSSH >> /var/log/user-data.log 2>&1
      - ufw allow 80 >> /var/log/user-data.log 2>&1
      - ufw allow 443 >> /var/log/user-data.log 2>&1
      - ufw --force enable >> /var/log/user-data.log 2>&1
      # Create deployment directory
      - mkdir -p /opt/projectmeats/env >> /var/log/user-data.log 2>&1
      - chown -R deploy:deploy /opt/projectmeats >> /var/log/user-data.log 2>&1
      - chmod 700 /opt/projectmeats/env >> /var/log/user-data.log 2>&1
      # Log completion
      - echo "Cloud-init completed" >> /var/log/user-data.log
  EOT
  depends_on = [time_sleep.wait_between_droplets]
}

resource "digitalocean_droplet" "projectmeats_prod" {
  name       = "projectmeats-prod"
  region     = var.region
  size       = "s-4vcpu-8gb"
  image      = "ubuntu-22-04-x64"
  ssh_keys   = [digitalocean_ssh_key.deploy_key.fingerprint]
  timeouts {
    create = "5m"
    delete = "5m"
  }
  user_data  = <<-EOT
    #cloud-config
    users:
      - name: deploy
        groups: sudo
        shell: /bin/bash
        sudo: ['ALL=(ALL) NOPASSWD:ALL']
        ssh-authorized-keys:
          - ${var.ssh_public_key}
    packages:
      - apt-transport-https
      - ca-certificates
      - curl
      - software-properties-common
      - python3
      - python3-pip
      - python3-venv
      - git
    runcmd:
      # Wait for network
      - sleep 10
      # Add swap
      - fallocate -l 2G /swapfile || true
      - chmod 600 /swapfile || true
      - mkswap /swapfile || true
      - swapon /swapfile || true
      - echo '/swapfile none swap sw 0 0' >> /etc/fstab
      # Install Docker
      - apt-get update -y >> /var/log/user-data.log 2>&1
      - apt-get install -y ca-certificates curl >> /var/log/user-data.log 2>&1
      - install -m 0755 -d /etc/apt/keyrings || true
      - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg >> /var/log/user-data.log 2>&1
      - chmod a+r /etc/apt/keyrings/docker.gpg
      - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      - apt-get update -y >> /var/log/user-data.log 2>&1
      - apt-get install -y docker-ce docker-ce-cli containerd.io >> /var/log/user-data.log 2>&1
      - systemctl enable docker >> /var/log/user-data.log 2>&1
      - systemctl start docker >> /var/log/user-data.log 2>&1
      - usermod -aG docker deploy >> /var/log/user-data.log 2>&1
      # Install Docker Compose plugin
      - mkdir -p /usr/libexec/docker/cli-plugins || true
      - curl -SL https://github.com/docker/compose/releases/download/v2.24.7/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose >> /var/log/user-data.log 2>&1
      - chmod +x /usr/libexec/docker/cli-plugins/docker-compose || true
      # Configure firewall
      - ufw allow OpenSSH >> /var/log/user-data.log 2>&1
      - ufw allow 80 >> /var/log/user-data.log 2>&1
      - ufw allow 443 >> /var/log/user-data.log 2>&1
      - ufw --force enable >> /var/log/user-data.log 2>&1
      # Create deployment directory
      - mkdir -p /opt/projectmeats/env >> /var/log/user-data.log 2>&1
      - chown -R deploy:deploy /opt/projectmeats >> /var/log/user-data.log 2>&1
      - chmod 700 /opt/projectmeats/env >> /var/log/user-data.log 2>&1
      # Log completion
      - echo "Cloud-init completed" >> /var/log/user-data.log
  EOT
  depends_on = [time_sleep.wait_between_droplets]
}

# Upload SSH key to Digital Ocean
resource "digitalocean_ssh_key" "deploy_key" {
  name       = "projectmeats-deploy-key"
  public_key = var.ssh_public_key
}

# PostgreSQL 15 database for UAT
resource "digitalocean_database_cluster" "projectmeats_uat_db" {
  name            = "projectmeats-uat-db"
  engine          = "pg"
  version         = "15"
  size            = "db-s-1vcpu-1gb"
  region          = var.region
  node_count      = 1
  storage_size_mib = 10240
  timeouts {
    create = "90m"
  }
}

resource "digitalocean_database_db" "projectmeats_uat_db_name" {
  cluster_id = digitalocean_database_cluster.projectmeats_uat_db.id
  name       = "projectmeats"
}

resource "digitalocean_database_user" "projectmeats_uat_db_user" {
  cluster_id = digitalocean_database_cluster.projectmeats_uat_db.id
  name       = "meatsuser"
}

resource "digitalocean_database_firewall" "projectmeats_uat_db_firewall" {
  cluster_id = digitalocean_database_cluster.projectmeats_uat_db.id
  rule {
    type  = "ip_addr"
    value = digitalocean_droplet.projectmeats_uat.ipv4_address
  }
}

# PostgreSQL 15 database for PROD
resource "digitalocean_database_cluster" "projectmeats_prod_db" {
  name            = "projectmeats-prod-db"
  engine          = "pg"
  version         = "15"
  size            = "db-s-1vcpu-1gb"
  region          = var.region
  node_count      = 1
  storage_size_mib = 10240
  timeouts {
    create = "90m"
  }
}

resource "digitalocean_database_db" "projectmeats_prod_db_name" {
  cluster_id = digitalocean_database_cluster.projectmeats_prod_db.id
  name       = "projectmeats"
}

resource "digitalocean_database_user" "projectmeats_prod_db_user" {
  cluster_id = digitalocean_database_cluster.projectmeats_prod_db.id
  name       = "meatsuser"
}

resource "digitalocean_database_firewall" "projectmeats_prod_db_firewall" {
  cluster_id = digitalocean_database_cluster.projectmeats_prod_db.id
  rule {
    type  = "ip_addr"
    value = digitalocean_droplet.projectmeats_prod.ipv4_address
  }
}

# Configure DNS records
resource "digitalocean_record" "dev_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "dev"
  value  = digitalocean_droplet.projectmeats_dev.ipv4_address
  ttl    = 300
}

resource "digitalocean_record" "uat_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "uat"
  value  = digitalocean_droplet.projectmeats_uat.ipv4_address
  ttl    = 300
  depends_on = [time_sleep.wait_between_droplets]
}

resource "digitalocean_record" "prod_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "prod"
  value  = digitalocean_droplet.projectmeats_prod.ipv4_address
  ttl    = 300
  depends_on = [time_sleep.wait_between_droplets]
}