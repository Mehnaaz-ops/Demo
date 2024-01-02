resource "openstack_compute_secgroup_v2" "vsm_secgroup" {
  name        = "vsm_secgroup"
  description = "VSM Security Group"

  rule {
    from_port   = 22
    to_port     = 22
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }

  rule {
    from_port   = 80
    to_port     = 80
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }

  rule {
    from_port   = 443
    to_port     = 443
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }
  
  rule {
    from_port   = 8080
    to_port     = 8090
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }
  
  rule {
    from_port   = 9300 
    to_port     = 9330
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }

}
