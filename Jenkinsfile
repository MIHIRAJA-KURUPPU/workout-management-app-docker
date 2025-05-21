pipeline {
    agent any

    environment {
        GITHUB_REPO = 'https://github.com/MIHIRAJA-KURUPPU/workout-management-app-docker'
        DOCKER_IMAGE = 'mihirajakuruppu123/workout-app-new'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code from: ${GITHUB_REPO}"
                checkout scm
                sh 'ls -la'  // List files after checkout
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
