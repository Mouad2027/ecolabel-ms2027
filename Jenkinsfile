pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = credentials('docker-registry-credentials')
        REGISTRY_URL = "${env.REGISTRY_URL ?: 'docker.io'}"
        IMAGE_PREFIX = "${env.IMAGE_PREFIX ?: 'ecolabel'}"
        POSTGRES_PASSWORD = credentials('postgres-password')
        MINIO_ROOT_PASSWORD = credentials('minio-password')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    env.BUILD_VERSION = "${env.BUILD_NUMBER}-${env.GIT_COMMIT_SHORT}"
                }
            }
        }
        
        stage('Lint & Static Analysis') {
            parallel {
                stage('Lint parser-produit') {
                    steps {
                        dir('parser-produit') {
                            sh '''
                                pip install flake8 black isort --quiet
                                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                                black --check . || true
                            '''
                        }
                    }
                }
                stage('Lint nlp-ingredients') {
                    steps {
                        dir('nlp-ingredients') {
                            sh '''
                                pip install flake8 black isort --quiet
                                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                                black --check . || true
                            '''
                        }
                    }
                }
                stage('Lint lca-lite') {
                    steps {
                        dir('lca-lite') {
                            sh '''
                                pip install flake8 black isort --quiet
                                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                                black --check . || true
                            '''
                        }
                    }
                }
                stage('Lint scoring') {
                    steps {
                        dir('scoring') {
                            sh '''
                                pip install flake8 black isort --quiet
                                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                                black --check . || true
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build parser-produit') {
                    steps {
                        script {
                            docker.build("${IMAGE_PREFIX}/parser-produit:${BUILD_VERSION}", "./parser-produit")
                        }
                    }
                }
                stage('Build nlp-ingredients') {
                    steps {
                        script {
                            docker.build("${IMAGE_PREFIX}/nlp-ingredients:${BUILD_VERSION}", "./nlp-ingredients")
                        }
                    }
                }
                stage('Build lca-lite') {
                    steps {
                        script {
                            docker.build("${IMAGE_PREFIX}/lca-lite:${BUILD_VERSION}", "./lca-lite")
                        }
                    }
                }
                stage('Build scoring') {
                    steps {
                        script {
                            docker.build("${IMAGE_PREFIX}/scoring:${BUILD_VERSION}", "./scoring")
                        }
                    }
                }
                stage('Build provenance') {
                    steps {
                        script {
                            docker.build("${IMAGE_PREFIX}/provenance:${BUILD_VERSION}", "./provenance")
                        }
                    }
                }
                stage('Build widget-api') {
                    steps {
                        script {
                            docker.build("${IMAGE_PREFIX}/widget-api:${BUILD_VERSION}", "./widget-api/backend")
                        }
                    }
                }
            }
        }
        
        stage('Run Unit Tests') {
            steps {
                script {
                    // Start infrastructure services for tests
                    sh 'docker-compose up -d postgres minio minio-init'
                    sh 'sleep 15' // Wait for services to be ready
                    
                    // Run tests for each microservice
                    def services = ['parser-produit', 'nlp-ingredients', 'lca-lite', 'scoring']
                    
                    services.each { service ->
                        echo "Running tests for ${service}..."
                        sh """
                            docker run --rm \
                                --network ecolabel-network \
                                -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/${service.replace('-', '_')}_db \
                                ${IMAGE_PREFIX}/${service}:${BUILD_VERSION} \
                                pytest tests/ -v --junitxml=/tmp/test-results-${service}.xml || true
                        """
                    }
                }
            }
            post {
                always {
                    sh 'docker-compose down -v || true'
                }
            }
        }
        
        stage('Integration Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    sh 'docker-compose up -d'
                    sh 'sleep 30' // Wait for all services to be ready
                    
                    // Health checks
                    sh '''
                        curl -f http://localhost:8001/health || exit 1
                        curl -f http://localhost:8002/health || exit 1
                        curl -f http://localhost:8003/health || exit 1
                        curl -f http://localhost:8004/health || exit 1
                        curl -f http://localhost:8005/health || exit 1
                    '''
                    
                    // Run integration tests
                    sh '''
                        # Test product parsing endpoint
                        curl -X POST http://localhost:8001/api/v1/parse/text \
                            -H "Content-Type: application/json" \
                            -d '{"text": "Test product"}' || true
                        
                        # Test NLP extraction endpoint
                        curl -X POST http://localhost:8002/api/v1/extract \
                            -H "Content-Type: application/json" \
                            -d '{"text": "sucre, farine, eau"}' || true
                    '''
                }
            }
            post {
                always {
                    sh 'docker-compose down -v || true'
                }
            }
        }
        
        stage('Security Scan') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def services = ['parser-produit', 'nlp-ingredients', 'lca-lite', 'scoring', 'provenance', 'widget-api']
                    
                    services.each { service ->
                        sh """
                            docker run --rm \
                                -v /var/run/docker.sock:/var/run/docker.sock \
                                aquasec/trivy:latest image \
                                --severity HIGH,CRITICAL \
                                --exit-code 0 \
                                ${IMAGE_PREFIX}/${service}:${BUILD_VERSION} || true
                        """
                    }
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    tag pattern: "v\\d+\\.\\d+\\.\\d+", comparator: "REGEXP"
                }
            }
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY_URL}", 'docker-registry-credentials') {
                        def services = ['parser-produit', 'nlp-ingredients', 'lca-lite', 'scoring', 'provenance', 'widget-api']
                        
                        services.each { service ->
                            def image = docker.image("${IMAGE_PREFIX}/${service}:${BUILD_VERSION}")
                            image.push()
                            image.push('latest')
                            
                            // Tag with version if this is a release
                            if (env.TAG_NAME) {
                                image.push(env.TAG_NAME)
                            }
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    echo "Deploying to staging environment..."
                    // Add your staging deployment commands here
                    // Example: kubectl apply, docker stack deploy, etc.
                    sh '''
                        # Example: Update staging with new images
                        # docker-compose -f docker-compose.staging.yml pull
                        # docker-compose -f docker-compose.staging.yml up -d
                        echo "Staging deployment placeholder"
                    '''
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
                parameters {
                    choice(name: 'DEPLOY_CONFIRM', choices: ['Yes', 'No'], description: 'Confirm production deployment')
                }
            }
            steps {
                script {
                    if (params.DEPLOY_CONFIRM == 'Yes') {
                        echo "Deploying to production environment..."
                        // Add your production deployment commands here
                        sh '''
                            # Example: Update production with new images
                            # docker-compose -f docker-compose.prod.yml pull
                            # docker-compose -f docker-compose.prod.yml up -d
                            echo "Production deployment placeholder"
                        '''
                    } else {
                        echo "Production deployment cancelled"
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
            sh 'docker system prune -f || true'
        }
        success {
            echo "Pipeline completed successfully!"
            // Uncomment to enable Slack notifications
            // slackSend(color: 'good', message: "Build ${env.BUILD_NUMBER} succeeded for ${env.JOB_NAME}")
        }
        failure {
            echo "Pipeline failed!"
            // Uncomment to enable Slack notifications
            // slackSend(color: 'danger', message: "Build ${env.BUILD_NUMBER} failed for ${env.JOB_NAME}")
        }
    }
}
