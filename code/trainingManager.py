
from azureml.core import Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core import ScriptRunConfig
from azureml.core.runconfig import DEFAULT_CPU_IMAGE

class TrainingManager(object):
    def __init__(self):
        pass

    def executeAction(self,experiment, project_folder,training_Script,cpu_cluster):
        #TODO: take environment as input from user for reusing it, may be useful when resubmitting the experiment.
        myenv = Environment("myenv")
        myenv.docker.enabled = True
        myenv.python.conda_dependencies = CondaDependencies.create(conda_packages=['scikit-learn'])
        src = ScriptRunConfig(source_directory=project_folder, script=training_Script)
        # Set compute target to the one created in previous step
        src.run_config.target = cpu_cluster.name

        # Set environment
        src.run_config.environment = myenv
        run = experiment.submit(config=src)

        # uncomment the lines below if you want to wait for training to complete. We can make this as user input later.
        # run.wait_for_completion(show_output=True);
        # run.get_metrics()