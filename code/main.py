import os
import json

from azureml.core import Workspace
from azureml.exceptions import WorkspaceException, AuthenticationException, ProjectSystemException
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.authentication import AzureCliAuthentication
from adal.adal_error import AdalError
from msrest.exceptions import AuthenticationError
from json import JSONDecodeError
from utils import required_parameters_provided, AMLConfigurationException
from workspaceManager import WorkspaceManager;
from computeManager import ComputeTargetManager;
from experimentManager import ExperimentManager;
from trainingManager import TrainingManager;
def main():
    # Loading input values
    print("::debug::Loading input values")
    compute_Target = None;
    parameters_file = os.environ.get("INPUT_PARAMETERSFILE", default="workspace.json")
    azure_credentials = os.environ.get("INPUT_AZURECREDENTIALS", default='{}')
    azureml_workSpaceName = os.environ.get("INPUT_WORKSPACENAME", default=None)
    azureml_createWSIfNotExist = os.environ.get("INPUT_CREATEWORKSPACE", default=False)
    
    wsManager = WorkspaceManager(parameters_file, azure_credentials, azureml_workSpaceName, azureml_createWSIfNotExist)
    ws = wsManager.executeAction(parameters_file, azure_credentials, azureml_workSpaceName, azureml_createWSIfNotExist);

    if ws != None:
        compute_parameters_file = os.environ.get("INPUT_PARAMETERS_FILE", default="compute.json")
        azure_computeTarget = os.environ.get("INPUT_COMPUTETARGET", default=None)
        computeMrg = ComputeTargetManager();
        compute_Target = computeMrg.executeAction(compute_parameters_file,ws,azure_credentials,azure_computeTarget);

    experiment_name = os.environ.get("INPUT_EXPERIMENTNAME", default=None)
    experiment = ExperimentManager().executeAction(ws,experiment_name)

    if compute_Target != None and experiment != None:
        TrainingManager().executeAction(experiment,"./train-on-amlcompute","train.py",compute_Target);
    else:
        print(" compute target or experiment note found")

if __name__ == "__main__":
    main()
