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
                                sh "make -C docker/alpine build"
                                sh "make -C docker/alpine version"
                            }
                        }
                    }
                }
                stage ("Python") {
                    agent any
                    stages {
                        stage ("Build") {
                            steps {
                                sh "make -C docker/python build"
                                sh "make -C docker/python version"
                            }
                        stage ("Test") {
                            steps {
                                sh "make -C docker/python test"
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
