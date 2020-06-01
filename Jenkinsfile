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
                stage ("Alpine") {
                    agent any
                    stages {
                        stage ("Build") {
                            steps {
                                sh "make -C docker/alpine-3.10 build"
                                sh "make -C docker/alpine-3.10 version"
                            }
                        }
                    }
                }
                stage ("Python") {
                    agent any
                    stages {
                        stage ("Build") {
                            steps {
                                sh "make -C docker/python-3.6 build"
                                sh "make -C docker/python-3.6 version"
                            }
                        }
                        stage ("Test") {
                            agent {
                                docker {
                                    image 'drtuxwang/python:latest'
                                    args '--network=host'
                                    reuseNode true
                                    alwaysPull false
                                }
                            }
                            steps {
                                sh "make install test"
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
    }
}
