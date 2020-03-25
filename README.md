# amlworkspace

An action to connect to your AML workspace or to create a new one. 



|Input | Required | Default | Description|
|--|--|--| --|
|azureCredentials| yes | {} | your Service Principle credentials for accessing or creating workspace, if you already have azure login , as your previous step, no need to provide this, and action will fall back to try cliAuthentication
|workspaceName| yes | None | name of the workspace if workspace already exists, else a new name
| createNew |  yes | false | if this input is set then only new workspace will be created
inputs 