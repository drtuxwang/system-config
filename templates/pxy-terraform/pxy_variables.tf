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

variable "pxy_min_map" {
    default = {
        dev = 1
        prod = 2
    }
}

variable "pxy_desired_map" {
    default = {
        dev = 2
        prod = 4
    }
}

variable "pxy_max_map" {
    default = {
        dev = 3
        prod = 6
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
        eu-west-1 = "subnet-85b8a5f0,subnet-d886877f,subnet-5dc85320"
        us-west-2 = "subnet-fd3979a4,subnet-58c58e6f,subnet-6ed73209"
    }
}
