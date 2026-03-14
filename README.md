# Jenkins Database Pipeline

This repository contains a automated CI/CD pipeline built with **Jenkins** to manage and execute SQL scripts against a database.

## Purpose

The primary goal of this pipeline is to provide a safe, automated way to execute database changes. It allows developers to:
1.  **Centralize SQL Scripts**: Fetch SQL files from any GitHub repository dynamically.
2.  **Safety First**: Include a manual approval step before any changes are applied to the database.
3.  **Environment Gates**: Use parameters to control deployment behavior (e.g., preventing accidental production runs).
4.  **Audit Trail**: Logs all executed SQL queries and connection results directly in Jenkins.

## Pipeline Structure

The `Jenkinsfile` defines several key stages:

1.  **Checkout**: Clones the current repository.
2.  **Build**: Performs preliminary checks and prints metadata.
3.  **Deploy**: Validates environment parameters.
4.  **Approval**: Pauses execution and waits for a human to confirm the deployment.
5.  **Check DB Connection & Execution**:
    *   Tests connectivity to the SQL Server.
    *   Parses a provided GitHub link to locate a specific SQL file.
    *   Performs a **Sparse Checkout** to download only the required SQL script.
    *   Executes the script using `sqlcmd`.
6.  **Clean Workspace**: Removes temporary files and repo clones.

## Parameters

| Parameter | Purpose |
| :--- | :--- |
| `DEPLOY_TO_PROD` | Boolean flag to verify intended deployment. |
| `GitLink` | The URL to the GitHub folder containing your SQL script. |
| `SQL_FILE_NAME` | The exact name of the `.sql` file to execute. |

## Prerequisites

*   **Jenkins Credentials**:
    *   `jenkins-sql-creds`: Username and password for the target SQL Server.
    *   `jenkins-github-creds`: Personal Access Token (PAT) for GitHub authentication.
*   **Infrastructure**: A Windows agent with `sqlcmd` and `git` installed.

## Documentation

A full technical breakdown of the `Jenkinsfile` logic can be found in the project's documentation folder.
