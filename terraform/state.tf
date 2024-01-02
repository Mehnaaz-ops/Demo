terraform {
  backend "swift" {
    container = "vsm-grid-terraform-state"
    archive_container = "vsm-grid-terraform-state-archive"
  }
}
