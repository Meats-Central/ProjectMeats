output "dev_droplet_ip" {
  description = "Public IP of DEV droplet"
  value       = digitalocean_droplet.projectmeats_dev.ipv4_address
}

output "uat_droplet_ip" {
  description = "Public IP of UAT droplet"
  value       = digitalocean_droplet.projectmeats_uat.ipv4_address
}

output "prod_droplet_ip" {
  description = "Public IP of PROD droplet"
  value       = digitalocean_droplet.projectmeats_prod.ipv4_address
}

output "dev_domain" {
  description = "DEV subdomain"
  value       = "dev.${var.domain_name}"
}

output "uat_domain" {
  description = "UAT subdomain"
  value       = "uat.${var.domain_name}"
}

output "prod_domain" {
  description = "PROD subdomain"
  value       = "prod.${var.domain_name}"
}