resource "openstack_dns_recordset_v2" "vsm" {
  zone_id     = "cd90b593-ec55-4038-b6c7-ae6f50671e9f"
  name        = "${var.vsm_hostname}.${var.dns_name}"
  description = "VSM"
  ttl         = 60
  type        = "A"
  records     = openstack_compute_instance_v2.vsm-instance.*.access_ip_v4
}

resource "openstack_dns_recordset_v2" "insights" {
  zone_id     = "cd90b593-ec55-4038-b6c7-ae6f50671e9f"
  name        = "${var.insights_hostname}.${var.dns_name}"
  description = "insights"
  ttl         = 60
  type        = "A"
  records     = openstack_compute_instance_v2.vsm-instance.*.access_ip_v4
}
