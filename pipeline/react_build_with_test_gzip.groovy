timeout(5) {
  node("master") {
    stage("Code Check Out") {
      git branch: 'main', credentialsId: env.Credential_ID, url: 'https://github.com/fsawscoe/ReactApplication.git'
      echo("${GIT_URL} Repository was successfully cloned.")
    }
	
    stage("Build Node Modules") {
      nodejs('Node') {
      sh 'npm install'
    }
      echo("Node Modules installed successully")
    }
	  
    stage("Test the React Application") {
      nodejs('Node') {
      sh 'npm test'
    }
      echo("React Application is Built Successfully")
    }	 
	
    stage("Build/Package the React Application") {
      nodejs('Node') {
      sh 'npm run build'
    }
      echo("React Application is Built Successfully")
    }

 
    stage("Gzip the React Build") {
      sh("gzip -r ./build")
      echo("React Application is Built & Compressed Successfully")
    }
    
  }
}
