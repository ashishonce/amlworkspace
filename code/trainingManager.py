
from azureml.core import Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core import ScriptRunConfig
from azureml.core.runconfig import DEFAULT_CPU_IMAGE

class TrainingManager(object):
    def __init__(self):
        pass

    def executeAction(self,experiment, project_folder,training_Script,cpu_cluster):
        # project_folder = './train-on-amlcompute'
        # os.makedirs(project_folder, exist_ok=True)
        # shutil.copy('train.py', project_folder) 
        myenv = Environment("myenv")
        myenv.docker.enabled = True
        myenv.python.conda_dependencies = CondaDependencies.create(conda_packages=['scikit-learn'])
        src = ScriptRunConfig(source_directory=project_folder, script=training_Script)
        # Set compute target to the one created in previous step
        src.run_config.target = cpu_cluster.name

        # Set environment
        src.run_config.environment = myenv
        run = experiment.submit(config=src)
        run.wait_for_completion(show_output=True);
        run.get_metrics()