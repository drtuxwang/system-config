resource "aws_autoscaling_group" "pxy_asg" {
    name = "${var.stackname}-stack-pxy-asg"
    vpc_zone_identifier = ["${split(",", lookup(var.pxy_sn_map, var.region))}"]
    launch_configuration = "${aws_launch_configuration.pxy_lc.name}"
    load_balancers = ["${aws_elb.pxy_lb.name}"]

    min_size = "${lookup(var.pxy_min_map, var.run_mode)}"
    max_size = "${lookup(var.pxy_max_map, var.run_mode)}"
    desired_capacity = "${lookup(var.pxy_desired_map, var.run_mode)}"

    health_check_grace_period = 300
    health_check_type = "ELB"
    force_delete = true

    tag {
        key = "stackname"
        value = "${var.stackname}"
        propagate_at_launch = true
    }
}

resource "aws_launch_configuration" "pxy_lc" {
    name = "${var.stackname}-stack-pxy-lc"
    image_id = "${lookup(var.pxy_ami_map, var.region)}"
    instance_type = "${lookup(var.pxy_type_map, var.run_mode)}"
    security_groups = ["${split(",", lookup(var.pxy_sg_map, var.region))}"]
    # key_name = "${var.keyname}"
}

resource "aws_elb" "pxy_lb" {
    name = "${var.stackname}-stack-pxy-lb"
    cross_zone_load_balancing = true
    subnets = ["${split(",", lookup(var.pxy_sn_map, var.region))}"]
    security_groups = ["${split(",", lookup(var.pxy_sg_map, var.region))}"]

    listener {
        lb_protocol = "http"
        lb_port = 80
        instance_protocol = "http"
        instance_port = 80
    }
    health_check {
        target = "TCP:22"
        healthy_threshold = 2
        unhealthy_threshold = 2
        timeout = 3
        interval = 30
    }
    connection_draining = true
    connection_draining_timeout = 400
    idle_timeout = 400

    tags {
        stackname = "${var.stackname}"
    }
}

resource "aws_autoscaling_policy" "pxy_scale_out" {
    name = "${var.stackname}-stack-pxy-scale-out"
    autoscaling_group_name = "${aws_autoscaling_group.pxy_asg.name}"
    adjustment_type = "ChangeInCapacity"
    scaling_adjustment = 1
    cooldown = 900
}

resource "aws_autoscaling_policy" "pxy_scale_in" {
    name = "${var.stackname}-stack-pxy-scale-in"
    autoscaling_group_name = "${aws_autoscaling_group.pxy_asg.name}"
    adjustment_type = "ChangeInCapacity"
    scaling_adjustment = -1
    cooldown = 900
}

resource "aws_cloudwatch_metric_alarm" "pxy_cpu_high" {
    alarm_name = "${var.stackname}-stack-pxy-cpu_high"
    alarm_description = "Scale-up if CPU > 70% for 5 minutes"
    metric_name = "CPUUtilization"
    namespace = "AWS/EC2"
    statistic = "Average"
    period = "300"
    evaluation_periods = "2"
    comparison_operator = "GreaterThanThreshold"
    threshold = "70"
    alarm_actions = ["${aws_autoscaling_policy.pxy_scale_out.arn}"]
    dimensions {
        AutoScalingGroupName = "${aws_autoscaling_group.pxy_asg.name}"
    }
}

resource "aws_cloudwatch_metric_alarm" "pxy_cpu_low" {
    alarm_name = "${var.stackname}-stack-pxy-cpu_high"
    alarm_description = "Scale-up if CPU < 20% for 5 minutes"
    metric_name = "CPUUtilization"
    namespace = "AWS/EC2"
    statistic = "Average"
    period = "300"
    evaluation_periods = "2"
    comparison_operator = "LessThanThreshold"
    threshold = "70"
    alarm_actions = ["${aws_autoscaling_policy.pxy_scale_in.arn}"]
    dimensions {
        AutoScalingGroupName = "${aws_autoscaling_group.pxy_asg.name}"
    }
}
