variable "pxy_ami_map" {
    default = {
        eu-west-1 = "ami-4374b732"
        us-west-2 = "ami-c1fe12a0"
    }
}

variable "pxy_type_map" {
    default = {
        dev = "t2.small"
        prod = "t2.medium"
    }
}

variable "pxy_sg_map" {
    default = {
        eu-west-1 = "sg-2bb7e1ef"
        us-west-2 = "sg-d3ac46a4"
    }
}

variable "pxy_sn_map" {
    default = {
        eu-west-1a = "subnet-85b8a5f0"
        us-west-2a = "subnet-fd3979a4"
    }
}
