import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from pathlib import Path

# Project structure & Global variables
# ------------------------------------
APP_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = APP_DIR.parent.absolute()

# Create logs directory if it doesn't exist
LOGS_DIR = PROJECT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Data paths
DATA_DIR = PROJECT_DIR / "data"
ORIGINAL_DATASET = DATA_DIR / "original"
# Training & Evaluation data dirs
TRAINING_DIR = ORIGINAL_DATASET / "training"
EVALUATION_DIR = ORIGINAL_DATASET / "evaluation"

# Predicted data dir
PREDICTED_DIR = DATA_DIR / "predicted"
PREDICTED_DIR.mkdir(exist_ok=True)

# Simple utility functions
# ------------------------------------

# Color maps for symbols according to arc-agi css
COLORS = {
    0: "#000000",  # black
    1: "#0074D9",  # blue
    2: "#FF4136",  # red
    3: "#2ECC40",  # green
    4: "#FFDC00",  # yellow
    5: "#AAAAAA",  # grey
    6: "#F012BE",  # fuchsia
    7: "#FF851B",  # orange
    8: "#7FDBFF",  # teal
    9: "#870C25"   # brown
}

# Create a sample object to house the actual training sample along with additional meta information
class Sample:
    def __init__(self, fpath: str):
        self.fpath = Path(fpath)
        self.id = self.fpath.stem
        self.url = f"https://arcprize.org/play?task={self.id}"
        # Load the raw json as dict & its components
        self.data = json.load(fpath.open())
        self.train = self.data['train']
        self.test = self.data['test']
        # Assumed to only have one input & output
        self.test_inp = self.test[0]['input']
        self.test_out = self.test[0]['output']
        self._predicted = None
        self.match = None

        # Meta information
        self.ntrain = len(self.data['train'])
        self.inp_rows = [len(example['input'][0]) for example in self.data['train']]
        self.inp_cols = [len(example['input']) for example in self.data['train']]
        self.out_rows = [len(example['output'][0]) for example in self.data['train']]
        self.out_cols = [len(example['output']) for example in self.data['train']]


    @property
    def predicted(self):
        return self._predicted

    @predicted.setter
    def predicted(self, value):
        self._predicted = value
        self.on_predicted_change()

    def on_predicted_change(self):
        self.match = self._predicted == self.test_out


    def _render_grid(self, grid: list[list[int]], img_width: int = 200, border_size: int = 1):
        # Convert grid to a NumPy array
        grid_array = np.array(grid, dtype=int)
        nrow, ncol = grid_array.shape

        # Determine scale for each cell
        scale = max(1, img_width // max(1, ncol))

        # Convert color codes from hex to RGB
        color_rgb = np.array([
            tuple(int(COLORS[i][k:k+2], 16) for k in (1, 3, 5))
            for i in range(10)
        ], dtype=np.uint8)

        # Create the RGBA version of the grid
        alpha = np.full((nrow, ncol, 1), 255, dtype=np.uint8)
        colored_grid = np.concatenate([color_rgb[grid_array], alpha], axis=-1)

        # Scale up the grid
        scaled_grid = np.kron(colored_grid, np.ones((scale, scale, 1), np.uint8))

        # Prepare final canvas
        final_height = nrow*scale + (nrow-1)*border_size
        final_width = ncol*scale + (ncol-1)*border_size
        canvas = np.full((final_height, final_width, 4), (80, 80, 80, 255), dtype=np.uint8)

        # Vectorized placement of scaled cells with borders
        row_idx = np.arange(nrow*scale)
        col_idx = np.arange(ncol*scale)
        row_idx += (row_idx // scale) * border_size
        col_idx += (col_idx // scale) * border_size
        canvas[row_idx[:, None], col_idx[None, :]] = scaled_grid

        return Image.fromarray(canvas, 'RGBA')

    def _render_sample(self, sample, img_width: int = 200):

        inp_img = self._render_grid(sample["input"], img_width).convert("RGBA")
        out_img = self._render_grid(sample["output"], img_width).convert("RGBA")

        images = [inp_img, out_img]

        border_width = 30
        total_width = sum(img.width for img in images) + border_width * (len(images) - 1)
        max_height = max(img.height for img in images)

        composite = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))
        x_offset = 0
        for img in images:
            composite.paste(img, (x_offset, 0), img)
            x_offset += img.width + border_width

        return composite

    def render_train(self, img_width: int = 200):
        train_images = [self._render_sample(sample, img_width) for sample in self.train]

        border_height = 30
        total_height = sum(img.height for img in train_images) + border_height * (len(train_images) - 1)
        max_width = max(img.width for img in train_images)

        composite = Image.new('RGBA', (max_width, total_height), (0, 0, 0, 0))
        y_offset = 0

        for img in train_images:
            composite.paste(img, (0, y_offset), img)
            y_offset += img.height + border_height

        return composite

    def render_test(self, img_width: int = 200):
        test_inp_img = self._render_grid(self.test_inp, img_width).convert("RGBA")
        test_out_img = self._render_grid(self.test_out, img_width).convert("RGBA")

        images = [test_out_img]

        if self._predicted is not None:
            predicted_img = self._render_grid(self._predicted, img_width).convert("RGBA")
        else:
            # Create a blank image
            predicted_img = Image.new('RGBA', (img_width, img_width), (0, 0, 0, 255))

        images.append(predicted_img)

        border_width = 30
        total_width = sum(img.width for img in images) + border_width * (len(images) - 1)
        max_height = test_inp_img.height + max(img.height for img in images) + border_width

        composite = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))

        # Paste the test input image on top in the middle
        x_offset = (total_width - test_inp_img.width) // 2
        composite.paste(test_inp_img, (x_offset, 0), test_inp_img)

        # Paste the output and predicted images side by side on the bottom row
        y_offset = test_inp_img.height + border_width
        x_offset = 0
        for img in images:
            composite.paste(img, (x_offset, y_offset), img)
            x_offset += img.width + border_width

        return composite



