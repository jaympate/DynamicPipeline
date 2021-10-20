timeout(5) {
  node("master")
  tools {nodejs "node"}{
    stage("Code Check Out") {
      git branch: 'main', credentialsId: env.Credential_ID, url: 'https://github.com/jaympate/ReactApp.git'
      echo("${GIT_URL} Repository was successfully cloned.")
    }
	
    stage("Build Node Modules") {
      nodejs('node') {
      sh 'npm install'
	echo("Building node modules")
    }
     	echo("Node Modules installed successully")
    }
	
    stage("Build/Package the React Application") {
      nodejs('node') {
      sh 'npm run build'
	    
    }
      echo("React Application is Built Successfully")
    }

  }
}
