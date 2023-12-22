"""
CLI to run training on a model
"""
import logging, os
from pathlib import Path
import wandb
import fire
import transformers

from axolotl.cli import (
    check_accelerate_default_config,
    check_user_token,
    load_cfg,
    load_datasets,
    print_axolotl_text_art,
)
from axolotl.common.cli import TrainerCliArgs
from axolotl.train import train
from axolotl.utils.dict import DictDefault

LOG = logging.getLogger("axolotl.cli.train")


def do_cli(config: Path = Path("examples/"), **kwargs):
    # pylint: disable=duplicate-code
    parsed_cfg = load_cfg(config, **kwargs)
    print(f"*********Parsed Args********* \n{parsed_cfg}\n***************************")
    print_axolotl_text_art()
    check_accelerate_default_config()
    check_user_token()
    parser = transformers.HfArgumentParser((TrainerCliArgs))
    parsed_cli_args, _ = parser.parse_args_into_dataclasses(
        return_remaining_strings=True
    )
    dataset_meta = load_datasets(cfg=parsed_cfg, cli_args=parsed_cli_args)
    if int(os.environ["RANK"]) == 0:
        print(f"We are in rank {os.environ['RANK']}, initializing wandb")
        wandb.init(project=parsed_cfg.wandb_project, entity=parsed_cfg.wandb_entity, config=parsed_cfg)
        
        # enable wandb injection of config
        parsed_cfg = DictDefault(wandb.config)

    train(cfg=parsed_cfg, cli_args=parsed_cli_args, dataset_meta=dataset_meta)

    wandb.finish()


if __name__ == "__main__":
    fire.Fire(do_cli)