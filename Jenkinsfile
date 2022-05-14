#!groovy

// Environment variables
def alpine_version = "3.14"
def python_version = "3.9"
def docker_builder_image = "drtuxwang/debian-docker:stable"
String branch_name = env.JOB_NAME - "system-config-"

// Create jobs pipeline

pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        parallelsAlwaysFailFast()
        timeout(time: 60, unit: "MINUTES")
    }

    parameters {
        string(name: "DOCKER_REG", description: "Docker Registry to use.", defaultValue: "docker.io")
    }

    stages {
        stage("Info") {
            steps {
                echo "Job Name:     ${env.JOB_NAME}"
                echo "Build Number: ${env.BUILD_NUMBER}"
                echo "Branch Name:  ${branch_name}"
            }
        }

        stage("Checkout") {
            steps {
                sh """
                    git clone --depth 1 --branch ${branch_name} https://github.com/drtuxwang/system-config.git system-config ||:
                    cd system-config
                    git pull --no-tags origin ${branch_name} || (git gc --prune=now && git pull --no-tags origin ${params.BRANCH})
                """
            }
        }

        stage ("Build") {
            parallel {
                stage ("Build_Alpine") {
                    stages {
                        stage ("Alpine_Image") {
                            agent {
                                docker {
                                    image "${params.DOCKER_REG}/${docker_builder_image}"
                                    reuseNode true
                                    alwaysPull false
                                }
                            }
                            steps {
                                sh """
                                    cd system-config
                                    make -C docker/alpine-${alpine_version} build
                                    make -C docker/alpine-${alpine_version} version
                                """
                            }
                        }
                    }
                }
                stage ("Build_Python") {
                    stages {
                        stage ("Python_Image") {
                            agent {
                                docker {
                                    image "${params.DOCKER_REG}/${docker_builder_image}"
                                    reuseNode true
                                    alwaysPull false
                                }
                            }
                            steps {
                                sh """
                                    cd system-config
                                    make -C docker/python-${python_version} build
                                    make -C docker/python-${python_version} version
                                """
                            }
                        }
                        stage ("Python_Test") {
                            agent {
                                docker {
                                    image "${params.DOCKER_REG}/drtuxwang/python-dev:${python_version}-slim-bullseye"
                                    reuseNode true
                                    alwaysPull false
                                }
                            }
                            steps {
                                sh """
                                    cd system-config
                                    make install test
                                """
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

    post {
        always {
            sh "echo \"Pipeline cleanup...\" ||:"
        }
    }
}
