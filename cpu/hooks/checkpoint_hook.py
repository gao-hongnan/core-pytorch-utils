import os
from typing import Any, Dict, List, Optional

from ..checkpoint import Checkpointer
from .hookbase import HookBase


class CheckpointerHook(HookBase):
    """Save checkpoints periodically.

    Save checkpoint, if current epoch is a multiple of period or ``max_epochs`` is reached.
    """

    def __init__(
        self, checkpointer: Checkpointer, period: int, max_to_keep: Optional[int] = None
    ) -> None:
        """
        Args:
            checkpointer: The checkpointer object used to save checkpoints.
            period (int): The period to save checkpoint.
            max_to_keep (int): Maximum number of most current checkpoints to keep,
                previous checkpoints will be deleted.
        """
        self._checkpointer = checkpointer
        self._period = period
        if max_to_keep is not None:
            assert max_to_keep > 0
        self._max_to_keep = max_to_keep

        self._recent_checkpoints: List[str] = []

    def after_epoch(self) -> None:
        if self.every_n_epochs(self._period) or self.is_last_epoch():
            epoch = self.trainer.epoch  # ranged in [0, max_epochs - 1]
            checkpoint_name = f"epoch_{epoch}.pth"
            self._checkpointer.save(checkpoint_name, epoch=epoch)

            if self._max_to_keep is not None:
                self._recent_checkpoints.append(checkpoint_name)
                if len(self._recent_checkpoints) > self._max_to_keep:
                    # delete the oldest checkpointer
                    file_name = self._recent_checkpoints.pop(0)
                    file_path = self._checkpointer.get_path(file_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)

    def state_dict(self) -> Dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if key != "checkpointer"}