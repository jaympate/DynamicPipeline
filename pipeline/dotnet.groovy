pipeline {
    agent any
     /*triggers {
        githubPush()
      }*/
    stages {
        stage('Code Check Out') {
            steps {
                git branch: 'main', credentialsId: env.Credential_ID, url: ${APP_URL}
                echo("${APP_URL} Repository was successfully cloned.")
                echo("${BUILD_NAME} for ${APP_URL}")
                }
            }
        stage('Restore packages'){
           steps{
               echo ("Restore package")
               sh 'dotnet restore ${FILE_NAME}.sln'
            }
         }        
        /*stage('Clean'){
           steps{
               echo ("Clean package")
               sh 'dotnet clean ${FILE_NAME}.sln --configuration Release'
            }
         }
        stage('Build'){
           steps{
               sh 'dotnet build ${FILE_NAME}.sln --configuration Release --no-restore'
            }
         }
        stage('Test: Unit Test'){
           steps {
                sh 'dotnet test XUnitTestProject/XUnitTestProject.csproj --configuration Release --no-restore'
             }
          }
        stage('Publish'){
             steps{
               sh 'dotnet publish ${FILE_NAME}/${FILE_NAME}.csproj --configuration Release --no-restore'
             }
        }*/ 
    }
}
