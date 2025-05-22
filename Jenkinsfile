// should be added to the git repository 


pipeline {
    agent any

    environment {
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code from: ${params.GITHUB_REPO}"
                checkout scm
                sh 'ls -la'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${params.DOCKER_IMAGE}:${env.DOCKER_TAG}"
                    sh """
                        docker version
                        docker build -t ${params.DOCKER_IMAGE}:${env.DOCKER_TAG} .
                    """
                    echo "Docker image build completed: ${params.DOCKER_IMAGE}:${env.DOCKER_TAG}"
                }
            }
        }
        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "Logging into Docker Hub and pushing image..."
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                            docker push ${params.DOCKER_IMAGE}:${env.DOCKER_TAG}
                        """
                    }
                    echo "Image pushed successfully: ${params.DOCKER_IMAGE}:${env.DOCKER_TAG}"
                }
            }
        }
        stage('Deploy to OCI Instance') {
            steps {
                script {
                    echo "Deploying application to OCI instance..."
                    withCredentials([
                        sshUserPrivateKey(credentialsId: 'oci-ssh-key', keyFileVariable: 'SSH_KEY'),
                        usernamePassword(credentialsId: 'postgres-creds', usernameVariable: 'POSTGRES_USER', passwordVariable: 'POSTGRES_PASSWORD')
                    ]) {
                        // Create deployment script
                        writeFile file: 'deploy.sh', text: """#!/bin/bash
                        # Set environment variables
                        export DOCKER_IMAGE=${params.DOCKER_IMAGE}
                        export DOCKER_TAG=${env.DOCKER_TAG}
                        export POSTGRES_VOLUME=${params.POSTGRES_VOLUME}
                        export IMAGE_VOLUME=${params.IMAGE_VOLUME}
                        export DOCKER_NETWORK=${params.DOCKER_NETWORK}
                        export POSTGRES_CONTAINER_NAME=${params.POSTGRES_CONTAINER_NAME}
                        export APP_CONTAINER_NAME=${params.APP_CONTAINER_NAME}
                        export POSTGRES_DB=${params.POSTGRES_DB}
                        export POSTGRES_IMAGE=${params.POSTGRES_IMAGE}
                        export POSTGRES_USER=\${1}
                        export POSTGRES_PASSWORD=\${2}

                        # Login to Docker Hub
                        echo \${3} | docker login -u \${4} --password-stdin

                        # Create necessary volumes and network
                        docker volume create \${POSTGRES_VOLUME} || true
                        docker volume create \${IMAGE_VOLUME} || true
                        docker network inspect \${DOCKER_NETWORK} >/dev/null 2>&1 || docker network create --driver bridge \${DOCKER_NETWORK}

                        # Deploy PostgreSQL container
                        docker rm -f \${POSTGRES_CONTAINER_NAME} || true
                        docker run -d \\
                            --name \${POSTGRES_CONTAINER_NAME} \\
                            --network \${DOCKER_NETWORK} \\
                            -e POSTGRES_USER=\${POSTGRES_USER} \\
                            -e POSTGRES_PASSWORD=\${POSTGRES_PASSWORD} \\
                            -e POSTGRES_DB=\${POSTGRES_DB} \\
                            -p 5434:5432 \\
                            -v \${POSTGRES_VOLUME}:/var/lib/postgresql/data \\
                            \${POSTGRES_IMAGE}

                        # Pull and run the application container
                        docker rm -f \${APP_CONTAINER_NAME} || true
                        docker pull \${DOCKER_IMAGE}:\${DOCKER_TAG}
                        docker run -d \\
                            --name \${APP_CONTAINER_NAME} \\
                            --network \${DOCKER_NETWORK} \\
                            -e DB_HOST=\${POSTGRES_CONTAINER_NAME} \\
                            -e DB_PORT=5432 \\
                            -e DB_NAME=\${POSTGRES_DB} \\
                            -e DB_USER=\${POSTGRES_USER} \\
                            -e DB_PASSWORD=\${POSTGRES_PASSWORD} \\
                            -e DATABASE_URL="postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@\${POSTGRES_CONTAINER_NAME}:5432/\${POSTGRES_DB}" \\
                            -p 5000:5000 \\
                            -v \${IMAGE_VOLUME}:/app/images \\
                            \${DOCKER_IMAGE}:\${DOCKER_TAG}

                        echo "Deployment completed successfully!"
                        """

                        // Make the script executable
                        sh "chmod +x deploy.sh"

                        // Copy the deployment script to the OCI instance
                        sh "scp -i \${SSH_KEY} -o StrictHostKeyChecking=no deploy.sh \${params.OCI_USER}@\${params.OCI_HOST}:/tmp/deploy.sh"

                        // Execute the deployment script on the OCI instance
                        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh """
                                ssh -i \${SSH_KEY} -o StrictHostKeyChecking=no \${params.OCI_USER}@\${params.OCI_HOST} "bash /tmp/deploy.sh '\${POSTGRES_USER}' '\${POSTGRES_PASSWORD}' '\${DOCKER_PASS}' '\${DOCKER_USER}'"
                            """
                        }

                        // Remove the temporary script from OCI instance
                        sh "ssh -i \${SSH_KEY} -o StrictHostKeyChecking=no \${params.OCI_USER}@\${params.OCI_HOST} 'rm /tmp/deploy.sh'"
                    }
                }
            }
        }
    }
    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed! Please check the logs above for more details.'
        }
    }
}
