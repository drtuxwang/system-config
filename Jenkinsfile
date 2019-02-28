#!groovy

// Environment variables
// BRANCH_NAME: branch being built

pipeline {
    agent any
    options {
        parallelsAlwaysFailFast()
    }
    environment {
        DOCKER_BUILD_FLAGS = "--network=host"
    }
    stages {
        stage ("Build") {
            parallel {
                stage("Ubuntu") {
                    agent any
                    stages {
                        stage ("Ubuntu (stable)") {
                            steps {
                                sh "make -C docker/ubuntu build"
                            }
                        }
                        stage ("Run tests") {
                            agent {
                                docker {
                                    image 'drtuxwang/ubuntu-python:18.04'
                                    args '--network=host'
                                    reuseNode true
                                    alwaysPull false
                                }
                            }
                            steps {
                                sh "make install test"
                            }
                        }
                        stage ("Ubuntu (32bit)") {
                            steps {
                                sh "make -C docker/ubuntu-i386 build"
                            }
                        }
                        stage ("Ubuntu (old)") {
                            steps {
                                sh "make -C docker/ubuntu-old build"
                            }
                        }
                        stage ("Ubuntu (test)") {
                            steps {
                                sh "make -C docker/ubuntu-test build"
                            }
                        }
                    }
                }
                stage("Debian") {
                    agent any
                    stages {
                        stage ("Debian (stable)") {
                            steps {
                                sh "make -C docker/debian build"
                            }
                        }
                        stage ("Debian (old)") {
                            steps {
                                sh "make -C docker/debian-old build"
                            }
                        }
                        stage ("Debian (test)") {
                            steps {
                                sh "make -C docker/debian-test build"
                            }
                        }
                    }
                }
                stage("CentOS") {
                    agent any
                    stages {
                        stage ("Centos (stable)") {
                            steps {
                                sh "make -C docker/centos build"
                            }
                        }
                        stage ("Centos (old)") {
                            steps {
                                sh "make -C docker/centos-old build"
                            }
                        }
                    }
                }
                stage ("Other") {
                    agent any
                    stages {
                        stage ("Alpine") {
                            steps {
                                sh "make -C docker/alpine build"
                            }
                        }
                        stage ("Alpine (32bit)") {
                            steps {
                                sh "make -C docker/alpine-i386 build"
                            }
                        }
                        stage ("Busybox") {
                            steps {
                                sh "make -C docker/busybox build"
                            }
                        }
                        stage ("Clearlinux") {
                            steps {
                                sh "make -C docker/clearlinux build"
                            }
                        }
                        stage ("Etcd") {
                            steps {
                                sh "make -C docker/etcd build"
                            }
                        }
                        stage ("Golang") {
                            steps {
                                sh "make -C docker/golang build"
                            }
                        }
                        stage ("Jenkins") {
                            steps {
                                sh "make -C docker/jenkins build"
                            }
                        }
                        stage ("Mongodb") {
                            steps {
                                sh "make -C docker/mongodb build"
                            }
                        }
                        stage ("Oracle XE") {
                            steps {
                                sh "make -C docker/oracle-xe build"
                            }
                        }
                        stage ("Docker Registry") {
                            steps {
                                sh "make -C docker/registry build"
                            }
                        }
                        stage ("Sudo") {
                            steps {
                                sh "make -C docker/sudo build"
                            }
                        }
                    }
                }
            }
        }
        stage ("Push Docker images") {
            when { branch "master" }
            steps {
                sh "sleep 2"
            }
        }
        stage ("Base images versions") {
            steps {
                sh "make -C docker version"
            }
        }
    }
}
