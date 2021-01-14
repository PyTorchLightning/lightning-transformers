from dataclasses import dataclass
from typing import Optional, Dict, Union

import dacite
import torch
from hydra.utils import get_class, instantiate
from omegaconf import DictConfig, OmegaConf
from pytorch_lightning import Trainer
from transformers import AutoTokenizer, PreTrainedTokenizerBase

from lightning_transformers.core.config import OptimizerConfig, SchedulerConfig, TrainerConfig
from lightning_transformers.core.huggingface import HFTransformerDataModule
from lightning_transformers.core.huggingface.config import (
    HFBackboneConfig,
    HFTaskConfig,
    HFTokenizerConfig,
    HFTransformerDataConfig,
)


class Instantiator:
    def __getattr__(self, _):
        raise NotImplementedError


class HydraInstantiator(Instantiator):
    def __init__(self):
        self.state = {}

    def model(self, cfg: HFTaskConfig):  # -> HFTransformer:
        return instantiate(cfg)

    def optimizer(self, model: torch.nn.Module, cfg: OptimizerConfig) -> torch.optim.Optimizer:
        no_decay = ["bias", "LayerNorm.weight"]
        grouped_parameters = [
            {
                "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": cfg.weight_decay,
            },
            {
                "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        return instantiate(cfg, grouped_parameters)

    def scheduler(
        self, cfg: SchedulerConfig, optimizer: torch.optim.Optimizer
    ) -> torch.optim.lr_scheduler._LRScheduler:
        return instantiate(cfg, optimizer=optimizer)

    def data_module(
        self, cfg: HFTransformerDataConfig, tokenizer: Optional[PreTrainedTokenizerBase] = None
    ) -> HFTransformerDataModule:
        return instantiate(cfg, tokenizer=tokenizer)

    # todo: These are HF specific instantiation not Hydra
    # todo: most of this code should live in a base class outside core/huggingface/
    def backbone(self, downstream_model_type: str, backbone_cfg: HFBackboneConfig) -> torch.nn.Module:
        return get_class(downstream_model_type).from_pretrained(
            backbone_cfg.pretrained_model_name_or_path, **self._state["backbone"]
        )

    def tokenizer(self, cfg: HFTokenizerConfig) -> PreTrainedTokenizerBase:
        return AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=cfg.pretrained_model_name_or_path, use_fast=cfg.use_fast
        )

    def trainer(self, cfg: TrainerConfig) -> Trainer:
        return instantiate(cfg)

    def dictconfig_to_dataclass(self, cfg: DictConfig) -> Union[DictConfig, dataclass]:
        # resolve interpolations
        cfg = OmegaConf.create(OmegaConf.to_container(cfg, resolve=True))
        converted = self._recursive_convert(cfg)
        return converted

    def _recursive_convert(self, cfg: DictConfig) -> Union[DictConfig, dataclass]:
        target = cfg.pop("_target_config_", None)
        for k, v in cfg.items():
            if isinstance(v, DictConfig):
                cfg[k] = self._recursive_convert(v)
        if target:
            cls = get_class(target)
            return dacite.from_dict(data_class=cls(), data=OmegaConf.to_container(cfg))
        return cfg

