variable "do_token" {
  description = "Digital Ocean Personal Access Token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "Digital Ocean region for droplets"
  type        = string
  default     = "nyc3"  # Change to your preferred region (e.g., sfo3, lon1)
}

variable "domain_name" {
  description = "Domain name for DNS records"
  type        = string
  default     = "meatscentral.com"  # Replace with your actual domain
}

variable "ssh_public_key" {
  description = "Public SSH key for deploy user"
  type        = string
}