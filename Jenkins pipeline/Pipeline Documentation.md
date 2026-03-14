Jenkins Pipeline – Jenkinsfile Documentation
File: 
Jenkinsfile
 Repository: HarrishC/jenkins_pipepline_testing Date: 14 March 2026

Overview
This is a Declarative Jenkins Pipeline written in Groovy. It automates the process of:

Checking out source code from GitHub
Running a deployment check
Requiring manual approval before proceeding
Connecting to a SQL Server database and executing a specified SQL file fetched from a separate GitHub repository
Notifying the team by email after every run
1. Agent
groovy
agent any
Instructs Jenkins to run this pipeline on any available agent/node.

2. Environment Variables
groovy
environment {
    DB_CREDS = credentials('jenkins-sql-creds')
    DB_NAME  = 'jenkinsTesting'
    MSSQL_CONNECTION_STRING = "Server=localhost\\SQLEXPRESS;..."
}
Variable	Source	Purpose
DB_CREDS	Jenkins Credentials Store (jenkins-sql-creds)	Injects DB_CREDS_USR (username) and DB_CREDS_PSW (password) as env vars
DB_NAME	Hardcoded	Name of the SQL Server database
MSSQL_CONNECTION_STRING	Constructed	Full connection string (used for reference)
3. Parameters
These are inputs the user provides each time they trigger a build in Jenkins.

Parameter	Type	Default	Description
DEPLOY_TO_PROD	Boolean	false	Gate to allow or block the Deploy stage
PrintingDifferentValue	String	test	A test value printed during Deploy
GitLink	String	(empty)	GitHub folder URL of the SQL scripts repo (e.g. https://github.com/user/repo/tree/main/sql)
SQL_FILE_NAME	String	(empty)	Exact filename of the SQL script to execute (e.g. create_tables.sql)
4. Stages
Stage 1 — Checkout
groovy
git branch: 'main', url: 'https://github.com/HarrishC/jenkins_pipepline_testing.git'
Clones the Jenkinsfile's own repository (the pipeline config repo) from the main branch into the Jenkins workspace.

Stage 2 — Build
groovy
echo "Build number : ${BUILD_NUMBER}"
A simple placeholder stage that prints the current Jenkins build number. This is where compilation or artifact-building steps would go.

Stage 3 — Deploy
Controlled by two parameter checks:

Check 1 — Production gate:

if DEPLOY_TO_PROD == true  → proceed (prints "Hello World!")
else                        → fail pipeline immediately
Check 2 — Value validation:

if PrintingDifferentValue is empty → fail
else                                → print the value
This stage acts as a conditional deployment gate. Actual deployment commands would replace the echo 'Hello World!' line.

Stage 4 — Approval
Pauses the pipeline and waits for a human to approve or reject before continuing.

Presents a prompt: "Do you want to proceed with the manual deployment?"
Requires the approver to type Y or N in the APPROVAL_REASON field
Y → pipeline continues
N → pipeline is aborted with an error
Anything else → pipeline fails
This prevents accidental or unauthorised deployments reaching the database execution stage.

Stage 5 — Check DB Connection
This is the most complex stage. It has two sub-tasks:

5a. Verify Database Connectivity
sqlcmd -S localhost\SQLEXPRESS -d jenkinsTesting -U <user> -P <pass> > nul 2>&1
Runs a silent sqlcmd connection test. If the exit code is non-zero, the pipeline fails immediately with a message to check the connection string and server status.

5b. Fetch and Execute SQL File from GitHub
Step 1 — Parse the GitHub URL (in Groovy)

The GitLink parameter (e.g. https://github.com/HarrishC/sql-repo/tree/main/scripts) is parsed to extract:

owner → HarrishC
repo → sql-repo
branch → main
folder → scripts
filePath → scripts/create_tables.sql (folder + SQL_FILE_NAME)
Step 2 — Checkout the SQL repo (sparse)

Jenkins' native GitSCM checkout is used with:

SparseCheckoutPaths — only downloads the specific folder containing the SQL file, not the entire repository (faster)
CloneOption depth: 1 — shallow clone (only latest commit, no full history)
Credentials from jenkins-github-creds — handled entirely by Jenkins; no passwords in URLs
Step 3 — Copy SQL file to workspace

batch
copy /Y "<src>" "<WORKSPACE>\queries\<filename>"
Creates the queries folder if it doesn't exist, then copies the SQL file out of the cloned repo into the workspace. The cloned repo folder is then deleted.

Step 4 — Print and Execute SQL

Reads and prints the SQL file content to the Jenkins console log for audit/visibility
Executes it against the SQL Server database using sqlcmd:
sqlcmd -S localhost\SQLEXPRESS -d jenkinsTesting -U <user> -P <pass> -i "<file>"
Stage 6 — Clean Workspace
groovy
cleanWs()
Deletes all files in the Jenkins workspace after the pipeline completes, keeping the agent clean for the next build.

5. Post — Always (Email Notification)
After every build (success or failure), an email is sent:

Field	Value
To	
harrishgamer13@gmail.com
Subject	<result> - <job name> #<build number>
Body	Build result, build number, and a link to the build URL
Attachment	Full Jenkins console log
Recipients	Also notifies whoever triggered the build
6. Credentials Used
Credential ID	Type	Used For
jenkins-sql-creds	Username + Password	SQL Server login — injected as DB_CREDS_USR / DB_CREDS_PSW
jenkins-github-creds	Username + Password	GitHub PAT for cloning the SQL scripts repo
7. Pipeline Flow Diagram
Trigger Build (with parameters)
        │
        ▼
  ┌─────────────┐
  │  Checkout   │  Clone Jenkinsfile repo (main branch)
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │    Build    │  Print build number
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │   Deploy    │  Check DEPLOY_TO_PROD & PrintingDifferentValue
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │  Approval   │  Wait for human Y/N input
  └──────┬──────┘
         │
  ┌──────▼──────────────────────────────────┐
  │         Check DB Connection             │
  │  1. Test SQL Server connectivity        │
  │  2. Parse GitLink URL                   │
  │  3. Sparse-checkout SQL repo            │
  │  4. Copy SQL_FILE_NAME to workspace     │
  │  5. Print SQL content                   │
  │  6. Execute via sqlcmd                  │
  └──────┬──────────────────────────────────┘
         │
  ┌──────▼──────┐
  │Clean Wspace │  Delete workspace files
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │Email Report │  Always sent (pass or fail)
  └─────────────┘
8. Common Errors & Solutions
Error	Cause	Fix
Deploy to production is set to false. Failing the pipeline.	DEPLOY_TO_PROD unchecked	Tick the checkbox when triggering the build
Failed to connect to the database	SQL Server down or wrong credentials	Check jenkins-sql-creds and SQL Server service
Authentication failed	GitHub PAT expired or wrong scope	Regenerate PAT with repo scope at github.com/settings/tokens
File not found in repo	Wrong SQL_FILE_NAME or GitLink folder	Verify the exact filename and folder path in GitHub
Failed to execute SQL	SQL syntax error in the file	Check the printed SQL content in the console log
