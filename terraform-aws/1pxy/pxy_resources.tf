resource "aws_instance" "pxy_instance" {
    ami = "${lookup(var.pxy_ami_map, var.region)}"
    instance_type = "${lookup(var.pxy_type_map, var.run_mode)}"
    security_groups = ["${split(",", lookup(var.pxy_sg_map, var.region))}"]
    subnet_id = "${lookup(var.pxy_sn_map, var.region)}"

    tags = {
        stackname = "${var.stackname}"
        class = "pxy"
        cluster = "aws-dev1"
    }
}
