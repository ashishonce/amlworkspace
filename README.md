# amlworkspace

An action to connect to your AML workspace or to create a new one. 



|Input | Required | Default | Description|
|--|--|--| --|
|azureCredentials| yes | {} | your Service Principle credentials for accessing or creating workspace, if you don't have any exisitng workspace, you must have a workspace.json file in .ml.azure folder in the repository
|workspaceName| yes | None | name of the workspace if workspace already exists, else a new name
| createWorkSpace |  yes | false | if this input is set then only new workspace will be created
| computeTarget |  yes | None | compute target to use for training, if you don't have any target, you must have a compute.json file in .ml.azure folder in the repository
| experimentName |  yes | None | experiment name to use for training, if you don't have any existing experiment registerd with AML, this will create a new one
