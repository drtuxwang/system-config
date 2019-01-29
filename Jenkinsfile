#!groovy

// Environment variables
// BRANCH_NAME: branch being built

pipeline {
    agent any
    options {
        parallelsAlwaysFailFast()
    }
    environment {
        DOCKER_BUILD_FLAGS = '--network=host'
    }
    stages {
        stage ('Build basic images') {
            parallel {
                stage ('Busybox') {
                    steps {
                        sh "make -C docker/busybox build"
                    }
                }
                stage ('Etcd') {
                    steps {
                        sh "make -C docker/etcd build"
                    }
                }
                stage ('Golang') {
                    steps {
                        sh "make -C docker/golang build"
                    }
                }
                stage ('Jenkins') {
                    steps {
                        sh "make -C docker/jenkins build"
                    }
                }
                stage ('Mongodb') {
                    steps {
                        sh "make -C docker/mongodb build"
                    }
                }
                stage ('Oracle XE') {
                    steps {
                        sh "make -C docker/oracle-xe build"
                    }
                }
                stage ('Docker Registry') {
                    steps {
                        sh "make -C docker/registry build"
                    }
                }
                stage ('Sudo') {
                    steps {
                        sh "make -C docker/sudo build"
                    }
                }
            }
        }
        stage ('Build Linux images') {
            parallel {
                stage ('Alpine') {
                    steps {
                        sh "make -C docker/alpine build"
                    }
                }
                stage ('Alpine (32bit)') {
                    steps {
                        sh "make -C docker/alpine-i386 build"
                    }
                }
                stage ('Clearlinux') {
                    steps {
                        sh "make -C docker/clearlinux build"
                    }
                }
                stage ('Centos') {
                    steps {
                        sh "make -C docker/centos build"
                    }
                }
                stage ('Centos (old)') {
                    steps {
                        sh "make -C docker/centos-old build"
                    }
                }
                stage ('Debian') {
                    steps {
                        sh "make -C docker/debian build"
                    }
                }
                stage ('Debian (old)') {
                    steps {
                        sh "make -C docker/debian-old build"
                    }
                }
                stage ('Debian (test)') {
                    steps {
                        sh "make -C docker/debian-test build"
                    }
                }
            }
        }
        stage ('Build Ubuntu Linux images') {
            parallel {
                stage ('Ubuntu') {
                    steps {
                        sh "make -C docker/ubuntu build"
                    }
                }
                stage ('Ubuntu (32bit)') {
                    steps {
                        sh "make -C docker/ubuntu-i386 build"
                    }
                }
                stage ('Ubuntu (old)') {
                    steps {
                        sh "make -C docker/ubuntu-old build"
                    }
                }
                stage ('Ubuntu (test)') {
                    steps {
                        sh "make -C docker/ubuntu-test build"
                    }
                }
            }
        }
        stage ('Run tests') {
            steps {
                sh 'make test'
            }
        }
        stage ('Push Docker images') {
            when { branch 'master' }
            steps {
                sh 'sleep 2'
            }
        }
        stage ('Base images versions') {
            steps {
                sh "make -C docker version"
            }
        }
    }
}
