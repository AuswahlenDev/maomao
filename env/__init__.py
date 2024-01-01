from secretbox import SecretBox 

def get_env(dev: bool=True) -> SecretBox:
    """
    Parameters
    ------------------------
    `dev: bool` Load from `env/.env.dev`. By default it is True
    """
    secrets = SecretBox()
    secrets.use_loaders(
        secrets.EnvFileLoader("env/.env.dev" if dev else "env/.env.product")
    )
    return secrets 