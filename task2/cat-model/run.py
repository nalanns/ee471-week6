import logging
import os
os.environ["TORCH_HOME"] = "."

import torch
from cog import BaseRunner, Input, Path
from PIL import Image
from torchvision import models

WEIGHTS = models.ResNet50_Weights.IMAGENET1K_V1


class Runner(BaseRunner):
    def setup(self):
        """Load the model into memory to make running multiple inferences efficient"""
        self.log = logging.getLogger("cat-model")
        self.log.setLevel(logging.INFO)
        handler = logging.FileHandler("/tmp/predictions.log")
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        self.log.addHandler(handler)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.resnet50(weights=WEIGHTS).to(self.device)
        self.model.eval()
        self.log.info("model loaded on %s", self.device)

    def run(self, image: Path = Input(description="Image to classify")) -> dict:
        """Run the model"""
        img = Image.open(image).convert("RGB")
        preds = self.model(WEIGHTS.transforms()(img).unsqueeze(0).to(self.device))
        top3 = preds[0].softmax(0).topk(3)
        categories = WEIGHTS.meta["categories"]
        result = {categories[i]: p.detach().item() for p, i in zip(*top3)}
        self.log.info("image=%s size=%s prediction=%s", image.name, img.size, result)
        return result