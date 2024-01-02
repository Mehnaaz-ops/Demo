resource "openstack_compute_instance_v2" "vsm-instance" {
  count             = var.num_vsm_nodes
  name              = "${var.vsm_hostname}${count.index}.${var.dns_name}"
  key_pair          = var.sos_keypair
  flavor_name       = var.vsm_flavor  
  security_groups   = ["default", openstack_compute_secgroup_v2.vsm_secgroup.name]

  image_name        = var.host_image

  network {
    uuid = var.network_uuid
  }

  lifecycle {
    ignore_changes = [image_name]
  }
  
  provisioner "local-exec" {
    command = "echo '[swarm]\n${self.access_ip_v4}' > ../playbooks/inventories/${var.vsm_hostname}${count.index}"
    interpreter = ["/bin/bash", "-c"]
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine",
      "sudo yum update -y",
      "sudo yum install -y yum-utils device-mapper-persistent-data lvm2",
      "sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
      "sudo yum install -y docker-ce docker-ce-cli containerd.io",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "sudo wget https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 -O /usr/bin/jq"
    ]

    connection {
      type        = "ssh"
      user        = "centos"
      private_key = file("~/.ssh/crkey")
      host        = "${self.access_ip_v4}"
    }
  }
}

output "vsm" {
  value = openstack_compute_instance_v2.vsm-instance.*.access_ip_v4
}
