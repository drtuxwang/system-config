#!groovy

// Environment variables
def alpine_version = "3.17"
def python_version = "3.11"
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

    environment {
        start_time = /${sh(script: "date +%s", returnStdout: true)}/
        PYTHONDONTWRITEBYTECODE = "1"
    }

    stages {
        stage("Info") {
            options {
                timeout(time: 1, unit: 'MINUTES')
            }
            steps {
                sh "date +'Pipeline start time: %Y-%m-%d-%H:%M:%S'"
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
                            options {
                                timeout(time: 15, unit: 'MINUTES')
                            }
                            agent {
                                docker {
                                    image "${params.DOCKER_REG}/${docker_builder_image}"
                                    reuseNode true
                                    alwaysPull false
                                    args "--entrypoint="
                                }
                            }
                            steps {
                                sh """
                                    cd system-config
                                    make --no-print-directory -C docker/alpine-${alpine_version} build
                                    make --no-print-directory -C docker/alpine-${alpine_version} version
                                """
                            }
                        }
                    }
                }
                stage ("Build_Python") {
                    stages {
                        stage ("Python_Image") {
                            options {
                                timeout(time: 45, unit: 'MINUTES')
                            }
                            agent {
                                docker {
                                    image "${params.DOCKER_REG}/${docker_builder_image}"
                                    reuseNode true
                                    alwaysPull false
                                    args "--entrypoint="
                                }
                            }
                            steps {
                                sh """
                                    cd system-config
                                    make --no-print-directory -C docker/python-${python_version} build
                                    make --no-print-directory -C docker/python-${python_version} version
                                    make --no-print-directory -C docker/python-${python_version}/pip build
                                    make --no-print-directory -C docker/python-${python_version}/pip version
                                """
                            }
                        }
                        stage ("Python_Test") {
                            options {
                                timeout(time: 15, unit: 'MINUTES')
                            }
                            agent {
                                docker {
                                    image "${params.DOCKER_REG}/drtuxwang/python-pip:${python_version}"
                                    reuseNode true
                                    alwaysPull false
                                    args "--entrypoint="
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
            options {
                timeout(time: 10, unit: 'MINUTES')
            }
            when { branch "master" }
            steps {
                sh "sleep 2"
            }
        }
    }

    post {
        failure {
            echo "Cleanup Git locks..."
            sh """find \$(find -type d -name .git) -name '*.lock' -exec rm -v {} +"""
        }
        always {
            echo "Pipeline cleanup..."
            sh """
                date +"Pipeline finish time: %Y-%m-%d-%H:%M:%S"
                echo "Pipeline elapsed time: \$((\$(date +%s) - ${start_time})) seconds"
            """
        }
    }
}
