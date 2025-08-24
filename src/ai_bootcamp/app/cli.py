import hydra
from omegaconf import DictConfig


@hydra.main(config_path="../../../configs", config_name="train", version_base=None)
def main(cfg: DictConfig):
    print(f"Training with cfg: {cfg}")
    print(f"Model: {cfg.model}")
    print(f"Trainer: {cfg.trainer}")
    print(f"Data path: {cfg.data.path}")


if __name__ == "__main__":
    main()