# Class to create an solution object for a particular solution run
# The run will mainly be deduped by timestamp and will have additional metadata
# identifying method, model, and other relevant information
class Solution:
    def __init__(self, author: str = "migos", desc: str = "skrrrt", tags: list[str] = list(["brrrr"])):
        self.tags = tags
        self.desc = desc
        self.author = author
        self.init_at = datetime.now(timezone.utc)
        self.answers = None
        # NOTE: For now, the entire set is loaded into memory but with the use of more synthetic sets,
        # the method will be changed to a generator that can be iterated over
        self.train_samples = [Sample(fpath) for fpath in TRAINING_DIR.rglob("*.json")]
        self.test_samples = [Sample(fpath) for fpath in EVALUATION_DIR.rglob("*.json")]

    def __str__(self):
        return f"{self.author}-{"_".join(self.tags)}-{self.init_at.replace(microsecond=0).isoformat()}"

    def __repr__(self):
        return f"{self.author}-{"_".join(self.tags)}-{self.init_at.replace(microsecond=0).isoformat()}"

    # Method to update object creation time to current time
    def reset_init_time(self):
        self.init_at = datetime.now(timezone.utc)

    def total_correct(self):
        return sum([int(sample.match)for sample in self.test_samples])

    def commit(self):
        # Save the solution to a file in the same format as the original dataset
        fname = self.__repr__()
        fpath = PREDICTED_DIR / f"{fname}.json"

        answers = {}
        # Combine all solutions into a single file
        # TODO: Right now this allows only one solution - modify it to take more than 1
        for sample in self.test_samples:
            answers[sample.id] = [{"attempt_1": sample.predicted}]

        with fpath.open("w") as f:
            json.dump(answers, f)


    # Iterator to yield training samples one-by-one
    # NOTE: This is currently not used and will be when the training set is augmented
    def get_train(self):
        for fpath in TRAINING_DIR.rglob("*.json"):
            # Load the json
            yield Sample(fpath)
