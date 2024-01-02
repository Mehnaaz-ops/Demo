# HOS credentials to be set on the instance
variable "sos_keypair" {
  default = "crkey"
}

variable "network_uuid" {
  default = "430e463e-0584-49ed-9ec4-917ade6137ce"
}

variable "pool" {
  default = "ext-net-LR0"
}

variable "vsm_hostname" {
  default = "vsm"
}

variable "insights_hostname" {
  default = "insights"
}

variable "num_vsm_nodes" {
  default = "5"
}

# Image to uses for instances
variable "host_image" {
  default = "CentOS-7-BaseImage"
}

# Image to uses for instances
variable "perf_image" {
  default = "CentOS-7-Current"
}


# Instance specs i.e. OpenStack flavors
variable "vsm_flavor" {
  default = "Memory1.xlarge"
}

#DNS varible names
variable "dns_name" {
  default = "infra.tssrd.hpecorp.net."
}

variable "dns_email" {
  default = "SolCX-Trishul@group.int.hpe.com"
}
  
  
variable "perf_hostname" {
  default = "perf"
}

variable "perfdb_hostname" {
  default = "perfdb"
}

variable "num_perf_nodes" {
  default = "4"
}

variable "num_perfdb_nodes" {
  default = "1"
}


# Instance specs i.e. OpenStack flavors
variable "perf_flavor" {
  default = "General1.xlarge"
}

# Instance specs i.e. OpenStack flavors
variable "perfdb_flavor" {
  default = "m1.large"
}
