pipeline {
    agent any

    environment {
        GITHUB_REPO = 'https://github.com/MIHIRAJA-KURUPPU/workout-management-app-docker'
        DOCKER_IMAGE = 'mihirajakuruppu123/workout-app-new'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        POSTGRES_VOLUME = "postgres-data-volume"
        IMAGE_VOLUME = "app-image-volume"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code from: ${GITHUB_REPO}"
                checkout scm
                sh 'ls -la'  
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh """
                        docker version
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    """
                    echo "Docker image build completed: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "Logging into Docker Hub and pushing image..."
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            echo "DockerHub Username: \$DOCKER_USER"
                            echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                            docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        """
                    }
                    echo "Image pushed successfully: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }

        stage('Prepare Docker Environment') {
            steps {
                script {
                    echo "Preparing Docker network and volume..."
                    sh """
                        docker volume create ${POSTGRES_VOLUME} || true
                        docker network inspect ${DOCKER_NETWORK} >/dev/null 2>&1 || docker network create --driver bridge ${DOCKER_NETWORK}
                    """
                    }
            }
        }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed! Please check the logs above for more details."
        }
    }
}
