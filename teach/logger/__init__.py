import os
from pathlib import Path
from .wandb_log import WandbLogger
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.loggers.base import DummyLogger
from hydra.utils import to_absolute_path
from omegaconf import DictConfig, OmegaConf
from .tools import cfg_to_flatten_config
import types
import wandb

def instantiate_logger(cfg: DictConfig):
    conf = OmegaConf.to_container(cfg.logger, resolve=True)
    name = conf.pop('logger_name')

    if name == 'wandb':
        project_save_dir = to_absolute_path(Path(cfg.path.working_dir) / conf['save_dir'])
        Path(project_save_dir).mkdir(exist_ok=True)
        conf['dir'] = project_save_dir
        conf['config'] = cfg_to_flatten_config(cfg)
        # maybe do this for connection error in cluster, could be redundant
        conf['settings'] = wandb.Settings(start_method="fork")
        # conf['mode']= 'online' if not cfg.logger.offline else 'offline'
        conf['notes']= cfg.logger.notes if cfg.logger.notes is not None else None
        conf['tags'] = cfg.logger.tags.strip().split(',')\
            if cfg.logger.tags is not None else None
        logger = WandbLogger(**conf)
        # begin / end already defined
        
    else:
        def begin(self, *args, **kwargs):
            return

        def end(self, *args, **kwargs):
            return

        if name == 'tensorboard':
            logger = TensorBoardLogger(**conf)
            logger.begin = begin
            logger.end = end
        elif name in ["none", None]:
            logger = DummyLogger()
            logger.begin = begin
            logger.end = end
        else:
            raise NotImplementedError("This logger is not recognized.")

    logger.lname = name
    return logger
