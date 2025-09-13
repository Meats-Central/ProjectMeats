# Define Digital Ocean droplets for DEV, UAT, and PROD
resource "digitalocean_droplet" "projectmeats_dev" {
  name       = "projectmeats-dev"
  region     = var.region
  size       = "s-1vcpu-1gb"  # Smaller for DEV to save cost
  image      = "ubuntu-22-04-x64"
  ssh_keys   = [digitalocean_ssh_key.deploy_key.fingerprint]
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
      # Install Docker from official repository
      - apt-get update
      - apt-get install -y ca-certificates curl
      - install -m 0755 -d /etc/apt/keyrings
      - curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
      - chmod a+r /etc/apt/keyrings/docker.asc
      - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      - apt-get update
      - apt-get install -y docker-ce docker-ce-cli containerd.io
      - systemctl enable docker
      - systemctl start docker
      # Install Docker Compose plugin
      - mkdir -p /usr/libexec/docker/cli-plugins
      - curl -SL https://github.com/docker/compose/releases/download/v2.39.1/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
      - chmod +x /usr/libexec/docker/cli-plugins/docker-compose
      - usermod -aG docker deploy
      # Configure firewall
      - ufw allow OpenSSH
      - ufw allow 80
      - ufw allow 443
  EOT
}

resource "digitalocean_droplet" "projectmeats_uat" {
  name       = "projectmeats-uat"
  region     = var.region
  size       = "s-2vcpu-2gb"  # Medium for UAT
  image      = "ubuntu-22-04-x64"
  ssh_keys   = [digitalocean_ssh_key.deploy_key.fingerprint]
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
      # Install Docker from official repository
      - apt-get update
      - apt-get install -y ca-certificates curl
      - install -m 0755 -d /etc/apt/keyrings
      - curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
      - chmod a+r /etc/apt/keyrings/docker.asc
      - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      - apt-get update
      - apt-get install -y docker-ce docker-ce-cli containerd.io
      - systemctl enable docker
      - systemctl start docker
      # Install Docker Compose plugin
      - mkdir -p /usr/libexec/docker/cli-plugins
      - curl -SL https://github.com/docker/compose/releases/download/v2.39.1/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
      - chmod +x /usr/libexec/docker/cli-plugins/docker-compose
      - usermod -aG docker deploy
      # Configure firewall
      - ufw allow OpenSSH
      - ufw allow 80
      - ufw allow 443
      - ufw --force enable
  EOT
}

resource "digitalocean_droplet" "projectmeats_prod" {
  name       = "projectmeats-prod"
  region     = var.region
  size       = "s-4vcpu-8gb"  # Larger for PROD
  image      = "ubuntu-22-04-x64"
  ssh_keys   = [digitalocean_ssh_key.deploy_key.fingerprint]
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
      # Install Docker from official repository
      - apt-get update
      - apt-get install -y ca-certificates curl
      - install -m 0755 -d /etc/apt/keyrings
      - curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
      - chmod a+r /etc/apt/keyrings/docker.asc
      - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      - apt-get update
      - apt-get install -y docker-ce docker-ce-cli containerd.io
      - systemctl enable docker
      - systemctl start docker
      # Install Docker Compose plugin
      - mkdir -p /usr/libexec/docker/cli-plugins
      - curl -SL https://github.com/docker/compose/releases/download/v2.39.1/docker-compose-linux-$(uname -m) -o /usr/libexec/docker/cli-plugins/docker-compose
      - chmod +x /usr/libexec/docker/cli-plugins/docker-compose
      - usermod -aG docker deploy
      # Configure firewall
      - ufw allow OpenSSH
      - ufw allow 80
      - ufw allow 443
      - ufw --force enable
  EOT
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
  storage_size_mib = 10240  # 10 GiB
  timeouts {
    create = "90m"  # Extended timeout for provisioning
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
  storage_size_mib = 10240  # 10 GiB
  timeouts {
    create = "90m"  # Extended timeout for provisioning
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

# Configure DNS records (ensure domain is added in DO DNS)
resource "digitalocean_record" "dev_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "dev"
  value  = digitalocean_droplet.projectmeats_dev.ipv4_address
  ttl    = 300
}
resource "digitalocean_record" "api_dev_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "api-dev"
  value  = digitalocean_droplet.projectmeats_dev.ipv4_address
  ttl    = 300
}

resource "digitalocean_record" "uat_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "uat"
  value  = digitalocean_droplet.projectmeats_uat.ipv4_address
  ttl    = 300
}
resource "digitalocean_record" "api_uat_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "api-uat"
  value  = digitalocean_droplet.projectmeats_uat.ipv4_address
  ttl    = 300
}

resource "digitalocean_record" "prod_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "@"
  value  = digitalocean_droplet.projectmeats_prod.ipv4_address
  ttl    = 300
}
resource "digitalocean_record" "api_prod_dns" {
  domain = var.domain_name
  type   = "A"
  name   = "api"
  value  = digitalocean_droplet.projectmeats_prod.ipv4_address
  ttl    = 300
}