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
  value       = "${var.domain_name}"
}

output "uat_db_connection_string" {
  description = "Connection string for UAT database"
  value       = "postgres://${digitalocean_database_user.projectmeats_uat_db_user.name}:${digitalocean_database_user.projectmeats_uat_db_user.password}@${digitalocean_database_cluster.projectmeats_uat_db.host}:${digitalocean_database_cluster.projectmeats_uat_db.port}/${digitalocean_database_db.projectmeats_uat_db_name.name}"
  sensitive   = true
}

output "prod_db_connection_string" {
  description = "Connection string for PROD database"
  value       = "postgres://${digitalocean_database_user.projectmeats_prod_db_user.name}:${digitalocean_database_user.projectmeats_prod_db_user.password}@${digitalocean_database_cluster.projectmeats_prod_db.host}:${digitalocean_database_cluster.projectmeats_prod_db.port}/${digitalocean_database_db.projectmeats_prod_db_name.name}"
  sensitive   = true
}