from collections import defaultdict
import logging
import numpy as np

class Logger:
    def __init__(self, console_logger):
        self.console_logger = console_logger

        self.use_tb = False
        self.use_wandb = False

        self.stats = defaultdict(lambda: [])

    def setup_tb(self, directory_name):
        # Import here so it doesn't have to be installed if you don't use it
        from tensorboard_logger import configure, log_value
        configure(directory_name)
        self.tb_logger = log_value
        self.use_tb = True

    def setup_wandb(self):
        import wandb
        self.wb_logger = wandb.log
        self.use_wandb = True

    def log_stat(self, key, value, t):
        self.stats[key].append((t, value))

        if self.use_tb:
            self.tb_logger(key, value, t)

        if self.use_wandb:
            self.wb_logger({key: value}, step=t)

    def print_recent_stats(self):
        log_str = "Recent Stats | t_env: {:>10} | Episode: {:>8}\n".format(*self.stats["episode"][-1])
        i = 0
        for (k, v) in sorted(self.stats.items()):
            if k == "episode":
                continue
            i += 1
            window = 5 if k != "epsilon" else 1
            if k == "train_metrics/q_grad_norm":
                item = "{:.4f}".format(np.mean([x[1].cpu().numpy() for x in self.stats[k][-window:]]))
            else:
                item = "{:.4f}".format(np.mean([x[1] for x in self.stats[k][-window:]]))
            log_str += "{:<25}{:>8}".format(k + ":", item)
            log_str += "\n" if i % 4 == 0 else "\t"
        self.console_logger.info(log_str)

    def print_stats_summary(self):
        log_str = "Summary Stats"
        i = 0
        for (k, v) in sorted(self.stats.items()):
            if k == "episode":
                continue
            i += 1
            mean_value = np.mean([x[1] for x in self.stats[k]], axis=0)
            if len(mean_value.shape) == 0:
                item = "{:.4f}".format(mean_value)
            else:
                item = mean_value.__repr__()
            log_str += "{:<25}{:>8}".format(k + ":", item)
            log_str += "\n" if i % 4 == 0 else "\t"
        self.console_logger.info(log_str)

# set up a custom logger
def get_logger():
    logger = logging.getLogger()
    logger.handlers = []
    ch = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s %(asctime)s] %(name)s %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel('DEBUG')

    return logger

