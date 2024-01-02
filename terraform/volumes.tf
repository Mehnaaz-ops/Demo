resource "openstack_blockstorage_volume_v2" "fsvol" {
  name = "pgfs"
  size = 100
}

resource "openstack_blockstorage_volume_v2" "dumpvol" {
  name = "pgdump"
  size = 60
}

resource "openstack_compute_volume_attach_v2" "pg_fs" {
  instance_id = "${openstack_compute_instance_v2.vsm-instance[3].id}"
  volume_id = "${openstack_blockstorage_volume_v2.fsvol.id}"
}

resource "openstack_compute_volume_attach_v2" "pg_dump" {
  instance_id = "${openstack_compute_instance_v2.vsm-instance[3].id}"
  volume_id = "${openstack_blockstorage_volume_v2.dumpvol.id}"
}
