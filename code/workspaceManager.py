
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


class WorkspaceManager(object):
    def __init__(self,parameters_file = None, azure_credentials = None, azureml_workSpaceName=None, azureml_createWSIfNotExist =False):

        pass


    def executeAction(self,parameters_file,azure_credentials,azureml_workSpaceName,azureml_createWSIfNotExist):
        try:
            azure_credentials = json.loads(azure_credentials)
        except JSONDecodeError:
            print("::error::Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS. The JSON should include the following keys: 'tenantId', 'clientId', 'clientSecret' and 'subscriptionId'.")
            raise AMLConfigurationException(f"Incorrect or poorly formed output from azure credentials saved in AZURE_CREDENTIALS secret. See setup in https://github.com/Azure/aml-workspace/blob/master/README.md")
        
        # Checking provided parameters
        print("::debug::Checking provided parameters")
        required_parameters_provided(
            parameters=azure_credentials,
            keys=["tenantId", "clientId", "clientSecret", "subscriptionId"],
            message="Required parameter(s) not found in your azure credentials saved in AZURE_CREDENTIALS secret for logging in to the workspace. Please provide a value for the following key(s): "
        )

        # # Loading parameters file
        # print("::debug::Loading parameters file")
        print("::debug::Loading parameters file")
        parameters_file_path = os.path.join(".ml", ".azure", parameters_file)
        print(os.path.abspath(parameters_file_path))
        try:
            with open(parameters_file_path) as f:
                parameters = json.load(f)
        except FileNotFoundError:
            print(" workspace file is not found, parameters will be empty")
            parameters = {}

        # Checking provided parameters if it's user provided config
        if parameters != {}:
            print("::debug::Checking provided parameters")
            required_parameters_provided(
                parameters=parameters,
                keys=["name", "resource_group"],
                message="Required parameter(s) not found in your parameters file for loading a workspace. Please provide a value for the following key(s): "
            )
            azureml_workSpaceName = parameters["name"];
            # over rider , if in workflow it is false but configuration over rides it or other way round
            azureml_createWSIfNotExist = azureml_createWSIfNotExist or parameters.get("create_workspace", False);
        
        if (azureml_workSpaceName == None) or len(azureml_workSpaceName) == 0:
            raise AMLConfigurationException("WorkSpace Name must be provided")

        # Loading Workspace
        sp_auth = ServicePrincipalAuthentication(
            tenant_id=azure_credentials.get("tenantId", ""),
            service_principal_id=azure_credentials.get("clientId", ""),
            service_principal_password=azure_credentials.get("clientSecret", "")
        )
        try:
            print("::debug::Loading existing Workspace")
            ws = Workspace.get(
                name=azureml_workSpaceName,
                subscription_id=azure_credentials.get("subscriptionId", ""),
                auth=sp_auth
            )
            print("::debug::Successfully loaded existing Workspace")
            print(ws)
        except AuthenticationException as exception:
            print(f"::error::Could not retrieve user token. Please paste output of `az ad sp create-for-rbac --name <your-sp-name> --role contributor --scopes /subscriptions/<your-subscriptionId>/resourceGroups/<your-rg> --sdk-auth` as value of secret variable: AZURE_CREDENTIALS: {exception}")
            raise AuthenticationException
        except AuthenticationError as exception:
            print(f"::error::Microsoft REST Authentication Error: {exception}")
            raise AuthenticationException
        except AdalError as exception:
            print(f"::error::Active Directory Authentication Library Error: {exception}")
            raise AdalError
        except ProjectSystemException as exception:
            print(f"::error::Workspace authorizationfailed: {exception}")
            raise ProjectSystemException
        except WorkspaceException as exception:
            print(f"::debug::Loading existing Workspace failed: {exception}")
            if azureml_createWSIfNotExist:
                try:
                    print("::debug::Creating new Workspace")
                    ws = Workspace.create(
                        name=azureml_workSpaceName,
                        subscription_id=azure_credentials.get("subscriptionId", ""),
                        resource_group=parameters.get("resource_group", azureml_workSpaceName+"_rsgrp"),
                        location=parameters.get("location", "southcentralUS"),
                        create_resource_group=parameters.get("create_resource_group", True),
                        sku=parameters.get("sku", "basic"),
                        friendly_name=parameters.get("friendly_name", None),
                        storage_account=parameters.get("storage_account", None),
                        key_vault=parameters.get("key_vault", None),
                        app_insights=parameters.get("app_insights", None),
                        container_registry=parameters.get("container_registry", None),
                        cmk_keyvault=parameters.get("cmk_key_vault", None),
                        resource_cmk_uri=parameters.get("resource_cmk_uri", None),
                        hbi_workspace=parameters.get("hbi_workspace", None),
                        auth=sp_auth,
                        exist_ok=True,
                        show_output=True
                    )
                except WorkspaceException as exception:
                    print(f"::error::Creating new Workspace failed: {exception}")
                    raise AMLConfigurationException(f"Creating new Workspace failed with 'WorkspaceException': {exception}.")
            else:
                print(f"::error::Loading existing Workspace failed with 'WorkspaceException' and new Workspace will not be created because parameter 'createWorkspace' was not defined or set to false in your parameter file: {exception}")
                raise AMLConfigurationException("Loading existing Workspace failed with 'WorkspaceException' and new Workspace will not be created because parameter 'createWorkspace' was not defined or set to false in your parameter file.")

        # Write Workspace ARM properties to config file
        # print("::debug::Writing Workspace ARM properties to config file")
        # config_file_path = os.environ.get("GITHUB_WORKSPACE", default=".ml")
        # print(config_file_path)
        # config_file_name = "aml_arm_config.json"
        # ws.write_config(
        #     file_name=config_file_name
        # )
        
        return ws;



