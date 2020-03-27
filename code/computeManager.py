import os
import json

from azureml.core import Workspace
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException, AuthenticationException, ProjectSystemException
from azureml.core.authentication import ServicePrincipalAuthentication
from adal.adal_error import AdalError
from msrest.exceptions import AuthenticationError
from json import JSONDecodeError
from utils import AMLConfigurationException, required_parameters_provided, create_aml_cluster, create_aks_cluster


class ComputeTargetManager(object):
    def __init__(self):
        pass
    
    def executeAction(self, parameters_file =None, ws = None, azure_credentials = None , azure_computeTarget = None):
        try:
            azure_credentials = json.loads(azure_credentials)
        except JSONDecodeError:
            print("::error::Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS")
            raise AMLConfigurationException(f"Incorrect or poorly formed output from azure credentials saved in AZURE_CREDENTIALS secret. See setup in https://github.com/Azure/aml-compute/blob/master/README.md")

        # Checking provided parameters
        print("::debug::Checking provided parameters")
        required_parameters_provided(
            parameters=azure_credentials,
            keys=["tenantId", "clientId", "clientSecret"],
            message="Required parameter(s) not found in your azure credentials saved in AZURE_CREDENTIALS secret for logging in to the workspace. Please provide a value for the following key(s): "
        )

        # Loading parameters file
        print("::debug::Loading parameters file")
        parameters_file_path = os.path.join(".ml", ".azure", parameters_file)
        try:
            with open(parameters_file_path) as f:
                parameters = json.load(f)
        except FileNotFoundError:
            print(f"::error::Could not find parameter file in {parameters_file_path}. Please provide a parameter file in your repository (e.g. .ml/.azure/compute.json).")
            parameters = {}

        # Loading compute target
        try:
            # Checking provided parameters
            print("Checking provided parameters")
            if parameters == {}:
                if azure_computeTarget == None:
                    print(" compute not available")
            else:
                required_parameters_provided(
                    parameters=parameters,
                    keys=["name"],
                    message="Required parameter(s) not found in your parameters file for loading a compute target. Please provide a value for the following key(s): "
                )
                azure_computeTarget = parameters["name"]

            print("Loading existing compute target")
            print(ws)
            print(azure_computeTarget)
            compute_target = ComputeTarget(
                workspace=ws,
                name=azure_computeTarget
            )
            print(f"::debug::Found compute target with same name. Not updating the compute target: {compute_target.serialize()}")
        except ComputeTargetException:
            print("::debug::Could not find existing compute target with provided name")

            # Checking provided parameters
            print("::debug::Checking provided parameters")
            required_parameters_provided(
                parameters=parameters,
                keys=["name", "compute_type"],
                message="Required parameter(s) not found in your parameters file for loading a compute target. Please provide a value for the following key(s): "
            )

            print("::debug::Creating new compute target")
            compute_type = parameters.get("compute_type", "")
            if compute_type == "amlcluster":
                compute_target = create_aml_cluster(
                    workspace=ws,
                    parameters=parameters
                )
                print(f"::debug::Successfully created AML cluster: {compute_target.serialize()}")
            if compute_type == "akscluster":
                compute_target = create_aks_cluster(
                    workspace=ws,
                    parameters=parameters
                )
                print(f"::debug::Successfully created AKS cluster: {compute_target.serialize()}")
            else:
                print(f"::error::Compute type '{compute_type}' is not supported")
                raise AMLConfigurationException(f"Compute type '{compute_type}' is not supported.")
        print("::debug::Successfully finished Azure Machine Learning Compute Action")
        return compute_target;
