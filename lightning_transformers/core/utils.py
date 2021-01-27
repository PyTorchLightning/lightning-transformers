from inspect import signature, Parameter
import os
import shutil
import subprocess
import warnings

from pytorch_lightning.loggers import WandbLogger


def initialize_wandb_logger(*_, **kwargs):
    all_parameters = signature(WandbLogger).parameters
    keys = [param.name for param in all_parameters.values() if param.kind == Parameter.POSITIONAL_OR_KEYWORD]
    wandb_dict = {k: kwargs.get(k) for k in keys if k in kwargs}

    try:
        commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    except:
        commit_sha = "n/a"

    try:
        gitdiff = subprocess.check_output(["git", "diff"]).decode()
    except:
        gitdiff = ""

    wandb_dict["config"] = {}
    # wandb_dict["config"].update(kwargs["model_config"])
    # wandb_dict["config"].update(kwargs["dataset_config"])
    wandb_dict["config"].update(
        {
            "run_path": os.getcwd(),
            "commit": commit_sha,
            "notes": wandb_dict.get("notes"),
        }
    )

    wandbLogger = WandbLogger(**wandb_dict)

    shutil.copyfile(
        os.path.join(os.getcwd(), ".hydra/config.yaml"),
        os.path.join(os.getcwd(), ".hydra/hydra-config.yaml"),
    )
    wandbLogger.experiment.save(os.path.join(os.getcwd(), ".hydra/hydra-config.yaml"))
    wandbLogger.experiment.save(os.path.join(os.getcwd(), ".hydra/overrides.yaml"))

    with open("change.patch", "w") as f:
        f.write(gitdiff)
    wandbLogger.experiment.save(os.path.join(os.getcwd(), "change.patch"))

    return wandbLogger


def set_ignore_warnings():
    warnings.simplefilter("ignore")
    # set os environ variable for multiprocesses
    os.environ["PYTHONWARNINGS"] = "ignore"
